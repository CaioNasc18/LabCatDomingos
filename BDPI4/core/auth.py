"""
Autenticação própria sobre a tabela utilizador (sem django.contrib.auth).
As palavras-passe são guardadas com o hasher do Django (PBKDF2).
As permissões vêm da matriz perfil_funcionalidade (Mobile e Backoffice).
"""
from functools import wraps

from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import redirect

from .db import execute, query, query_one, registar_log


def autenticar(email, password):
    u = query_one(
        """SELECT u.id_utilizador, u.nome, u.password_hash, u.ativo, p.nome AS perfil,
                  c.id_colaborador, cl.id_cliente, cl.nome AS nome_cliente,
                  (a.id_administrador IS NOT NULL) AS e_administrador
           FROM utilizador u
           JOIN perfil p              ON p.id_perfil = u.id_perfil
           LEFT JOIN colaborador c    ON c.id_utilizador = u.id_utilizador AND c.ativo
           LEFT JOIN cliente cl       ON cl.id_utilizador = u.id_utilizador AND cl.ativo
           LEFT JOIN administrador a  ON a.id_utilizador = u.id_utilizador AND a.ativo
           WHERE lower(u.email) = lower(%s)""",
        [email.strip()],
    )
    if not u or not u["ativo"] or not check_password(password, u["password_hash"]):
        return None
    execute("UPDATE utilizador SET ultimo_login = now() WHERE id_utilizador = %s",
            [u["id_utilizador"]])
    registar_log(u["id_utilizador"], "Login", "utilizador", u["id_utilizador"])
    return u


def funcionalidades_do_perfil(perfil):
    """Nomes das funcionalidades do perfil, das duas plataformas."""
    linhas = query(
        """SELECT DISTINCT f.nome
           FROM perfil_funcionalidade pf
           JOIN perfil p         ON p.id_perfil = pf.id_perfil
           JOIN funcionalidade f ON f.id_funcionalidade = pf.id_funcionalidade
           WHERE p.nome = %s""",
        [perfil],
    )
    return sorted(l["nome"] for l in linhas)


def hash_password(password):
    return make_password(password)


def password_correta(id_utilizador, password):
    u = query_one("SELECT password_hash FROM utilizador WHERE id_utilizador = %s", [id_utilizador])
    return bool(u) and check_password(password, u["password_hash"])


def tem(request, *funcionalidades):
    """O utilizador tem alguma destas funcionalidades?"""
    f = request.session.get("funcionalidades", [])
    return any(x in f for x in funcionalidades)


def login_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if "id_utilizador" not in request.session:
            return redirect("login")
        return view(request, *args, **kwargs)
    return wrapper


def requer_funcionalidade(*nomes):
    """Bloqueia a view se o perfil não tiver nenhuma das funcionalidades indicadas."""
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapper(request, *args, **kwargs):
            if not tem(request, *nomes):
                messages.error(request, "Não tem permissão para aceder a essa página.")
                return redirect("inicio")
            return view(request, *args, **kwargs)
        return wrapper
    return decorator


def requer_colaborador(view):
    """Só para quem tem registo de colaborador (colaboradores e administradores)."""
    @wraps(view)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.session.get("id_colaborador"):
            messages.error(request, "Esta área é só para a equipa do laboratório.")
            return redirect("inicio")
        return view(request, *args, **kwargs)
    return wrapper


def requer_cliente(view):
    @wraps(view)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.session.get("id_cliente"):
            return redirect("inicio")
        return view(request, *args, **kwargs)
    return wrapper
