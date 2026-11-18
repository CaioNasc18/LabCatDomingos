from django.contrib import messages
from django.db import IntegrityError
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from core.auth import hash_password, requer_funcionalidade
from core.db import DatabaseError, como_utilizador, execute, mensagem_erro, query, query_one


def _erro_unico(exc):
    texto = mensagem_erro(exc)
    if "email" in texto:
        return "Já existe um utilizador com esse e-mail."
    if "nif" in texto:
        return "Já existe um cliente com esse NIF."
    if "nome" in texto:
        return "Já existe um registo com esse nome."
    return texto


def _password_valida(request, password):
    if len(password) < 8:
        messages.error(request, "A palavra-passe inicial tem de ter pelo menos 8 caracteres.")
        return False
    return True


# ---------------------------------------------------------------------
# Clientes
# ---------------------------------------------------------------------
@requer_funcionalidade("Gestão de clientes")
def clientes(request):
    q = (request.GET.get("q") or "").strip() or None
    linhas = query(
        """SELECT c.id_cliente, c.nome, c.nif, c.tipo_entidade, u.email, u.telefone,
                  (c.ativo AND u.ativo) AS ativo,
                  (SELECT COUNT(*) FROM encomenda e WHERE e.id_cliente = c.id_cliente) AS encomendas
           FROM cliente c JOIN utilizador u ON u.id_utilizador = c.id_utilizador
           WHERE (%s::TEXT IS NULL OR c.nome ILIKE '%%' || %s || '%%' OR c.nif ILIKE '%%' || %s || '%%')
           ORDER BY c.nome""",
        [q, q, q],
    )
    return render(request, "gestao/clientes.html", {"linhas": linhas})


@requer_funcionalidade("Gestão de clientes")
def cliente_form(request, id_cliente=None):
    atual = None
    if id_cliente:
        atual = query_one(
            """SELECT c.id_cliente, c.id_utilizador, c.nome, c.nif, c.morada, c.tipo_entidade, u.email, u.telefone
               FROM cliente c JOIN utilizador u ON u.id_utilizador = c.id_utilizador WHERE c.id_cliente = %s""",
            [id_cliente])
        if not atual:
            raise Http404
    campos = ["nome", "nif", "email", "telefone", "morada", "tipo_entidade", "password"]
    dados = {k: (request.POST.get(k) or "").strip() for k in campos} if request.method == "POST" else (atual or {})

    if request.method == "POST":
        if not dados["nome"] or not dados["nif"] or not dados["email"]:
            messages.error(request, "Nome, NIF e e-mail são obrigatórios.")
        elif not atual and not _password_valida(request, request.POST.get("password", "")):
            pass
        else:
            try:
                with como_utilizador(request.session["id_utilizador"]):
                    if atual:
                        execute("UPDATE utilizador SET nome = %s, email = %s, telefone = %s WHERE id_utilizador = %s",
                                [dados["nome"], dados["email"], dados["telefone"] or None, atual["id_utilizador"]])
                        execute("""UPDATE cliente SET nome = %s, nif = %s, morada = %s, tipo_entidade = %s
                                   WHERE id_cliente = %s""",
                                [dados["nome"], dados["nif"], dados["morada"] or None, dados["tipo_entidade"] or None,
                                 id_cliente])
                    else:
                        uid = execute(
                            """INSERT INTO utilizador (id_perfil, nome, email, password_hash, telefone)
                               SELECT id_perfil, %s, %s, %s, %s FROM perfil WHERE nome = 'Cliente'
                               RETURNING id_utilizador""",
                            [dados["nome"], dados["email"], hash_password(request.POST["password"]),
                             dados["telefone"] or None])
                        execute("""INSERT INTO cliente (id_utilizador, nome, nif, morada, tipo_entidade)
                                   VALUES (%s, %s, %s, %s, %s)""",
                                [uid, dados["nome"], dados["nif"], dados["morada"] or None, dados["tipo_entidade"] or None])
                messages.success(request, "Cliente guardado.")
                return redirect("gestao:clientes")
            except IntegrityError as exc:
                messages.error(request, _erro_unico(exc))
    return render(request, "gestao/cliente_form.html", {"d": dados, "atual": atual})


@require_POST
@requer_funcionalidade("Gestão de clientes")
def ativar_cliente(request, id_cliente):
    with como_utilizador(request.session["id_utilizador"]):
        execute("UPDATE cliente SET ativo = NOT ativo WHERE id_cliente = %s", [id_cliente])
        execute("""UPDATE utilizador u SET ativo = c.ativo FROM cliente c
                   WHERE c.id_cliente = %s AND u.id_utilizador = c.id_utilizador""", [id_cliente])
    messages.success(request, "Estado do cliente alterado.")
    return redirect("gestao:clientes")


