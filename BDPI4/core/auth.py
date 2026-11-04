"""
Autenticação própria sobre a tabela utilizador (sem django.contrib.auth).
As palavras-passe são guardadas com o hasher do Django (PBKDF2).
"""
from functools import wraps

from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import redirect

from .db import execute, query, query_one, registar_log


def autenticar(email, password):
    u = query_one(
        """SELECT u.id_utilizador, u.nome, u.password_hash, u.ativo, p.nome AS perfil
           FROM utilizador u JOIN perfil p ON p.id_perfil = u.id_perfil
           WHERE u.email = %s""",
        [email],
    )
    if not u or not u["ativo"] or not check_password(password, u["password_hash"]):
        return None
    execute("UPDATE utilizador SET ultimo_login = now() WHERE id_utilizador = %s",
            [u["id_utilizador"]])
    registar_log(u["id_utilizador"], "Login", "utilizador", u["id_utilizador"])
    return u


def funcionalidades_do_perfil(perfil, plataforma="Backoffice"):
    linhas = query(
        """SELECT f.nome
           FROM perfil_funcionalidade pf
           JOIN perfil p         ON p.id_perfil = pf.id_perfil
           JOIN funcionalidade f ON f.id_funcionalidade = pf.id_funcionalidade
           WHERE p.nome = %s AND f.plataforma = %s
           ORDER BY f.modulo, f.nome""",
        [perfil, plataforma],
    )
    return [l["nome"] for l in linhas]


def hash_password(password):
    return make_password(password)


def login_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if "id_utilizador" not in request.session:
            return redirect("login")
        return view(request, *args, **kwargs)
    return wrapper


def requer_funcionalidade(nome):
    """Bloqueia a view se o perfil do utilizador não tiver a funcionalidade."""
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapper(request, *args, **kwargs):
            if nome not in request.session.get("funcionalidades", []):
                return redirect("inicio")
            return view(request, *args, **kwargs)
        return wrapper
    return decorator
