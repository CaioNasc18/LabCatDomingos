"""
Fotografias e ficheiros técnicos das encomendas.

Em desenvolvimento são guardados em MEDIA_ROOT (pasta media/); a BD guarda só o caminho.
Em produção (Render) o disco é temporário: estas duas funções são o único sítio a
mudar para passar ao armazenamento S3 previsto na arquitetura.
"""
import mimetypes
import re
import uuid
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404

from .db import execute

EXTENSOES_FOTO = {"jpg", "jpeg", "png", "webp", "heic"}
EXTENSOES_FICHEIRO = {"stl", "ply", "obj", "dcm", "dicom", "pdf", "zip"}
EXTENSOES = EXTENSOES_FOTO | EXTENSOES_FICHEIRO


class FicheiroInvalido(ValueError):
    pass


def _nome_seguro(nome):
    nome = Path(nome).name
    nome = re.sub(r"[^A-Za-z0-9._-]+", "_", nome).strip("._") or "ficheiro"
    return nome[:120]


def guardar(upload, id_encomenda, id_encomenda_tipo, id_utilizador, visibilidade):
    """Grava o ficheiro em disco e regista-o em fotografia ou ficheiro. Devolve o tipo."""
    ext = Path(upload.name).suffix.lower().lstrip(".")
    if ext not in EXTENSOES:
        raise FicheiroInvalido(f"Formato .{ext or '?'} não aceite. Use STL, PLY, OBJ, DICOM, PDF, ZIP, JPG ou PNG.")
    if upload.size > settings.TAMANHO_MAXIMO_FICHEIRO:
        raise FicheiroInvalido("O ficheiro excede o limite de 250 MB.")
    if visibilidade not in ("interna", "cliente"):
        visibilidade = "interna"

    relativo = Path("encomendas") / str(id_encomenda) / f"{uuid.uuid4().hex[:8]}_{_nome_seguro(upload.name)}"
    destino = Path(settings.MEDIA_ROOT) / relativo
    destino.parent.mkdir(parents=True, exist_ok=True)
    with open(destino, "wb") as f:
        for bloco in upload.chunks():
            f.write(bloco)

    if ext in EXTENSOES_FOTO:
        execute(
            """INSERT INTO fotografia (id_encomenda_tipo, id_utilizador, ficheiro_path, visibilidade, tamanho_ficheiro)
               VALUES (%s, %s, %s, %s, %s)""",
            [id_encomenda_tipo, id_utilizador, relativo.as_posix(), visibilidade, upload.size],
        )
        return "fotografia"
    execute(
        """INSERT INTO ficheiro (id_encomenda_tipo, id_utilizador, tipo_ficheiro, ficheiro_path, visibilidade, tamanho_ficheiro)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        [id_encomenda_tipo, id_utilizador, ext.upper(), relativo.as_posix(), visibilidade, upload.size],
    )
    return "ficheiro"


def nome_original(caminho):
    """encomendas/3/ab12cd34_scan.stl -> scan.stl"""
    base = Path(caminho).name
    return base.split("_", 1)[1] if "_" in base else base


def enviar(caminho, descarregar=True):
    destino = (Path(settings.MEDIA_ROOT) / caminho).resolve()
    if Path(settings.MEDIA_ROOT).resolve() not in destino.parents or not destino.is_file():
        raise Http404("Ficheiro não encontrado.")
    tipo, _ = mimetypes.guess_type(destino.name)
    return FileResponse(open(destino, "rb"), as_attachment=descarregar,
                        filename=nome_original(caminho), content_type=tipo or "application/octet-stream")
