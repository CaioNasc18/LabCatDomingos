import unicodedata

from django import template

register = template.Library()


@register.filter
def obter(linha, chave):
    """{{ linha|obter:"coluna" }} — valor de uma coluna numa linha (dicionário)."""
    return linha.get(chave)


@register.filter
def estado_css(estado):
    """'Em processamento' -> 'em-processamento' (classe da cor do estado)."""
    if not estado:
        return ""
    s = unicodedata.normalize("NFKD", str(estado)).encode("ascii", "ignore").decode()
    return s.lower().replace(" ", "-")


@register.filter
def dias(n):
    """Texto do prazo a partir dos dias que faltam."""
    if n is None:
        return ""
    if n < 0:
        return f"{-n} dia{'s' if n != -1 else ''} em atraso"
    if n == 0:
        return "termina hoje"
    if n == 1:
        return "termina amanhã"
    return f"faltam {n} dias"


@register.filter
def prazo_css(n):
    if n is None:
        return ""
    if n < 0:
        return "prazo-atraso"
    if n <= 3:
        return "prazo-proximo"
    return ""


@register.filter
def duracao(td):
    if td is None:
        return ""
    minutos = int(td.total_seconds() // 60)
    h, m = divmod(minutos, 60)
    d, h = divmod(h, 24)
    if d:
        return f"{d} d {h} h"
    return f"{h} h {m:02d} min" if h else f"{m} min"


@register.filter
def tamanho(n):
    if not n:
        return ""
    for unidade in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f} {unidade}" if unidade == "B" else f"{n:.1f} {unidade}"
        n /= 1024
    return f"{n:.1f} TB"


@register.simple_tag
def dentes_fdi():
    """Quadrantes do odontograma (notação FDI), na ordem em que aparecem na boca."""
    return {
        "superior": [list(range(18, 10, -1)), list(range(21, 29))],
        "inferior": [list(range(48, 40, -1)), list(range(31, 39))],
    }


@register.filter
def lista_dentes(texto):
    """'11, 12' -> {11, 12}"""
    if not texto:
        return set()
    return {int(x) for x in str(texto).replace(" ", "").split(",") if x}