# ---------------------------------------------------------------------
# Colaboradores (inclui administradores)
# ---------------------------------------------------------------------
@requer_funcionalidade("Gestão de colaboradores")
def colaboradores(request):
    linhas = query(
        """SELECT v.*,
                  (SELECT COUNT(*) FROM vw_trabalhos_atribuidos a WHERE a.id_colaborador = v.id_colaborador) AS atuais,
                  (SELECT COUNT(*) FROM vw_trabalhos_realizados r WHERE r.id_colaborador = v.id_colaborador) AS realizadas
           FROM vw_colaboradores v ORDER BY v.ativo DESC, v.nome"""
    )
    return render(request, "gestao/colaboradores.html", {"linhas": linhas})


@requer_funcionalidade("Gestão de colaboradores")
def colaborador_novo(request):
    dados = {k: (request.POST.get(k) or "").strip() for k in ("nome", "email", "telefone")}
    dados["administrador"] = request.POST.get("administrador") == "1"
    if request.method == "POST":
        if not dados["nome"] or not dados["email"]:
            messages.error(request, "Nome e e-mail são obrigatórios.")
        elif _password_valida(request, request.POST.get("password", "")):
            perfil = "Administrador" if dados["administrador"] else "Colaborador"
            try:
                with como_utilizador(request.session["id_utilizador"]):
                    uid = execute(
                        """INSERT INTO utilizador (id_perfil, nome, email, password_hash, telefone)
                           SELECT id_perfil, %s, %s, %s, %s FROM perfil WHERE nome = %s RETURNING id_utilizador""",
                        [dados["nome"], dados["email"], hash_password(request.POST["password"]),
                         dados["telefone"] or None, perfil])
                    if dados["administrador"]:
                        # o trigger trg_admin_colaborador cria também o registo de colaborador
                        execute("INSERT INTO administrador (id_utilizador) VALUES (%s)", [uid])
                    else:
                        execute("INSERT INTO colaborador (id_utilizador) VALUES (%s)", [uid])
                messages.success(request, f"{perfil} criado.")
                return redirect("gestao:colaboradores")
            except IntegrityError as exc:
                messages.error(request, _erro_unico(exc))
    return render(request, "gestao/colaborador_form.html", {"d": dados})


@require_POST
@requer_funcionalidade("Gestão de colaboradores")
def ativar_colaborador(request, id_colaborador):
    c = query_one("SELECT id_utilizador FROM colaborador WHERE id_colaborador = %s", [id_colaborador])
    if not c:
        raise Http404
    if c["id_utilizador"] == request.session["id_utilizador"]:
        messages.error(request, "Não pode desativar a sua própria conta.")
        return redirect("gestao:colaboradores")
    with como_utilizador(request.session["id_utilizador"]):
        execute("UPDATE colaborador SET ativo = NOT ativo WHERE id_colaborador = %s", [id_colaborador])
        execute("""UPDATE utilizador u SET ativo = c.ativo FROM colaborador c
                   WHERE c.id_colaborador = %s AND u.id_utilizador = c.id_utilizador""", [id_colaborador])
    messages.success(request, "Estado do colaborador alterado.")
    return redirect("gestao:colaboradores")


# ---------------------------------------------------------------------
# Utilizadores
# ---------------------------------------------------------------------
@requer_funcionalidade("Gestão de utilizadores")
def utilizadores(request):
    linhas = query(
        """SELECT u.id_utilizador, u.nome, u.email, p.nome AS perfil, u.ativo, u.data_criacao, u.ultimo_login
           FROM utilizador u JOIN perfil p ON p.id_perfil = u.id_perfil
           ORDER BY p.id_perfil, u.nome"""
    )
    return render(request, "gestao/utilizadores.html", {"linhas": linhas})


@require_POST
@requer_funcionalidade("Gestão de utilizadores")
def ativar_utilizador(request, id_utilizador):
    if id_utilizador == request.session["id_utilizador"]:
        messages.error(request, "Não pode desativar a sua própria conta.")
    else:
        with como_utilizador(request.session["id_utilizador"]):
            execute("UPDATE utilizador SET ativo = NOT ativo WHERE id_utilizador = %s", [id_utilizador])
        messages.success(request, "Estado do utilizador alterado.")
    return redirect("gestao:utilizadores")


@require_POST
@requer_funcionalidade("Gestão de utilizadores")
def repor_password(request, id_utilizador):
    nova = request.POST.get("password", "")
    if _password_valida(request, nova):
        with como_utilizador(request.session["id_utilizador"]):
            execute("UPDATE utilizador SET password_hash = %s WHERE id_utilizador = %s",
                    [hash_password(nova), id_utilizador])
        messages.success(request, "Palavra-passe reposta. Comunique-a ao utilizador.")
    return redirect("gestao:utilizadores")


