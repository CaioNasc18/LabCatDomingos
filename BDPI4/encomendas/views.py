from datetime import date, datetime

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from core import consultas
from core.auth import login_required, requer_cliente, requer_funcionalidade, tem
from core.db import DatabaseError, chamar, como_utilizador, execute, mensagem_erro, query, query_one
from core.ficheiros import EXTENSOES, FicheiroInvalido, enviar, guardar
from core.templatetags.core_extras import lista_dentes

ESTADOS = ["Em avaliação", "Por iniciar", "Em processamento", "Em espera", "Em prova", "Concluído", "Entregue"]
CORES_VITA = ["A1", "A2", "A3", "A3.5", "A4", "B1", "B2", "B3", "B4", "C1", "C2", "C3", "C4", "D2", "D3", "D4"]


def _e_laboratorio(request):
    return tem(request, "Todas as Encomendas")


def _encomenda_ou_404(request, id_encomenda):
    """Carrega a encomenda e verifica o acesso: a equipa do laboratório vê todas, o cliente só as suas."""
    e = consultas.encomenda(id_encomenda)
    if not e:
        raise Http404
    equipa = _e_laboratorio(request) or request.session.get("id_colaborador")
    if not equipa and e["id_cliente"] != request.session.get("id_cliente"):
        raise Http404
    return e


# ---------------------------------------------------------------------
# Laboratório
# ---------------------------------------------------------------------
@requer_funcionalidade("Alteração administrativa")
def pedidos(request):
    linhas = query(
        """SELECT id_encomenda, codigo, cliente, tipos, n_trabalhos,
                  to_char(data_criacao, 'DD/MM/YYYY HH24:MI') AS recebido
           FROM vw_pedidos_por_aceitar ORDER BY data_criacao"""
    )
    return render(request, "core/lista.html", {
        "titulo": "Pedidos por aceitar",
        "descricao": "Encomendas em avaliação. Ao aceitar, é obrigatório definir a data limite.",
        "colunas": [("codigo", "Pedido"), ("cliente", "Cliente"), ("tipos", "Tipos de trabalho"),
                    ("n_trabalhos", "Trabalhos"), ("recebido", "Recebido")],
        "linhas": linhas, "mono": ["codigo", "recebido"],
        "link": {"url": "encomendas:detalhe", "chave": "id_encomenda"},
        "vazio": "Não há pedidos por aceitar.",
    })


@requer_funcionalidade("Todas as Encomendas")
def lista(request):
    estado = request.GET.get("estado") or None
    q = (request.GET.get("q") or "").strip() or None
    linhas = query(
        """SELECT e.id_encomenda, e.codigo, c.nome AS cliente, est.nome AS estado, e.data_criacao, e.data_limite,
                  (e.data_limite::DATE - CURRENT_DATE) AS dias,
                  string_agg(tt.nome, ' + ' ORDER BY ett.id_encomenda_tipo) AS tipos
           FROM encomenda e
           JOIN cliente c            ON c.id_cliente = e.id_cliente
           JOIN estado_encomenda est ON est.id_estado = e.id_estado
           LEFT JOIN encomenda_tipo_trabalho ett ON ett.id_encomenda = e.id_encomenda
           LEFT JOIN tipo_trabalho tt ON tt.id_tipo_trabalho = ett.id_tipo_trabalho
           LEFT JOIN paciente pa      ON pa.id_paciente = e.id_paciente
           WHERE (%s::TEXT IS NULL OR est.nome = %s)
             AND (%s::TEXT IS NULL OR e.codigo ILIKE '%%' || %s || '%%'
                                   OR c.nome ILIKE '%%' || %s || '%%'
                                   OR pa.nome ILIKE '%%' || %s || '%%')
           GROUP BY e.id_encomenda, c.nome, est.nome
           ORDER BY e.data_criacao DESC""",
        [estado, estado, q, q, q, q],
    )
    return render(request, "encomendas/lista.html", {"linhas": linhas, "estados": ESTADOS, "estado": estado})


