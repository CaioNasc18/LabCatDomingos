"""
Acesso à base de dados em SQL direto (sem ORM).

Todas as queries usam parâmetros (%s), nunca concatenação de strings,
para evitar SQL injection.
"""
import re
from contextlib import contextmanager

from django.db import DatabaseError, connection, transaction

atomic = transaction.atomic


def _linhas_para_dicts(cursor):
    colunas = [c.name for c in cursor.description]
    return [dict(zip(colunas, linha)) for linha in cursor.fetchall()]


def query(sql, params=None):
    """SELECT que devolve várias linhas, como lista de dicionários."""
    with connection.cursor() as cur:
        cur.execute(sql, params or [])
        return _linhas_para_dicts(cur)


def query_one(sql, params=None):
    """SELECT que devolve uma linha (dicionário) ou None."""
    linhas = query(sql, params)
    return linhas[0] if linhas else None


def execute(sql, params=None):
    """INSERT/UPDATE/DELETE. Com RETURNING devolve a primeira coluna da linha."""
    with connection.cursor() as cur:
        cur.execute(sql, params or [])
        if cur.description:
            return cur.fetchone()[0]
        return cur.rowcount


_NOME_PROCEDIMENTO = re.compile(r"^sp_[a-z_]+$")


def chamar(procedimento, *params):
    """
    CALL a um procedimento da BD (04_logica.sql).
    Devolve os parâmetros INOUT como dicionário (ou None).
    Ex.: chamar("sp_aceitar_encomenda", 1, data_limite, id_utilizador)
    """
    if not _NOME_PROCEDIMENTO.match(procedimento):
        raise ValueError("Nome de procedimento inválido.")
    marcadores = ", ".join(["%s"] * len(params))
    with connection.cursor() as cur:
        cur.execute(f"CALL {procedimento}({marcadores})", list(params))
        if cur.description:
            return _linhas_para_dicts(cur)[0]
    return None


@contextmanager
def como_utilizador(id_utilizador):
    """
    Transação em que os triggers sabem quem está a fazer a ação
    (logs e histórico). Usar em INSERT/UPDATE/DELETE feitos pelo Django:

        with como_utilizador(request.session["id_utilizador"]):
            execute("UPDATE cliente SET ativo = false WHERE id_cliente = %s", [id])
    """
    with atomic():
        execute("SELECT set_config('app.id_utilizador', %s, true)", [str(id_utilizador)])
        yield


def mensagem_erro(exc):
    """Texto do RAISE EXCEPTION do PostgreSQL, para mostrar ao utilizador."""
    causa = exc.__cause__ or exc
    diag = getattr(causa, "diag", None)
    if diag is not None and diag.message_primary:
        return diag.message_primary
    return str(exc)


def registar_log(id_utilizador, acao, tabela=None, registo_id=None, detalhes=None):
    execute(
        """INSERT INTO logs (id_utilizador, acao, tabela_afetada, registo_id, detalhes)
           VALUES (%s, %s, %s, %s, %s)""",
        [id_utilizador, acao, tabela, registo_id, detalhes],
    )


__all__ = [
    "DatabaseError", "atomic", "chamar", "como_utilizador", "execute",
    "mensagem_erro", "query", "query_one", "registar_log",
]