# ---------------------------------------------------------------------
# Tipos de trabalho, processos e etapas
# ---------------------------------------------------------------------
@requer_funcionalidade("Gestão de Tipos de Trabalho", "Gestão de Processos", "Gestão de Etapas")
def tipos(request):
    linhas = query(
        """SELECT tt.id_tipo_trabalho, tt.nome, tt.ativo, p.nome AS processo,
                  COUNT(e.id_etapa) FILTER (WHERE e.ativa)                   AS etapas,
                  COUNT(e.id_etapa) FILTER (WHERE e.ativa AND e.obrigatoria) AS obrigatorias,
                  (SELECT COUNT(*) FROM encomenda_tipo_trabalho ett WHERE ett.id_tipo_trabalho = tt.id_tipo_trabalho) AS usos
           FROM tipo_trabalho tt
           LEFT JOIN processo p ON p.id_tipo_trabalho = tt.id_tipo_trabalho AND p.ativo
           LEFT JOIN etapa e    ON e.id_processo = p.id_processo
           GROUP BY tt.id_tipo_trabalho, p.nome
           ORDER BY tt.ativo DESC, tt.nome"""
    )
    return render(request, "gestao/tipos.html", {"linhas": linhas})


@requer_funcionalidade("Gestão de Tipos de Trabalho")
def tipo_novo(request):
    d = {"nome": (request.POST.get("nome") or "").strip(), "descricao": (request.POST.get("descricao") or "").strip(),
         "etapas": request.POST.get("etapas") or "", "finais": request.method != "POST" or request.POST.get("finais") == "1"}
    if request.method == "POST":
        etapas = [l.strip() for l in d["etapas"].splitlines() if l.strip()]
        if d["finais"]:
            etapas = [e for e in etapas if e not in ("Faturação", "Embalamento e envio final")]
            etapas += ["Faturação", "Embalamento e envio final"]
        if not d["nome"] or not etapas:
            messages.error(request, "Indique o nome e pelo menos uma etapa.")
        else:
            try:
                with como_utilizador(request.session["id_utilizador"]):
                    id_tipo = execute("INSERT INTO tipo_trabalho (nome, descricao) VALUES (%s, %s) RETURNING id_tipo_trabalho",
                                      [d["nome"], d["descricao"] or None])
                    id_proc = execute("INSERT INTO processo (id_tipo_trabalho, nome) VALUES (%s, %s) RETURNING id_processo",
                                      [id_tipo, f"Processo {d['nome']}"])
                    for ordem, nome in enumerate(etapas, start=1):
                        execute("INSERT INTO etapa (id_processo, ordem, nome, obrigatoria) VALUES (%s, %s, %s, %s)",
                                [id_proc, ordem, nome, nome in ("Faturação", "Embalamento e envio final")])
                messages.success(request, "Tipo de trabalho criado com o seu processo e etapas.")
                return redirect("gestao:tipo", id_tipo)
            except IntegrityError as exc:
                messages.error(request, _erro_unico(exc))
    return render(request, "gestao/tipo_novo.html", {"d": d})


@requer_funcionalidade("Gestão de Tipos de Trabalho", "Gestão de Processos", "Gestão de Etapas")
def tipo(request, id_tipo_trabalho):
    t = query_one(
        """SELECT tt.*, p.id_processo, p.nome AS processo
           FROM tipo_trabalho tt LEFT JOIN processo p ON p.id_tipo_trabalho = tt.id_tipo_trabalho AND p.ativo
           WHERE tt.id_tipo_trabalho = %s""", [id_tipo_trabalho])
    if not t:
        raise Http404
    etapas = query(
        """SELECT e.id_etapa, e.nome, e.obrigatoria, e.ativa,
                  (SELECT COUNT(*) FROM execucao_etapa x WHERE x.id_etapa = e.id_etapa) AS execucoes
           FROM etapa e WHERE e.id_processo = %s ORDER BY e.ativa DESC, e.ordem""", [t["id_processo"]]) if t["id_processo"] else []
    return render(request, "gestao/tipo.html", {"t": t, "etapas": etapas})


