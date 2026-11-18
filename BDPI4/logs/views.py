from django.shortcuts import render

from core.auth import requer_funcionalidade
from core.db import query


@requer_funcionalidade("Logs")
def lista(request):
    tabela = request.GET.get("tabela") or None
    acao = request.GET.get("acao") or None
    q = (request.GET.get("q") or "").strip() or None
    linhas = query(
        """SELECT id_logs, data_hora, utilizador, acao, tabela_afetada, registo_id, detalhes
           FROM vw_logs
           WHERE (%s::TEXT IS NULL OR tabela_afetada = %s)
             AND (%s::TEXT IS NULL OR acao = %s)
             AND (%s::TEXT IS NULL OR utilizador ILIKE '%%' || %s || '%%')
           ORDER BY id_logs DESC
           LIMIT 300""",
        [tabela, tabela, acao, acao, q, q],
    )
    tabelas = query("SELECT DISTINCT tabela_afetada FROM logs WHERE tabela_afetada IS NOT NULL ORDER BY 1")
    acoes = query("SELECT DISTINCT acao FROM logs ORDER BY 1")
    return render(request, "logs/lista.html",
                  {"linhas": linhas, "tabelas": tabelas, "acoes": acoes, "tabela": tabela, "acao": acao})
