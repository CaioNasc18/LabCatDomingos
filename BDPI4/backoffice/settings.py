"""
Configuração do backoffice — LAB Catarina Domingos (PI IV).

Os dados sensíveis (ligação à BD, SECRET_KEY) vêm de variáveis de ambiente.
Em desenvolvimento são lidos do ficheiro .env (ver .env.example).
No Render/Vercel definem-se nas definições do serviço.
"""
import os
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-apenas-local-trocar-em-producao")
DEBUG = os.environ.get("DEBUG", "True") == "True"
if not DEBUG and SECRET_KEY == "dev-apenas-local-trocar-em-producao":
    raise RuntimeError("Falta definir SECRET_KEY nas variáveis de ambiente.")
ALLOWED_HOSTS = [h for h in os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h]


INSTALLED_APPS = [
    # sem ORM: nenhuma app do Django que precise de tabelas próprias (migrate)
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",          # BD (db.py), login e permissões, base dos templates
    "dashboard",     # Dashboard geral
    "encomendas",    # Todas as encomendas, aceitar, alterar estado; encomendas do cliente
    "trabalhos",     # Trabalhos atribuídos e disponíveis, assumir e concluir etapas
    "gestao",        # Clientes, colaboradores, utilizadores, tipos de trabalho, etapas, permissões
    "logs",          # Logs (auditoria)
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",   # serve o CSS/JS em produção (Render)
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Sessões guardadas num cookie assinado: não é preciso criar tabelas do Django
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"

ROOT_URLCONF = "backoffice.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.backoffice",   # menu por permissões + notificações por ler
            ],
        },
    },
]

WSGI_APPLICATION = "backoffice.wsgi.application"


# ---------------------------------------------------------------------
# Base de dados — Neon (PostgreSQL na cloud)
# DATABASE_URL é a connection string copiada do painel do Neon:
#   postgresql://utilizador:password@ep-xxxx.region.aws.neon.tech/neondb?sslmode=require
# ---------------------------------------------------------------------
def _db_config(url):
    u = urlparse(url)
    opcoes = {k: v[0] for k, v in parse_qs(u.query).items()}
    opcoes.setdefault("sslmode", "require")   # o Neon obriga a SSL
    opcoes.pop("channel_binding", None)       # parâmetro que o Neon junta; não é preciso
    config = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": u.path.lstrip("/"),
        "USER": unquote(u.username or ""),
        "PASSWORD": unquote(u.password or ""),
        "HOST": u.hostname,
        "PORT": str(u.port or 5432),
        "OPTIONS": opcoes,
        "CONN_MAX_AGE": 60,
        "CONN_HEALTH_CHECKS": True,
    }
    # host "-pooler" (ligação partilhada, ex. na Vercel): o PgBouncer do Neon
    # não suporta cursores do lado do servidor
    if "-pooler" in (u.hostname or ""):
        config["DISABLE_SERVER_SIDE_CURSORS"] = True
        config["CONN_MAX_AGE"] = 0
    return config


DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("Falta DATABASE_URL. Copia .env.example para .env e cola a connection string do Neon.")

DATABASES = {"default": _db_config(DATABASE_URL)}


LANGUAGE_CODE = "pt-pt"
TIME_ZONE = "Europe/Lisbon"
USE_I18N = True
USE_TZ = False  # as colunas são TIMESTAMP sem fuso horário

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"   # python manage.py collectstatic (só em produção)

# Fotografias e ficheiros das encomendas.
# Em desenvolvimento ficam na pasta media/. No Render o disco é temporário:
# em produção têm de ir para o armazenamento S3 previsto na arquitetura.
MEDIA_ROOT = Path(os.environ.get("MEDIA_ROOT", BASE_DIR / "media"))
TAMANHO_MAXIMO_FICHEIRO = 250 * 1024 * 1024        # 250 MB, como no protótipo

# Render: o HTTPS termina no proxy do Render
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CSRF_TRUSTED_ORIGINS = [
    f"https://*{h}" if h.startswith(".") else f"https://{h}"
    for h in ALLOWED_HOSTS if h not in ("localhost", "127.0.0.1")
]
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
