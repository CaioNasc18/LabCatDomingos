// GET /sync/ — todos os dados a que o utilizador autenticado tem acesso,
// uma secção por tabela local da app (estratégia da Aula 9).
//
// Cliente: só o que é seu; estados simplificados (fn_estado_cliente);
//          sem etapas, sem execuções, sem notas e ficheiros internos.
// Colaborador / administrador: tudo.
const express = require('express');
const { consulta } = require('../bd');
const { exigeLogin, assincrono } = require('../autenticacao');

const router = express.Router();

async function linhas(sql, valores) {
  const { rows } = await consulta(sql, valores);
  return rows;
}

async function syncCliente(u) {
  const id = [u.id_cliente];
  const meu = [u.id_cliente, u.id_utilizador];

  return {
    clientes: await linhas(
      `SELECT id_cliente, nome, nif, morada, tipo_entidade FROM cliente WHERE id_cliente = $1`, id),

    encomendas: await linhas(
      `SELECT e.id_encomenda, e.codigo, e.id_cliente, e.id_medico, e.id_paciente,
              fn_estado_cliente(est.nome) AS estado,
              e.data_criacao, e.data_limite, e.observacoes
       FROM   encomenda e
       JOIN   estado_encomenda est ON est.id_estado = e.id_estado
       WHERE  e.id_cliente = $1
       ORDER  BY e.data_criacao DESC`, id),

    trabalhos: await linhas(
      `SELECT ett.id_encomenda_tipo, ett.id_encomenda, e.codigo, ett.id_tipo_trabalho,
              tt.nome AS tipo_trabalho, fn_estado_cliente(est.nome) AS estado,
              ett.natureza, ett.cor, ett.material_a_enviar, ett.data_prevista_consulta,
              ett.notas, e.id_paciente, e.data_limite
       FROM   encomenda_tipo_trabalho ett
       JOIN   encomenda e               ON e.id_encomenda = ett.id_encomenda
       JOIN   tipo_trabalho tt          ON tt.id_tipo_trabalho = ett.id_tipo_trabalho
       JOIN   estado_encomenda_tipo est ON est.id_estado = ett.id_estado
       WHERE  e.id_cliente = $1
       ORDER  BY ett.id_encomenda_tipo`, id),

    pacientes: await linhas(
      `SELECT DISTINCT pa.id_paciente, pa.nome, fn_idade(pa.data_nascimento) AS idade, pa.sexo
       FROM   paciente pa JOIN encomenda e ON e.id_paciente = pa.id_paciente
       WHERE  e.id_cliente = $1`, id),

    medicos: await linhas(
      `SELECT DISTINCT m.id_medico, m.cedula_profissional
       FROM   medico m JOIN encomenda e ON e.id_medico = m.id_medico
       WHERE  e.id_cliente = $1`, id),

    trabalho_dentes: await linhas(
      `SELECT o.id_encomenda_tipo, o.numero_dente
       FROM   odontograma o
       JOIN   encomenda_tipo_trabalho ett ON ett.id_encomenda_tipo = o.id_encomenda_tipo
       JOIN   encomenda e ON e.id_encomenda = ett.id_encomenda
       WHERE  e.id_cliente = $1
       ORDER  BY o.id_encomenda_tipo, o.numero_dente`, id),

    tipos_trabalho: await linhas(
      `SELECT id_tipo_trabalho, nome FROM tipo_trabalho WHERE ativo ORDER BY nome`),

    etapas: [],
    execucoes: [],
    colaboradores: [],
    trabalhos_disponiveis: [],
    trabalhos_atribuidos: [],

    notas: await linhas(
      `SELECT n.id_nota, n.id_encomenda_tipo, n.conteudo, n.data_criacao,
              n.id_utilizador, u.nome AS autor
       FROM   nota n
       JOIN   utilizador u ON u.id_utilizador = n.id_utilizador
       JOIN   encomenda_tipo_trabalho ett ON ett.id_encomenda_tipo = n.id_encomenda_tipo
       JOIN   encomenda e ON e.id_encomenda = ett.id_encomenda
       WHERE  e.id_cliente = $1
         AND  (n.visibilidade = 'cliente' OR n.id_utilizador = $2)
       ORDER  BY n.data_criacao`, meu),

    ficheiros: await linhas(
      `SELECT f.origem, f.id, f.id_encomenda_tipo, f.tipo_ficheiro, f.ficheiro_path,
              f.data_upload, f.tamanho_ficheiro
       FROM (
         SELECT 'ficheiro' AS origem, id_ficheiro AS id, id_encomenda_tipo, tipo_ficheiro,
                ficheiro_path, visibilidade, data_upload, tamanho_ficheiro, id_utilizador
         FROM   ficheiro
         UNION ALL
         SELECT 'fotografia', id_fotografia, id_encomenda_tipo, 'foto',
                ficheiro_path, visibilidade, data_upload, tamanho_ficheiro, id_utilizador
         FROM   fotografia
       ) f
       JOIN   encomenda_tipo_trabalho ett ON ett.id_encomenda_tipo = f.id_encomenda_tipo
       JOIN   encomenda e ON e.id_encomenda = ett.id_encomenda
       WHERE  e.id_cliente = $1
         AND  (f.visibilidade = 'cliente' OR f.id_utilizador = $2)
       ORDER  BY f.data_upload`, meu),

    notificacoes: await notificacoes(u),
  };
}

