"""Consultas usadas em mais do que uma app (encomendas e execução)."""
from .db import query, query_one
from .ficheiros import nome_original


def encomenda(id_encomenda):
    return query_one(
        """SELECT e.id_encomenda, e.codigo, e.id_cliente, e.observacoes,
                  e.data_criacao, e.data_aceitacao, e.data_limite,
                  (e.data_limite::DATE - CURRENT_DATE) AS dias,
                  est.nome AS estado, fn_estado_cliente(est.nome) AS estado_cliente,
                  c.nome AS cliente, c.nif,
                  m.cedula_profissional,
                  pa.nome AS paciente, pa.sexo, fn_idade(pa.data_nascimento) AS idade_paciente,
                  u.nome AS criado_por
           FROM encomenda e
           JOIN cliente c            ON c.id_cliente = e.id_cliente
           JOIN estado_encomenda est ON est.id_estado = e.id_estado
           JOIN utilizador u         ON u.id_utilizador = e.criado_por
           LEFT JOIN medico m        ON m.id_medico = e.id_medico
           LEFT JOIN paciente pa     ON pa.id_paciente = e.id_paciente
           WHERE e.id_encomenda = %s""",
        [id_encomenda],
    )


def trabalhos(id_encomenda):
    return query(
        """SELECT ett.id_encomenda_tipo, tt.nome AS tipo_trabalho, est.nome AS estado,
                  fn_estado_cliente(est.nome) AS estado_cliente,
                  ett.natureza, ett.cor, ett.material_a_enviar, ett.data_prevista_consulta, ett.notas,
                  (SELECT string_agg(o.numero_dente::TEXT, ', ' ORDER BY o.numero_dente)
                   FROM odontograma o WHERE o.id_encomenda_tipo = ett.id_encomenda_tipo) AS dentes
           FROM encomenda_tipo_trabalho ett
           JOIN tipo_trabalho tt          ON tt.id_tipo_trabalho = ett.id_tipo_trabalho
           JOIN estado_encomenda_tipo est ON est.id_estado = ett.id_estado
           WHERE ett.id_encomenda = %s
           ORDER BY ett.id_encomenda_tipo""",
        [id_encomenda],
    )


def trabalho(id_encomenda_tipo):
    return query_one(
        """SELECT ett.id_encomenda_tipo, ett.id_encomenda, e.codigo, c.nome AS cliente,
                  tt.nome AS tipo_trabalho, est.nome AS estado,
                  ett.natureza, ett.cor, ett.material_a_enviar, ett.data_prevista_consulta,
                  e.data_limite, (e.data_limite::DATE - CURRENT_DATE) AS dias, e.observacoes,
                  pa.nome AS paciente, pa.sexo, fn_idade(pa.data_nascimento) AS idade_paciente,
                  m.cedula_profissional,
                  (SELECT string_agg(o.numero_dente::TEXT, ', ' ORDER BY o.numero_dente)
                   FROM odontograma o WHERE o.id_encomenda_tipo = ett.id_encomenda_tipo) AS dentes
           FROM encomenda_tipo_trabalho ett
           JOIN encomenda e               ON e.id_encomenda = ett.id_encomenda
           JOIN cliente c                 ON c.id_cliente = e.id_cliente
           JOIN tipo_trabalho tt          ON tt.id_tipo_trabalho = ett.id_tipo_trabalho
           JOIN estado_encomenda_tipo est ON est.id_estado = ett.id_estado
           LEFT JOIN paciente pa          ON pa.id_paciente = e.id_paciente
           LEFT JOIN medico m             ON m.id_medico = e.id_medico
           WHERE ett.id_encomenda_tipo = %s""",
        [id_encomenda_tipo],
    )


def etapas(id_encomenda_tipo):
    """Etapas do processo ativo com a situação neste trabalho (sem numeração)."""
    return query(
        """SELECT et.id_etapa, et.nome, et.obrigatoria,
                  CASE
                    WHEN bool_or(x.id_execucao IS NOT NULL AND x.data_fim IS NULL) THEN 'em-curso'
                    WHEN bool_or(x.data_fim IS NOT NULL)                           THEN 'feita'
                    ELSE 'por-fazer'
                  END AS situacao,
                  string_agg(DISTINCT u.nome, ', ')  AS por,
                  min(x.data_inicio)                 AS inicio,
                  max(x.data_fim)                    AS fim
           FROM encomenda_tipo_trabalho ett
           JOIN processo p        ON p.id_tipo_trabalho = ett.id_tipo_trabalho AND p.ativo
           JOIN etapa et          ON et.id_processo = p.id_processo AND et.ativa
           LEFT JOIN execucao_etapa x ON x.id_etapa = et.id_etapa AND x.id_encomenda_tipo = ett.id_encomenda_tipo
           LEFT JOIN colaborador c    ON c.id_colaborador = x.id_colaborador
           LEFT JOIN utilizador u     ON u.id_utilizador = c.id_utilizador
           WHERE ett.id_encomenda_tipo = %s
           GROUP BY et.id_etapa, et.nome, et.obrigatoria, et.ordem
           ORDER BY et.ordem""",
        [id_encomenda_tipo],
    )


