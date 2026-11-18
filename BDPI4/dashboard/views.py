from django.shortcuts import render

from core.auth import requer_funcionalidade
from core.db import query, query_one


@requer_funcionalidade("Dashboard geral")
def dashboard(request):
    n = query_one("SELECT * FROM vw_dashboard")
    pedidos = query(
        """SELECT id_encomenda, codigo, cliente, tipos, data_criacao
           FROM vw_pedidos_por_aceitar ORDER BY data_criacao LIMIT 6"""
    )
    prazos = query(
        """SELECT e.id_encomenda, e.codigo, c.nome AS cliente, est.nome AS estado, e.data_limite,
                  (e.data_limite::DATE - CURRENT_DATE) AS dias
           FROM encomenda e
           JOIN cliente c            ON c.id_cliente = e.id_cliente
           JOIN estado_encomenda est ON est.id_estado = e.id_estado
           WHERE e.data_limite IS NOT NULL
             AND est.nome NOT IN ('Concluído', 'Entregue')
             AND e.data_limite::DATE <= CURRENT_DATE + 3
           ORDER BY e.data_limite
           LIMIT 8"""
    )
    meus = query(
        """SELECT atribuicao, id_encomenda_tipo, codigo, tipo_trabalho, etapa, estado_trabalho, dias_ate_limite
           FROM vw_trabalhos_atribuidos
           WHERE id_utilizador = %s
           ORDER BY dias_ate_limite NULLS LAST
           LIMIT 6""",
        [request.session["id_utilizador"]],
    )
    ativos = (n["por_iniciar"] + n["em_processamento"] + n["em_espera"] + n["em_prova"])
    return render(request, "dashboard/dashboard.html",
                  {"n": n, "ativos": ativos, "pedidos": pedidos, "prazos": prazos, "meus": meus})