@requer_funcionalidade("Todas as Encomendas")
def detalhe(request, id_encomenda):
    e = _encomenda_ou_404(request, id_encomenda)
    separador = request.GET.get("tab", "resumo")
    trabalhos = consultas.trabalhos(id_encomenda)
    for t in trabalhos:
        t["sel"] = lista_dentes(t["dentes"])
        if separador == "etapas":
            t["etapas"] = consultas.etapas(t["id_encomenda_tipo"])
    notas = consultas.notas(id_encomenda=id_encomenda)
    anexos = consultas.anexos(id_encomenda=id_encomenda)
    return render(request, "encomendas/detalhe.html", {
        "e": e, "separador": separador, "trabalhos": trabalhos, "notas": notas, "anexos": anexos,
        "historico": consultas.historico(id_encomenda) if separador == "historico" else [],
        "pode_alterar": tem(request, "Alteração administrativa"),
        "extensoes": ", ".join(sorted(EXTENSOES)),
    })


@require_POST
@requer_funcionalidade("Alteração administrativa")
def aceitar(request, id_encomenda):
    try:
        data_limite = datetime.fromisoformat(request.POST.get("data_limite", ""))
    except ValueError:
        messages.error(request, "Indique uma data limite válida.")
        return redirect("encomendas:detalhe", id_encomenda)
    try:
        chamar("sp_aceitar_encomenda", id_encomenda, data_limite, request.session["id_utilizador"])
        messages.success(request, "Encomenda aceite. Os trabalhos ficaram disponíveis para a equipa.")
    except DatabaseError as exc:
        messages.error(request, mensagem_erro(exc))
    return redirect("encomendas:detalhe", id_encomenda)


@require_POST
@requer_funcionalidade("Alteração administrativa")
def alterar_estado(request, id_encomenda, id_encomenda_tipo):
    try:
        chamar("sp_alterar_estado_trabalho", id_encomenda_tipo, request.POST.get("estado"),
               request.session["id_utilizador"], (request.POST.get("justificacao") or "").strip() or None)
        messages.success(request, "Estado do trabalho alterado.")
    except DatabaseError as exc:
        messages.error(request, mensagem_erro(exc))
    return redirect("encomendas:detalhe", id_encomenda)


# ---------------------------------------------------------------------
# Notas e ficheiros (laboratório e cliente)
# ---------------------------------------------------------------------
def _voltar(request, e):
    destino = request.POST.get("voltar")
    if destino and destino.startswith("/"):
        return redirect(destino)
    if _e_laboratorio(request):
        return redirect("encomendas:detalhe", e["id_encomenda"])
    return redirect("encomendas:detalhe_cliente", e["id_encomenda"])


def _trabalho_da_encomenda(id_encomenda, valor):
    try:
        id_ett = int(valor)
    except (TypeError, ValueError):
        return None
    return query_one("SELECT 1 FROM encomenda_tipo_trabalho WHERE id_encomenda_tipo = %s AND id_encomenda = %s",
                     [id_ett, id_encomenda]) and id_ett


@require_POST
@login_required
def nova_nota(request, id_encomenda):
    e = _encomenda_ou_404(request, id_encomenda)
    id_ett = _trabalho_da_encomenda(id_encomenda, request.POST.get("trabalho"))
    conteudo = (request.POST.get("conteudo") or "").strip()
    cliente = not _e_laboratorio(request) and not request.session.get("id_colaborador")
    visibilidade = "cliente" if cliente else request.POST.get("visibilidade", "interna")
    if not id_ett or not conteudo:
        messages.error(request, "Escolha o trabalho e escreva a nota.")
        return _voltar(request, e)
    with como_utilizador(request.session["id_utilizador"]):
        execute("INSERT INTO nota (id_encomenda_tipo, id_utilizador, conteudo, visibilidade) VALUES (%s, %s, %s, %s)",
                [id_ett, request.session["id_utilizador"], conteudo, visibilidade])
    messages.success(request, "Nota guardada.")
    return _voltar(request, e)


