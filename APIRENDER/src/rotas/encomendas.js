// POST /encomendas/ — criar uma encomenda (cliente; administrador em nome de um cliente)
const express = require('express');
const { transacao } = require('../bd');
const { exigeLogin, exigeFuncionalidade, assincrono } = require('../autenticacao');

const router = express.Router();

const NATUREZAS = ['Físico', 'Digital'];

router.post('/encomendas/', exigeLogin, exigeFuncionalidade('Criar Encomenda'), assincrono(async (req, res) => {
  const u = req.utilizador;
  const corpo = req.body || {};
  const trabalhos = Array.isArray(corpo.trabalhos) ? corpo.trabalhos : [];

  // O cliente cria sempre para si; o administrador indica o cliente
  const idCliente = u.perfil === 'cliente' ? u.id_cliente : Number(corpo.id_cliente);
  if (!idCliente) {
    return res.status(400).json({ erro: 'Indique o id_cliente da encomenda.' });
  }
  if (trabalhos.length === 0) {
    return res.status(400).json({ erro: 'A encomenda tem de ter pelo menos um trabalho.' });
  }
  for (const t of trabalhos) {
    if (!Number.isInteger(t.id_tipo_trabalho)) {
      return res.status(400).json({ erro: 'Cada trabalho precisa de id_tipo_trabalho (número).' });
    }
    if (t.natureza && !NATUREZAS.includes(t.natureza)) {
      return res.status(400).json({ erro: 'natureza tem de ser "Físico" ou "Digital".' });
    }
  }

  const resultado = await transacao(u.id_utilizador, async (bd) => {
    // Paciente (o mobile envia a idade; a BD guarda a data de nascimento)
    let idPaciente = null;
    const p = corpo.paciente;
    if (p && p.nome) {
      const { rows } = await bd.query(
        `INSERT INTO paciente (nome, data_nascimento, sexo)
         VALUES ($1,
                 COALESCE($2::DATE, (CURRENT_DATE - make_interval(years => $3::INT))::DATE),
                 $4)
         RETURNING id_paciente`,
        [p.nome, p.data_nascimento || null, Number.isInteger(p.idade) ? p.idade : null, p.sexo || null],
      );
      idPaciente = rows[0].id_paciente;
    }

    // Médico: identificado só pela cédula profissional
    let idMedico = null;
    if (corpo.cedula_medico) {
      const { rows } = await bd.query(
        `INSERT INTO medico (cedula_profissional) VALUES ($1)
         ON CONFLICT (cedula_profissional) DO UPDATE SET cedula_profissional = EXCLUDED.cedula_profissional
         RETURNING id_medico`,
        [String(corpo.cedula_medico).trim()],
      );
      idMedico = rows[0].id_medico;
    }

    // Encomenda + um trabalho por tipo (procedimento da BD)
    const { rows: criada } = await bd.query(
      'CALL sp_criar_encomenda($1, $2, $3::INT[], $4, $5, $6, NULL)',
      [idCliente, u.id_utilizador, trabalhos.map((t) => t.id_tipo_trabalho),
        idMedico, idPaciente, corpo.observacoes || null],
    );
    const idEncomenda = criada[0].p_id_encomenda;

    // Detalhes de cada trabalho e dentes do odontograma
    const { rows: itens } = await bd.query(
      `SELECT id_encomenda_tipo FROM encomenda_tipo_trabalho
       WHERE id_encomenda = $1 ORDER BY id_encomenda_tipo`,
      [idEncomenda],
    );
    for (let i = 0; i < itens.length; i += 1) {
      const t = trabalhos[i];
      const id = itens[i].id_encomenda_tipo;
      await bd.query(
        `UPDATE encomenda_tipo_trabalho
         SET natureza = $2, cor = $3, material_a_enviar = $4,
             data_prevista_consulta = $5, notas = $6
         WHERE id_encomenda_tipo = $1`,
        [id, t.natureza || null, t.cor || null, t.material_a_enviar || null,
          t.data_prevista_consulta || null, t.notas || null],
      );
      for (const dente of Array.isArray(t.dentes) ? t.dentes : []) {
        await bd.query(
          `INSERT INTO odontograma (id_encomenda_tipo, numero_dente) VALUES ($1, $2)
           ON CONFLICT DO NOTHING`,
          [id, dente],
        );
      }
    }

    const { rows } = await bd.query('SELECT codigo FROM encomenda WHERE id_encomenda = $1', [idEncomenda]);
    return {
      id_encomenda: idEncomenda,
      codigo: rows[0].codigo,
      trabalhos: itens.map((x) => x.id_encomenda_tipo),
    };
  });

  res.status(201).json(resultado);
}));

module.exports = router;