@require_POST
@requer_funcionalidade("Gestão de Tipos de Trabalho")
def tipo_guardar(request, id_tipo_trabalho):
    nome = (request.POST.get("nome") or "").strip()
    if request.POST.get("acao") == "ativar":
        with como_utilizador(request.session["id_utilizador"]):
            execute("UPDATE tipo_trabalho SET ativo = NOT ativo WHERE id_tipo_trabalho = %s", [id_tipo_trabalho])
        messages.success(request, "Estado do tipo de trabalho alterado.")
    elif nome:
        try:
            with como_utilizador(request.session["id_utilizador"]):
                execute("UPDATE tipo_trabalho SET nome = %s, descricao = %s WHERE id_tipo_trabalho = %s",
                        [nome, (request.POST.get("descricao") or "").strip() or None, id_tipo_trabalho])
            messages.success(request, "Tipo de trabalho guardado.")
        except IntegrityError as exc:
            messages.error(request, _erro_unico(exc))
    return redirect("gestao:tipo", id_tipo_trabalho)


@require_POST
@requer_funcionalidade("Gestão de Etapas")
def etapa_nova(request, id_tipo_trabalho):
    nome = (request.POST.get("nome") or "").strip()
    p = query_one("SELECT id_processo FROM processo WHERE id_tipo_trabalho = %s AND ativo", [id_tipo_trabalho])
    if not nome or not p:
        messages.error(request, "Indique o nome da etapa.")
    else:
        with como_utilizador(request.session["id_utilizador"]):
            execute("""INSERT INTO etapa (id_processo, ordem, nome, obrigatoria)
                       SELECT %s, COALESCE(MAX(ordem), 0) + 1, %s, %s FROM etapa WHERE id_processo = %s""",
                    [p["id_processo"], nome, request.POST.get("obrigatoria") == "1", p["id_processo"]])
        messages.success(request, "Etapa acrescentada.")
    return redirect("gestao:tipo", id_tipo_trabalho)


@require_POST
@requer_funcionalidade("Gestão de Etapas")
def etapa_guardar(request, id_tipo_trabalho, id_etapa):
    nome = (request.POST.get("nome") or "").strip()
    if not nome:
        messages.error(request, "A etapa tem de ter nome.")
    else:
        with como_utilizador(request.session["id_utilizador"]):
            execute("""UPDATE etapa SET nome = %s, obrigatoria = %s, ativa = %s
                       WHERE id_etapa = %s
                         AND id_processo IN (SELECT id_processo FROM processo WHERE id_tipo_trabalho = %s)""",
                    [nome, request.POST.get("obrigatoria") == "1", request.POST.get("ativa") == "1",
                     id_etapa, id_tipo_trabalho])
        messages.success(request, "Etapa guardada.")
    return redirect("gestao:tipo", id_tipo_trabalho)


# ---------------------------------------------------------------------
# Permissões (matriz perfil × funcionalidade)
# ---------------------------------------------------------------------
@requer_funcionalidade("Gestão de permissões")
def permissoes(request):
    perfis = query("SELECT id_perfil, nome FROM perfil ORDER BY id_perfil")
    funcs = query(
        """SELECT f.id_funcionalidade, f.nome, f.plataforma, f.modulo,
                  array_agg(pf.id_perfil) FILTER (WHERE pf.id_perfil IS NOT NULL) AS perfis
           FROM funcionalidade f
           LEFT JOIN perfil_funcionalidade pf ON pf.id_funcionalidade = f.id_funcionalidade
           GROUP BY f.id_funcionalidade
           ORDER BY f.plataforma, f.modulo, f.nome"""
    )
    grupos = {}
    for f in funcs:
        f["marcas"] = [(p["id_perfil"], p["id_perfil"] in (f["perfis"] or [])) for p in perfis]
        grupos.setdefault(f["plataforma"], []).append(f)
    return render(request, "gestao/permissoes.html", {"perfis": perfis, "grupos": sorted(grupos.items())})


@require_POST
@requer_funcionalidade("Gestão de permissões")
def alternar_permissao(request, id_perfil, id_funcionalidade):
    f = query_one("""SELECT f.nome, p.nome AS perfil FROM funcionalidade f, perfil p
                     WHERE f.id_funcionalidade = %s AND p.id_perfil = %s""", [id_funcionalidade, id_perfil])
    if f and f["nome"] == "Gestão de permissões" and f["perfil"] == request.session["perfil"]:
        messages.error(request, "Não pode retirar ao seu próprio perfil a gestão de permissões.")
        return redirect("gestao:permissoes")
    with como_utilizador(request.session["id_utilizador"]):
        apagadas = execute("DELETE FROM perfil_funcionalidade WHERE id_perfil = %s AND id_funcionalidade = %s",
                           [id_perfil, id_funcionalidade])
        if not apagadas:
            execute("INSERT INTO perfil_funcionalidade (id_perfil, id_funcionalidade) VALUES (%s, %s)",
                    [id_perfil, id_funcionalidade])
    messages.success(request, "Permissão atualizada. Aplica-se no próximo início de sessão.")
    return redirect("gestao:permissoes")