@require_POST
@login_required
def novos_anexos(request, id_encomenda):
    e = _encomenda_ou_404(request, id_encomenda)
    id_ett = _trabalho_da_encomenda(id_encomenda, request.POST.get("trabalho"))
    cliente = not _e_laboratorio(request) and not request.session.get("id_colaborador")
    visibilidade = "cliente" if cliente else request.POST.get("visibilidade", "interna")
    ficheiros = request.FILES.getlist("ficheiros")
    if not id_ett or not ficheiros:
        messages.error(request, "Escolha o trabalho e pelo menos um ficheiro.")
        return _voltar(request, e)
    try:
        with como_utilizador(request.session["id_utilizador"]):
            for f in ficheiros:
                guardar(f, id_encomenda, id_ett, request.session["id_utilizador"], visibilidade)
        messages.success(request, f"{len(ficheiros)} ficheiro(s) adicionado(s).")
    except FicheiroInvalido as exc:
        messages.error(request, str(exc))
    return _voltar(request, e)


@login_required
def descarregar(request, tipo, id_anexo):
    tabela, chave = {"fotografia": ("fotografia", "id_fotografia"), "ficheiro": ("ficheiro", "id_ficheiro")}.get(tipo, (None, None))
    if not tabela:
        raise Http404
    a = query_one(
        f"""SELECT a.ficheiro_path, a.visibilidade, a.id_utilizador, ett.id_encomenda
            FROM {tabela} a JOIN encomenda_tipo_trabalho ett ON ett.id_encomenda_tipo = a.id_encomenda_tipo
            WHERE a.{chave} = %s""",
        [id_anexo],
    )
    if not a:
        raise Http404
    if not (_e_laboratorio(request) or request.session.get("id_colaborador")):
        _encomenda_ou_404(request, a["id_encomenda"])          # o cliente só acede às suas encomendas
        if a["visibilidade"] != "cliente" and a["id_utilizador"] != request.session["id_utilizador"]:
            raise Http404
    return enviar(a["ficheiro_path"], descarregar=request.GET.get("ver") != "1")


# ---------------------------------------------------------------------
# Nova encomenda (cliente ou administrador em nome do cliente)
# ---------------------------------------------------------------------
def _trabalhos_do_post(request):
    indices = sorted({int(k.split("-", 1)[1]) for k in request.POST
                      if k.startswith("tipo-") and k.split("-", 1)[1].isdigit()})
    lista = []
    for i in indices:
        lista.append({
            "i": str(i),
            "tipo": request.POST.get(f"tipo-{i}") or "",
            "natureza": request.POST.get(f"natureza-{i}") or "",
            "cor": request.POST.get(f"cor-{i}") or "",
            "material": (request.POST.get(f"material-{i}") or "").strip(),
            "sel": {int(d) for d in request.POST.getlist(f"dentes-{i}") if d.isdigit()},
            "ficheiros": request.FILES.getlist(f"ficheiros-{i}"),
        })
    return lista


def _validar(dados, trabalhos, e_admin):
    erros = []
    if e_admin and not dados["cliente"]:
        erros.append("Selecione o cliente.")
    if not trabalhos:
        erros.append("Acrescente pelo menos um trabalho.")
    for n, t in enumerate(trabalhos, start=1):
        if not t["tipo"].isdigit():
            erros.append(f"Trabalho {n:02d}: escolha o tipo de trabalho.")
        if t["natureza"] not in ("Físico", "Digital"):
            erros.append(f"Trabalho {n:02d}: indique se é físico ou digital.")
        if not t["sel"]:
            erros.append(f"Trabalho {n:02d}: o odontograma é obrigatório (selecione pelo menos um dente).")
        for f in t["ficheiros"]:
            ext = f.name.rsplit(".", 1)[-1].lower() if "." in f.name else ""
            if ext not in EXTENSOES:
                erros.append(f"Trabalho {n:02d}: o formato de {f.name} não é aceite.")
    if dados["data_nascimento"]:
        try:
            if date.fromisoformat(dados["data_nascimento"]) > date.today():
                erros.append("A data de nascimento não pode ser futura.")
        except ValueError:
            erros.append("Data de nascimento inválida.")
    return erros


