"""
Cria o primeiro administrador (utilizador + administrador) em SQL direto.
Uso: python manage.py criar_admin --nome "Catarina Domingos" --email admin@lab.pt --password ...
"""
from django.core.management.base import BaseCommand, CommandError

from core.auth import hash_password
from core.db import atomic, execute, query_one, registar_log


class Command(BaseCommand):
    help = "Cria um utilizador com perfil Administrador"

    def add_arguments(self, parser):
        parser.add_argument("--nome", required=True)
        parser.add_argument("--email", required=True)
        parser.add_argument("--password", required=True)

    def handle(self, *args, **o):
        if query_one("SELECT 1 FROM utilizador WHERE email = %s", [o["email"]]):
            raise CommandError("Já existe um utilizador com esse email.")

        with atomic():
            id_utilizador = execute(
                """INSERT INTO utilizador (id_perfil, nome, email, password_hash)
                   SELECT id_perfil, %s, %s, %s FROM perfil WHERE nome = 'Administrador'
                   RETURNING id_utilizador""",
                [o["nome"], o["email"], hash_password(o["password"])],
            )
            execute("INSERT INTO administrador (id_utilizador) VALUES (%s)", [id_utilizador])
            registar_log(id_utilizador, "Criar administrador", "utilizador", id_utilizador)

        self.stdout.write(self.style.SUCCESS(f"Administrador criado (id {id_utilizador})."))
