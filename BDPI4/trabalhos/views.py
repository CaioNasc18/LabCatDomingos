from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from core import consultas
from core.auth import requer_colaborador
from core.db import DatabaseError, chamar, mensagem_erro, query, query_one
from core.ficheiros import EXTENSOES
from core.templatetags.core_extras import lista_dentes


@requer_colaborador
def meus(request):
    """Página inicial do colaborador: etapas em curso e trabalhos que lhe foram encaminhados."""
    linhas = query(
        """SELECT atribuicao, id_execucao, id_encomenda_tipo, codigo, tipo_trabalho, etapa,
                  estado_trabalho, data_inicio, data_limite, dias_ate_limite, observacoes
           FROM vw_trabalhos_atribuidos
           WHERE id_colaborador = %s
           ORDER BY dias_ate_limite NULLS LAST, data_inicio""",
        [request.session["id_colaborador"]],
    )
    em_curso = [l for l in linhas if l["atribuicao"] == "Em curso"]
    encaminhados = [l for l in linhas if l["atribuicao"] != "Em curso"]
    disponiveis = query_one("SELECT COUNT(*) AS n FROM vw_trabalhos_disponiveis")["n"]
    return render(request, "trabalhos/meus.html",
                  {"em_curso": em_curso, "encaminhados": encaminhados, "disponiveis": disponiveis})


@requer_colaborador
def disponiveis(request):
    q = (request.GET.get("q") or "").strip() or None
    linhas = query(
        """SELECT v.id_encomenda_tipo, v.codigo, v.cliente, v.tipo_trabalho, v.estado_trabalho,
                  v.data_limite, v.dias_ate_limite, pa.nome AS paciente,
                  (SELECT string_agg(o.numero_dente::TEXT, ', ' ORDER BY o.numero_dente)
                   FROM odontograma o WHERE o.id_encomenda_tipo = v.id_encomenda_tipo) AS dentes
           FROM vw_trabalhos_disponiveis v
           JOIN encomenda_tipo_trabalho ett ON ett.id_encomenda_tipo = v.id_encomenda_tipo
           JOIN encomenda e      ON e.id_encomenda = ett.id_encomenda
           LEFT JOIN paciente pa ON pa.id_paciente = e.id_paciente
           WHERE (%s::TEXT IS NULL OR v.codigo ILIKE '%%' || %s || '%%' OR v.tipo_trabalho ILIKE '%%' || %s || '%%'
                  OR pa.nome ILIKE '%%' || %s || '%%')
           ORDER BY v.dias_ate_limite NULLS LAST""",
        [q, q, q, q],
    )
    return render(request, "trabalhos/disponiveis.html", {"linhas": linhas})


@requer_colaborador
def realizados(request):
    linhas = query(
        """SELECT id_encomenda_tipo, codigo, tipo_trabalho, etapa, data_inicio, data_fim, duracao, observacoes
           FROM vw_trabalhos_realizados
           WHERE id_colaborador = %s
           ORDER BY data_fim DESC LIMIT 200""",
        [request.session["id_colaborador"]],
    )
    return render(request, "trabalhos/realizados.html", {"linhas": linhas})


@requer_colaborador
def detalhe(request, id_encomenda_tipo):
    t = consultas.trabalho(id_encomenda_tipo)
    if not t:
        raise Http404
    t["sel"] = lista_dentes(t["dentes"])
    minha = query_one(
        """SELECT x.id_execucao, et.nome AS etapa, x.data_inicio
           FROM execucao_etapa x JOIN etapa et ON et.id_etapa = x.id_etapa
           WHERE x.id_encomenda_tipo = %s AND x.id_colaborador = %s AND x.data_fim IS NULL
           ORDER BY x.data_inicio DESC LIMIT 1""",
        [id_encomenda_tipo, request.session["id_colaborador"]],
    )
    etapas = consultas.etapas(id_encomenda_tipo)
    colegas = query("SELECT id_colaborador, nome, e_administrador FROM vw_colaboradores WHERE ativo ORDER BY nome")
    separador = request.GET.get("tab", "execucao")
    return render(request, "trabalhos/detalhe.html", {
        "t": t, "minha": minha, "etapas": etapas, "colegas": colegas, "separador": separador,
        "execucoes": consultas.execucoes(id_encomenda_tipo),
        "notas": consultas.notas(id_encomenda_tipo=id_encomenda_tipo),
        "anexos": consultas.anexos(id_encomenda_tipo=id_encomenda_tipo),
        "trabalhos": [{"id_encomenda_tipo": t["id_encomenda_tipo"], "tipo_trabalho": t["tipo_trabalho"]}],
        "feitas": sum(1 for e in etapas if e["situacao"] == "feita"),
        "extensoes": ", ".join(sorted(EXTENSOES)),
        "finais_bloqueadas": t["estado"] != "Concluído",
    })


@require_POST
@requer_colaborador
def assumir(request, id_encomenda_tipo):
    try:
        chamar("sp_assumir_etapa", id_encomenda_tipo, int(request.POST.get("etapa", 0)),
               request.session["id_colaborador"], None)
        messages.success(request, "Etapa iniciada. A data e a hora de início ficaram registadas.")
    except (DatabaseError, ValueError) as exc:
        messages.error(request, mensagem_erro(exc) if isinstance(exc, DatabaseError) else "Escolha uma etapa.")
    return redirect("trabalhos:detalhe", id_encomenda_tipo)


@require_POST
@requer_colaborador
def concluir(request, id_execucao):
    x = query_one("SELECT id_encomenda_tipo FROM execucao_etapa WHERE id_execucao = %s", [id_execucao])
    if not x:
        raise Http404
    seguinte = request.POST.get("seguinte") or None
    etapa_seguinte = request.POST.get("etapa_seguinte") or None
    try:
        chamar("sp_concluir_etapa", id_execucao, request.session["id_colaborador"],
               int(seguinte) if seguinte else None,
               (request.POST.get("observacoes") or "").strip() or None,
               int(etapa_seguinte) if etapa_seguinte else None)
        if seguinte:
            messages.success(request, "Etapa concluída e trabalho encaminhado. O colega foi notificado.")
        else:
            messages.success(request, "Etapa concluída.")
    except DatabaseError as exc:
        messages.error(request, mensagem_erro(exc))
    return redirect("trabalhos:detalhe", x["id_encomenda_tipo"])


@require_POST
@requer_colaborador
def estado(request, id_encomenda_tipo):
    novo = request.POST.get("estado")
    try:
        chamar("sp_alterar_estado_trabalho", id_encomenda_tipo, novo, request.session["id_utilizador"],
               (request.POST.get("justificacao") or "").strip() or None)
        texto = {"Em espera": "Trabalho colocado em espera.", "Em processamento": "Trabalho retomado.",
                 "Concluído": "Trabalho concluído. A faturação e o envio final ficaram disponíveis."}
        messages.success(request, texto.get(novo, "Estado alterado."))
    except DatabaseError as exc:
        messages.error(request, mensagem_erro(exc))
    return redirect("trabalhos:detalhe", id_encomenda_tipo)