@requer_funcionalidade("Criar Encomenda", "Alteração administrativa")
def nova(request):
    e_cliente = bool(request.session.get("id_cliente"))
    e_admin = not e_cliente and tem(request, "Alteração administrativa")
    if not e_cliente and not e_admin:
        messages.error(request, "Não tem permissão para criar encomendas.")
        return redirect("inicio")

    tipos = query("SELECT id_tipo_trabalho, nome FROM tipo_trabalho WHERE ativo ORDER BY nome")
    clientes = query("SELECT id_cliente, nome, nif FROM cliente WHERE ativo ORDER BY nome") if e_admin else []
    campos = ["cliente", "cedula", "paciente", "sexo", "data_nascimento", "data_consulta", "observacoes", "visibilidade"]
    dados = {k: (request.POST.get(k) or "").strip() for k in campos}
    trabalhos = [{"i": "0", "tipo": "", "natureza": "Digital", "cor": "", "material": "", "sel": set(), "ficheiros": []}]

    if request.method == "POST":
        trabalhos = _trabalhos_do_post(request)
        erros = _validar(dados, trabalhos, e_admin)
        if erros:
            for erro in erros:
                messages.error(request, erro)
        else:
            id_cliente = request.session["id_cliente"] if e_cliente else int(dados["cliente"])
            uid = request.session["id_utilizador"]
            visibilidade = "cliente" if e_cliente else (dados["visibilidade"] or "cliente")
            try:
                with como_utilizador(uid):
                    id_paciente = None
                    if dados["paciente"]:
                        id_paciente = execute(
                            "INSERT INTO paciente (nome, data_nascimento, sexo) VALUES (%s, %s, %s) RETURNING id_paciente",
                            [dados["paciente"], dados["data_nascimento"] or None, dados["sexo"] or None])
                    id_medico = None
                    if dados["cedula"]:
                        m = query_one("SELECT id_medico FROM medico WHERE cedula_profissional = %s", [dados["cedula"]])
                        id_medico = m["id_medico"] if m else execute(
                            "INSERT INTO medico (cedula_profissional) VALUES (%s) RETURNING id_medico", [dados["cedula"]])
                    r = chamar("sp_criar_encomenda", id_cliente, uid, [int(t["tipo"]) for t in trabalhos],
                               id_medico, id_paciente, dados["observacoes"] or None, None)
                    id_encomenda = r["p_id_encomenda"]
                    ids = [l["id_encomenda_tipo"] for l in query(
                        "SELECT id_encomenda_tipo FROM encomenda_tipo_trabalho WHERE id_encomenda = %s ORDER BY id_encomenda_tipo",
                        [id_encomenda])]
                    for id_ett, t in zip(ids, trabalhos):
                        execute(
                            """UPDATE encomenda_tipo_trabalho
                               SET natureza = %s, cor = %s, material_a_enviar = %s, data_prevista_consulta = %s
                               WHERE id_encomenda_tipo = %s""",
                            [t["natureza"], t["cor"] or None, t["material"] or None,
                             dados["data_consulta"] or None, id_ett])
                        for dente in sorted(t["sel"]):
                            execute("INSERT INTO odontograma (id_encomenda_tipo, numero_dente) VALUES (%s, %s)",
                                    [id_ett, dente])
                        for f in t["ficheiros"]:
                            guardar(f, id_encomenda, id_ett, uid, visibilidade)
                codigo = query_one("SELECT codigo FROM encomenda WHERE id_encomenda = %s", [id_encomenda])["codigo"]
                messages.success(request, f"Encomenda {codigo} criada. O laboratório foi notificado.")
                return redirect("encomendas:detalhe_cliente" if e_cliente else "encomendas:detalhe", id_encomenda)
            except (DatabaseError, FicheiroInvalido) as exc:
                messages.error(request, mensagem_erro(exc) if isinstance(exc, DatabaseError) else str(exc))

    return render(request, "encomendas/nova.html", {
        "tipos": tipos, "clientes": clientes, "e_admin": e_admin, "dados": dados,
        "trabalhos": trabalhos, "cores": CORES_VITA, "modelo": {"i": "__i__", "natureza": "Digital", "sel": set()},
    })