async function syncColaborador(u) {
  return {
    clientes: await linhas(
      `SELECT id_cliente, nome, nif, morada, tipo_entidade FROM cliente WHERE ativo ORDER BY nome`),

    encomendas: await linhas(
      `SELECT e.id_encomenda, e.codigo, e.id_cliente, e.id_medico, e.id_paciente,
              est.nome AS estado, e.data_criacao, e.data_aceitacao, e.data_limite, e.observacoes
       FROM   encomenda e
       JOIN   estado_encomenda est ON est.id_estado = e.id_estado
       ORDER  BY e.data_criacao DESC`),

    trabalhos: await linhas(
      `SELECT ett.id_encomenda_tipo, ett.id_encomenda, e.codigo, ett.id_tipo_trabalho,
              tt.nome AS tipo_trabalho, est.nome AS estado,
              ett.natureza, ett.cor, ett.material_a_enviar, ett.data_prevista_consulta,
              ett.notas, e.id_paciente, e.data_limite
       FROM   encomenda_tipo_trabalho ett
       JOIN   encomenda e               ON e.id_encomenda = ett.id_encomenda
       JOIN   tipo_trabalho tt          ON tt.id_tipo_trabalho = ett.id_tipo_trabalho
       JOIN   estado_encomenda_tipo est ON est.id_estado = ett.id_estado
       ORDER  BY ett.id_encomenda_tipo`),

    pacientes: await linhas(
      `SELECT id_paciente, nome, fn_idade(data_nascimento) AS idade, sexo FROM paciente`),

    medicos: await linhas(`SELECT id_medico, cedula_profissional FROM medico`),

    trabalho_dentes: await linhas(
      `SELECT id_encomenda_tipo, numero_dente FROM odontograma
       ORDER BY id_encomenda_tipo, numero_dente`),

    tipos_trabalho: await linhas(
      `SELECT id_tipo_trabalho, nome FROM tipo_trabalho WHERE ativo ORDER BY nome`),

    // Etapas do processo ativo de cada tipo (a app não as deve numerar)
    etapas: await linhas(
      `SELECT e.id_etapa, p.id_tipo_trabalho, e.nome, e.ordem, e.obrigatoria
       FROM   etapa e JOIN processo p ON p.id_processo = e.id_processo AND p.ativo
       WHERE  e.ativa
       ORDER  BY p.id_tipo_trabalho, e.ordem`),

    execucoes: await linhas(
      `SELECT x.id_execucao, x.id_encomenda_tipo, x.id_etapa, et.nome AS etapa,
              x.id_colaborador, u.nome AS colaborador,
              x.id_colaborador_seguinte, x.id_etapa_seguinte,
              x.data_inicio, x.data_fim, x.estado_execucao, x.observacoes
       FROM   execucao_etapa x
       JOIN   etapa et ON et.id_etapa = x.id_etapa
       LEFT   JOIN colaborador c ON c.id_colaborador = x.id_colaborador
       LEFT   JOIN utilizador u  ON u.id_utilizador = c.id_utilizador
       ORDER  BY x.id_execucao`),

    colaboradores: await linhas(
      `SELECT id_colaborador, id_utilizador, nome, e_administrador
       FROM   vw_colaboradores WHERE ativo ORDER BY nome`),

    trabalhos_disponiveis: await linhas(
      `SELECT * FROM vw_trabalhos_disponiveis ORDER BY data_limite NULLS LAST`),

    trabalhos_atribuidos: await linhas(
      `SELECT * FROM vw_trabalhos_atribuidos WHERE id_colaborador = $1
       ORDER BY data_limite NULLS LAST`, [u.id_colaborador]),

    notas: await linhas(
      `SELECT n.id_nota, n.id_encomenda_tipo, n.conteudo, n.visibilidade, n.data_criacao,
              n.id_utilizador, u.nome AS autor
       FROM   nota n JOIN utilizador u ON u.id_utilizador = n.id_utilizador
       ORDER  BY n.data_criacao`),

    ficheiros: await linhas(
      `SELECT 'ficheiro' AS origem, id_ficheiro AS id, id_encomenda_tipo, tipo_ficheiro,
              ficheiro_path, visibilidade, data_upload, tamanho_ficheiro, id_utilizador
       FROM   ficheiro
       UNION ALL
       SELECT 'fotografia', id_fotografia, id_encomenda_tipo, 'foto',
              ficheiro_path, visibilidade, data_upload, tamanho_ficheiro, id_utilizador
       FROM   fotografia
       ORDER  BY data_upload`),

    notificacoes: await notificacoes(u),
  };
}

function notificacoes(u) {
  return linhas(
    `SELECT id_notificacao, tipo, mensagem, lida, data_criacao
     FROM   notificacao WHERE id_utilizador = $1
     ORDER  BY data_criacao DESC`, [u.id_utilizador]);
}

router.get('/sync/', exigeLogin, assincrono(async (req, res) => {
  const u = req.utilizador;
  let dados;
  if (u.perfil === 'cliente') {
    if (!u.id_cliente) {
      return res.status(403).json({ erro: 'Utilizador cliente sem registo na tabela cliente.' });
    }
    dados = await syncCliente(u);
  } else if (u.id_colaborador) {
    dados = await syncColaborador(u);
  } else {
    return res.status(403).json({ erro: 'Perfil sem acesso à aplicação.' });
  }

  const { rows } = await consulta(`SELECT to_char(now() AT TIME ZONE 'UTC',
    'YYYY-MM-DD"T"HH24:MI:SS"Z"') AS agora`);

  res.json({
    ...dados,
    servidor_em: rows[0].agora,
    eu: {
      id_utilizador: u.id_utilizador,
      nome: u.nome,
      email: u.email,
      perfil: u.perfil,
      cliente_id: u.id_cliente,
      colaborador_id: u.id_colaborador,
    },
  });
}));

module.exports = router;
