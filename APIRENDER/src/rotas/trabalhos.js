// Execução dos trabalhos (colaborador / administrador), notas e notificações
const express = require('express');
const { consulta, transacao } = require('../bd');
const {
  exigeLogin, exigeFuncionalidade, exigeColaborador, assincrono,
} = require('../autenticacao');

const router = express.Router();

const idDe = (valor) => (Number.isInteger(Number(valor)) && Number(valor) > 0 ? Number(valor) : null);

// Assumir uma etapa de um trabalho (qualquer etapa, por qualquer ordem)
router.post('/trabalhos/:id/assumir', exigeLogin, exigeColaborador,
  exigeFuncionalidade('Assumir trabalho'), assincrono(async (req, res) => {
    const idEtapa = idDe(req.body.id_etapa);
    if (!idEtapa) return res.status(400).json({ erro: 'Indique o id_etapa.' });

    const resultado = await transacao(req.utilizador.id_utilizador, async (bd) => {
      const { rows } = await bd.query('CALL sp_assumir_etapa($1, $2, $3, NULL)',
        [idDe(req.params.id), idEtapa, req.utilizador.id_colaborador]);
      return { id_execucao: rows[0].p_id_execucao };
    });
    res.status(201).json(resultado);
  }));

// Concluir a etapa em curso.
//   Encaminhar: id_colaborador_seguinte (+ id_etapa_seguinte opcional)
//   Deixar disponível: sem id_colaborador_seguinte
router.post('/execucoes/:id/concluir', exigeLogin, exigeColaborador,
  exigeFuncionalidade('Executar trabalho'), assincrono(async (req, res) => {
    const corpo = req.body || {};
    await transacao(req.utilizador.id_utilizador, (bd) => bd.query(
      'CALL sp_concluir_etapa($1, $2, $3, $4, $5)',
      [idDe(req.params.id), req.utilizador.id_colaborador,
        idDe(corpo.id_colaborador_seguinte), corpo.observacoes || null,
        idDe(corpo.id_etapa_seguinte)],
    ));
    res.json({ ok: true });
  }));

// Mudar o estado: "Em espera" (justificação obrigatória),
// "Em processamento" (retomar) ou "Concluído" (a qualquer momento)
router.post('/trabalhos/:id/estado', exigeLogin, exigeColaborador,
  exigeFuncionalidade('Alterar situação do trabalho'), assincrono(async (req, res) => {
    const { estado, justificacao } = req.body || {};
    await transacao(req.utilizador.id_utilizador, (bd) => bd.query(
      'CALL sp_alterar_estado_trabalho($1, $2, $3, $4)',
      [idDe(req.params.id), estado, req.utilizador.id_utilizador, justificacao || null],
    ));
    res.json({ ok: true });
  }));

// Nova nota num trabalho.
//   Colaborador: visibilidade "interna" (por omissão) ou "cliente"
//   Cliente: só nos seus trabalhos, e a nota é sempre visível para ele
router.post('/trabalhos/:id/notas', exigeLogin, assincrono(async (req, res) => {
  const u = req.utilizador;
  const idTrabalho = idDe(req.params.id);
  const conteudo = String((req.body && req.body.conteudo) || '').trim();
  if (!conteudo) return res.status(400).json({ erro: 'A nota não pode estar vazia.' });

  let visibilidade;
  if (u.perfil === 'cliente') {
    const { rows } = await consulta(
      `SELECT 1 FROM encomenda_tipo_trabalho ett
       JOIN encomenda e ON e.id_encomenda = ett.id_encomenda
       WHERE ett.id_encomenda_tipo = $1 AND e.id_cliente = $2`,
      [idTrabalho, u.id_cliente],
    );
    if (rows.length === 0) return res.status(404).json({ erro: 'Trabalho não encontrado.' });
    visibilidade = 'cliente';
  } else {
    const { rows } = await consulta("SELECT fn_tem_funcionalidade($1, 'Notas', 'Mobile') AS pode",
      [u.id_utilizador]);
    if (!rows[0].pode) return res.status(403).json({ erro: 'Sem permissão: Notas.' });
    visibilidade = req.body.visibilidade === 'cliente' ? 'cliente' : 'interna';
  }

  const nota = await transacao(u.id_utilizador, async (bd) => {
    const { rows } = await bd.query(
      `INSERT INTO nota (id_encomenda_tipo, id_utilizador, conteudo, visibilidade)
       VALUES ($1, $2, $3, $4)
       RETURNING id_nota, id_encomenda_tipo, conteudo, visibilidade, data_criacao`,
      [idTrabalho, u.id_utilizador, conteudo, visibilidade],
    );
    return rows[0];
  });
  res.status(201).json(nota);
}));

// Marcar notificações como lidas (todas, ou só os ids indicados)
router.post('/notificacoes/lidas', exigeLogin, assincrono(async (req, res) => {
  const ids = Array.isArray(req.body && req.body.ids) ? req.body.ids.map(Number) : null;
  const { rowCount } = await consulta(
    `UPDATE notificacao SET lida = TRUE
     WHERE id_utilizador = $1 AND NOT lida
       AND ($2::INT[] IS NULL OR id_notificacao = ANY($2::INT[]))`,
    [req.utilizador.id_utilizador, ids],
  );
  res.json({ marcadas: rowCount });
}));

module.exports = router;