# ---------------------------------------------------------------------
# Área do cliente (só vê o estado simplificado; as etapas não aparecem)
# ---------------------------------------------------------------------
@requer_cliente
def inicio_cliente(request):
    id_cliente = request.session["id_cliente"]
    contagens = {l["estado"]: l["n"] for l in query(
        """SELECT fn_estado_cliente(est.nome) AS estado, COUNT(*) AS n
           FROM encomenda_tipo_trabalho ett
           JOIN encomenda e               ON e.id_encomenda = ett.id_encomenda
           JOIN estado_encomenda_tipo est ON est.id_estado = ett.id_estado
           WHERE e.id_cliente = %s GROUP BY 1""", [id_cliente])}
    recentes = query(
        """SELECT v.id_encomenda, v.codigo, v.estado, v.data_criacao, v.data_limite, v.n_trabalhos,
                  (SELECT string_agg(tt.nome, ' + ' ORDER BY ett.id_encomenda_tipo)
                   FROM encomenda_tipo_trabalho ett JOIN tipo_trabalho tt ON tt.id_tipo_trabalho = ett.id_tipo_trabalho
                   WHERE ett.id_encomenda = v.id_encomenda) AS tipos
           FROM vw_encomendas_cliente v WHERE v.id_cliente = %s
           ORDER BY v.data_criacao DESC LIMIT 6""", [id_cliente])
    return render(request, "encomendas/inicio_cliente.html", {
        "contagens": [(nome, contagens.get(nome, 0)) for nome in ("Por iniciar", "Em processamento", "Em espera", "Concluído")],
        "recentes": recentes,
    })


@requer_cliente
def minhas(request):
    q = (request.GET.get("q") or "").strip() or None
    linhas = query(
        """SELECT v.id_encomenda, v.codigo, v.estado, v.n_trabalhos,
                  to_char(v.data_criacao, 'DD/MM/YYYY') AS criada,
                  to_char(v.data_limite, 'DD/MM/YYYY')  AS data_limite,
                  pa.nome AS paciente
           FROM vw_encomendas_cliente v
           JOIN encomenda e      ON e.id_encomenda = v.id_encomenda
           LEFT JOIN paciente pa ON pa.id_paciente = e.id_paciente
           WHERE v.id_cliente = %s
             AND (%s::TEXT IS NULL OR v.codigo ILIKE '%%' || %s || '%%' OR pa.nome ILIKE '%%' || %s || '%%')
           ORDER BY v.data_criacao DESC""",
        [request.session["id_cliente"], q, q, q],
    )
    return render(request, "core/lista.html", {
        "titulo": "As minhas encomendas",
        "colunas": [("codigo", "Encomenda"), ("paciente", "Paciente"), ("estado", "Estado"),
                    ("n_trabalhos", "Trabalhos"), ("criada", "Criada"), ("data_limite", "Data limite")],
        "linhas": linhas, "mono": ["codigo", "criada", "data_limite"], "estado": ["estado"],
        "link": {"url": "encomendas:detalhe_cliente", "chave": "id_encomenda"},
        "pesquisa": "Pesquisar por código de encomenda ou paciente",
        "vazio": "Ainda não fez encomendas.",
    })


@requer_cliente
def detalhe_cliente(request, id_encomenda):
    e = _encomenda_ou_404(request, id_encomenda)
    uid = request.session["id_utilizador"]
    trabalhos = consultas.trabalhos(id_encomenda)
    for t in trabalhos:
        t["sel"] = lista_dentes(t["dentes"])
    return render(request, "encomendas/detalhe_cliente.html", {
        "e": e, "trabalhos": trabalhos,
        "notas": consultas.notas(id_encomenda=id_encomenda, so_cliente=True, id_utilizador_cliente=uid),
        "anexos": consultas.anexos(id_encomenda=id_encomenda, so_cliente=True, id_utilizador_cliente=uid),
        "extensoes": ", ".join(sorted(EXTENSOES)),
    })
