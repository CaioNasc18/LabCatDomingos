"""
Menu lateral construído a partir das permissões do perfil autenticado:
cada entrada corresponde a uma funcionalidade e só aparece se o perfil a tiver.
Zonas do administrador: Painel, Encomendas, Execução, Gestão, Sistema (capítulo 3.2.2).
"""
from django.urls import reverse

from .db import query_one

# (zona, [(rótulo, nome do url, funcionalidades que dão acesso)])
MENU_LABORATORIO = [
    ("Painel", [
        ("Dashboard", "dashboard", ["Dashboard geral"]),
    ]),
    ("Encomendas", [
        ("Pedidos por aceitar", "encomendas:pedidos", ["Alteração administrativa"]),
        ("Todas as encomendas", "encomendas:lista", ["Todas as Encomendas"]),
        ("Nova encomenda", "encomendas:nova", ["Alteração administrativa"]),
    ]),
    ("Execução", [
        ("Os meus trabalhos", "trabalhos:meus", ["Executar trabalho"]),
        ("Trabalhos disponíveis", "trabalhos:disponiveis", ["Assumir trabalho", "Consultar Encomendas disponíveis"]),
        ("Trabalhos realizados", "trabalhos:realizados", ["Executar trabalho"]),
    ]),
    ("Gestão", [
        ("Clientes", "gestao:clientes", ["Gestão de clientes"]),
        ("Colaboradores", "gestao:colaboradores", ["Gestão de colaboradores"]),
        ("Utilizadores", "gestao:utilizadores", ["Gestão de utilizadores"]),
        ("Tipos de trabalho", "gestao:tipos", ["Gestão de Tipos de Trabalho", "Gestão de Processos", "Gestão de Etapas"]),
    ]),
    ("Sistema", [
        ("Permissões", "gestao:permissoes", ["Gestão de permissões"]),
        ("Logs", "logs:lista", ["Logs"]),
    ]),
]

MENU_CLIENTE = [
    ("Área do cliente", [
        ("Início", "encomendas:inicio_cliente", ["Consultar Encomendas"]),
        ("Nova encomenda", "encomendas:nova", ["Criar Encomenda"]),
        ("As minhas encomendas", "encomendas:minhas", ["Consultar Encomendas"]),
    ]),
]


def _construir(menu, funcs, caminho):
    zonas = []
    for zona, itens in menu:
        visiveis = []
        for rotulo, url_nome, precisa in itens:
            if any(p in funcs for p in precisa):
                url = reverse(url_nome)
                ativo = caminho == url or (url != "/" and caminho.startswith(url) and url_nome != "encomendas:nova")
                visiveis.append({"rotulo": rotulo, "url": url, "ativo": ativo})
        if visiveis:
            zonas.append({"nome": zona, "itens": visiveis})
    # só um item ativo: o de url mais comprido
    ativos = [i for z in zonas for i in z["itens"] if i["ativo"]]
    if len(ativos) > 1:
        melhor = max(ativos, key=lambda i: len(i["url"]))
        for i in ativos:
            i["ativo"] = i is melhor
    return zonas


def backoffice(request):
    s = getattr(request, "session", None)
    if not s or "id_utilizador" not in s:
        return {}
    funcs = s.get("funcionalidades", [])
    menu = _construir(MENU_CLIENTE if s.get("id_cliente") else MENU_LABORATORIO, funcs, request.path)
    por_ler = query_one(
        "SELECT COUNT(*) AS n FROM notificacao WHERE id_utilizador = %s AND NOT lida",
        [s["id_utilizador"]],
    )["n"]
    return {"menu": menu, "notificacoes_por_ler": por_ler}
