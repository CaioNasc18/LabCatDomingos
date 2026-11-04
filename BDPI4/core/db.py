from django.db import connection, transaction


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


def registar_log(id_utilizador, acao, tabela=None, registo_id=None, detalhes=None):
    execute(
        """INSERT INTO logs (id_utilizador, acao, tabela_afetada, registo_id, detalhes)
           VALUES (%s, %s, %s, %s, %s)""",
        [id_utilizador, acao, tabela, registo_id, detalhes],
    )


# Para várias operações que têm de acontecer juntas:
#   with transaction.atomic():
#       execute(...); execute(...)
atomic = transaction.atomic
