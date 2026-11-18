from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .auth import (autenticar, funcionalidades_do_perfil, hash_password, login_required,
                   password_correta, tem)
from .db import como_utilizador, execute, query, query_one


def login_view(request):
    if "id_utilizador" in request.session:
        return redirect("inicio")
    if request.method == "POST":
        u = autenticar(request.POST.get("email", ""), request.POST.get("password", ""))
        if u:
            request.session.cycle_key()
            request.session["id_utilizador"] = u["id_utilizador"]
            request.session["nome"] = u["nome_cliente"] or u["nome"]
            request.session["perfil"] = u["perfil"]
            request.session["id_colaborador"] = u["id_colaborador"]
            request.session["id_cliente"] = u["id_cliente"]
            request.session["e_administrador"] = u["e_administrador"]
            request.session["funcionalidades"] = funcionalidades_do_perfil(u["perfil"])
            return redirect("inicio")
        messages.error(request, "Email ou palavra-passe incorretos.")
    return render(request, "core/login.html")


def logout_view(request):
    request.session.flush()
    return redirect("login")


@login_required
def inicio(request):
    """Página de entrada conforme o perfil."""
    s = request.session
    if tem(request, "Dashboard geral"):
        return redirect("dashboard")                       # administrador
    if s.get("id_colaborador"):
        return redirect("trabalhos:meus")                  # colaborador: trabalhos atribuídos
    if s.get("id_cliente"):
        return redirect("encomendas:inicio_cliente")       # cliente
    return render(request, "core/sem_acesso.html")


@login_required
def notificacoes(request):
    filtro = request.GET.get("filtro", "todas")
    linhas = query(
        """SELECT id_notificacao, tipo, mensagem, lida, data_criacao
           FROM notificacao
           WHERE id_utilizador = %s AND (%s = 'todas' OR NOT lida)
           ORDER BY data_criacao DESC, id_notificacao DESC
           LIMIT 200""",
        [request.session["id_utilizador"], filtro],
    )
    return render(request, "core/notificacoes.html", {"linhas": linhas, "filtro": filtro})


@require_POST
@login_required
def marcar_lida(request, id_notificacao=None):
    if id_notificacao:
        execute("UPDATE notificacao SET lida = true WHERE id_notificacao = %s AND id_utilizador = %s",
                [id_notificacao, request.session["id_utilizador"]])
    else:
        execute("UPDATE notificacao SET lida = true WHERE id_utilizador = %s AND NOT lida",
                [request.session["id_utilizador"]])
    return redirect(request.POST.get("voltar") or "notificacoes")


@login_required
def conta(request):
    uid = request.session["id_utilizador"]
    if request.method == "POST":
        atual, nova, repetir = (request.POST.get(k, "") for k in ("atual", "nova", "repetir"))
        if not password_correta(uid, atual):
            messages.error(request, "A palavra-passe atual não está correta.")
        elif len(nova) < 8:
            messages.error(request, "A nova palavra-passe tem de ter pelo menos 8 caracteres.")
        elif nova != repetir:
            messages.error(request, "As duas palavras-passe novas não coincidem.")
        else:
            with como_utilizador(uid):
                execute("UPDATE utilizador SET password_hash = %s WHERE id_utilizador = %s",
                        [hash_password(nova), uid])
            messages.success(request, "Palavra-passe alterada.")
        return redirect("conta")

    u = query_one(
        """SELECT u.nome, u.email, u.telefone, p.nome AS perfil, u.data_criacao, u.ultimo_login,
                  cl.nome AS clinica, cl.nif, cl.morada, cl.tipo_entidade
           FROM utilizador u
           JOIN perfil p        ON p.id_perfil = u.id_perfil
           LEFT JOIN cliente cl ON cl.id_utilizador = u.id_utilizador
           WHERE u.id_utilizador = %s""",
        [uid],
    )
    resumo = None
    if request.session.get("id_colaborador"):
        resumo = query_one(
            """SELECT (SELECT COUNT(*) FROM vw_trabalhos_atribuidos WHERE id_colaborador = %s) AS atuais,
                      (SELECT COUNT(*) FROM vw_trabalhos_realizados WHERE id_colaborador = %s) AS concluidas""",
            [request.session["id_colaborador"]] * 2,
        )
    return render(request, "core/conta.html", {"u": u, "resumo": resumo})