def execucoes(id_encomenda_tipo):
    return query(
        """SELECT x.id_execucao, et.nome AS etapa, u.nome AS colaborador, x.data_inicio, x.data_fim,
                  (x.data_fim - x.data_inicio) AS duracao, x.observacoes,
                  us.nome AS seguinte, es.nome AS etapa_seguinte
           FROM execucao_etapa x
           JOIN etapa et            ON et.id_etapa = x.id_etapa
           JOIN colaborador c       ON c.id_colaborador = x.id_colaborador
           JOIN utilizador u        ON u.id_utilizador = c.id_utilizador
           LEFT JOIN colaborador cs ON cs.id_colaborador = x.id_colaborador_seguinte
           LEFT JOIN utilizador us  ON us.id_utilizador = cs.id_utilizador
           LEFT JOIN etapa es       ON es.id_etapa = x.id_etapa_seguinte
           WHERE x.id_encomenda_tipo = %s
           ORDER BY x.data_inicio DESC, x.id_execucao DESC""",
        [id_encomenda_tipo],
    )


def notas(id_encomenda=None, id_encomenda_tipo=None, so_cliente=False, id_utilizador_cliente=None):
    """Notas de uma encomenda ou de um trabalho. O cliente vê as visíveis e as suas."""
    return query(
        """SELECT n.id_nota, n.conteudo, n.visibilidade, n.data_criacao,
                  u.nome AS autor, p.nome AS perfil_autor, tt.nome AS tipo_trabalho
           FROM nota n
           JOIN utilizador u                ON u.id_utilizador = n.id_utilizador
           JOIN perfil p                    ON p.id_perfil = u.id_perfil
           JOIN encomenda_tipo_trabalho ett ON ett.id_encomenda_tipo = n.id_encomenda_tipo
           JOIN tipo_trabalho tt            ON tt.id_tipo_trabalho = ett.id_tipo_trabalho
           WHERE (%s::INT IS NULL OR ett.id_encomenda = %s)
             AND (%s::INT IS NULL OR ett.id_encomenda_tipo = %s)
             AND (NOT %s OR n.visibilidade = 'cliente' OR n.id_utilizador = %s)
           ORDER BY n.data_criacao DESC, n.id_nota DESC""",
        [id_encomenda, id_encomenda, id_encomenda_tipo, id_encomenda_tipo, so_cliente, id_utilizador_cliente],
    )


def anexos(id_encomenda=None, id_encomenda_tipo=None, so_cliente=False, id_utilizador_cliente=None):
    """Fotografias e ficheiros juntos, mais recentes primeiro."""
    linhas = query(
        """SELECT 'fotografia' AS tipo, f.id_fotografia AS id, 'Fotografia' AS formato,
                  f.ficheiro_path, f.visibilidade, f.data_upload, f.tamanho_ficheiro,
                  u.nome AS autor, tt.nome AS tipo_trabalho
           FROM fotografia f
           JOIN utilizador u                ON u.id_utilizador = f.id_utilizador
           JOIN encomenda_tipo_trabalho ett ON ett.id_encomenda_tipo = f.id_encomenda_tipo
           JOIN tipo_trabalho tt            ON tt.id_tipo_trabalho = ett.id_tipo_trabalho
           WHERE (%s::INT IS NULL OR ett.id_encomenda = %s)
             AND (%s::INT IS NULL OR ett.id_encomenda_tipo = %s)
             AND (NOT %s OR f.visibilidade = 'cliente' OR f.id_utilizador = %s)
           UNION ALL
           SELECT 'ficheiro', fi.id_ficheiro, fi.tipo_ficheiro,
                  fi.ficheiro_path, fi.visibilidade, fi.data_upload, fi.tamanho_ficheiro,
                  u.nome, tt.nome
           FROM ficheiro fi
           JOIN utilizador u                ON u.id_utilizador = fi.id_utilizador
           JOIN encomenda_tipo_trabalho ett ON ett.id_encomenda_tipo = fi.id_encomenda_tipo
           JOIN tipo_trabalho tt            ON tt.id_tipo_trabalho = ett.id_tipo_trabalho
           WHERE (%s::INT IS NULL OR ett.id_encomenda = %s)
             AND (%s::INT IS NULL OR ett.id_encomenda_tipo = %s)
             AND (NOT %s OR fi.visibilidade = 'cliente' OR fi.id_utilizador = %s)
           ORDER BY data_upload DESC""",
        [id_encomenda, id_encomenda, id_encomenda_tipo, id_encomenda_tipo, so_cliente, id_utilizador_cliente] * 2,
    )
    for a in linhas:
        a["nome"] = nome_original(a["ficheiro_path"])
    return linhas


def historico(id_encomenda):
    return query(
        """SELECT h.data_hora, tt.nome AS tipo_trabalho, est.nome AS estado, u.nome AS por, h.observacoes
           FROM historico_estado h
           JOIN encomenda_tipo_trabalho ett ON ett.id_encomenda_tipo = h.id_encomenda_tipo
           JOIN tipo_trabalho tt            ON tt.id_tipo_trabalho = ett.id_tipo_trabalho
           JOIN estado_encomenda_tipo est   ON est.id_estado = h.id_estado
           LEFT JOIN colaborador c          ON c.id_colaborador = h.id_colaborador
           LEFT JOIN utilizador u           ON u.id_utilizador = c.id_utilizador
           WHERE ett.id_encomenda = %s
           ORDER BY h.data_hora DESC, h.id_historico DESC""",
        [id_encomenda],
    )
