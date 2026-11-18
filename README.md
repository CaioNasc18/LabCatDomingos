# Base de dados — LAB Catarina Domingos (PI IV)

PostgreSQL no **Neon** + Django em SQL direto (sem ORM, sem migrações).

## Scripts SQL (correr por esta ordem)

| Script | Conteúdo | Quando correr |
| --- | --- | --- |
| `01_schema.sql` | as 25 tabelas, chaves, restrições e índices | só numa BD vazia (apaga tudo) |
| `02_seed.sql` | perfis, estados, funcionalidades, permissões, tipos de trabalho, processos e etapas | logo a seguir ao 01 |
| `03_alteracoes_feedback.sql` | feedback da aula: material removido, notas por utilizador, administradores como colaboradores | **uma vez** em cada branch |
| `04_logica.sql` | funções, procedimentos, triggers e vistas (Ficha 8) | depois do 03; pode ser corrido de novo |
| `05_backoffice.sql` | o que o backoffice precisa: encaminhar com próxima etapa, faturação/envio só depois de concluído, notificações de pedidos e notas, vistas de pedidos e trabalhos realizados | depois do 04; pode ser corrido de novo |

No Neon, onde as tabelas já existem (`dev` e `production`): correr os scripts que ainda não correram, por ordem
(ex.: se já correram o 03 e o 04, correr **só o 05**). Se voltarem a correr o 04, corram o 05 a seguir.

Correr no **SQL Editor** do Neon (colar o script → Run) ou no pgAdmin ligado ao Neon
(host do Neon, porta `5432`, base de dados `neondb`, SSL mode `require`).
Fazer primeiro no branch `dev` e só depois no `production`.

Verificação depois do 05:

```sql
SELECT (SELECT count(*) FROM pg_proc WHERE proname LIKE 'fn\_%' OR proname LIKE 'sp\_%') AS funcoes_e_procedimentos,
       (SELECT count(*) FROM pg_views WHERE viewname LIKE 'vw\_%')                       AS vistas,
       (SELECT count(DISTINCT tgname) FROM pg_trigger WHERE tgname LIKE 'trg\_%')         AS triggers;
-- esperado: 21 funções e procedimentos, 9 vistas, 8 triggers
```

### O que o 04 e o 05 criam

- **Funções:** `fn_gerar_codigo_encomenda`, `fn_idade`, `fn_estado_cliente`, `fn_estado_encomenda_calculado`,
  `fn_tem_funcionalidade`, `fn_ordem_estado`, `fn_id_estado_tipo`, `fn_utilizador_atual`
- **Procedimentos:** `sp_criar_encomenda`, `sp_aceitar_encomenda`, `sp_assumir_etapa`, `sp_concluir_etapa`,
  `sp_alterar_estado_trabalho`
- **Triggers:** `trg_auditoria` (logs em 11 tabelas), `trg_admin_colaborador`, `trg_validar_estado_trabalho`,
  `trg_historico_estado`, `trg_estado_encomenda`, `trg_validar_execucao`;
  no 05, `trg_notificar_novo_pedido` e `trg_notificar_nota`
- **Vistas:** `vw_colaboradores`, `vw_encomendas_cliente`, `vw_trabalhos_cliente`, `vw_trabalhos_atribuidos`,
  `vw_trabalhos_disponiveis`, `vw_dashboard`, `vw_logs`; no 05, `vw_pedidos_por_aceitar` e `vw_trabalhos_realizados`
- **05 altera:** `sp_assumir_etapa` (faturação e envio final só depois de concluído) e `sp_concluir_etapa`
  (passa a receber a próxima etapa e notifica o colaborador para quem o trabalho é encaminhado)

Exemplo:

```sql
CALL sp_criar_encomenda(1, 3, ARRAY[1, 8], NULL, NULL, 'Urgente', NULL);   -- cliente 1, criada pelo utilizador 3
CALL sp_aceitar_encomenda(1, '2026-12-01 18:00', 1);
SELECT * FROM vw_encomendas_cliente;
```

`CALL` não aceita subconsultas nos argumentos: passar valores diretos.

## Django

```bash
cd django
python -m venv venv
venv\Scripts\activate            # PowerShell: .\venv\Scripts\Activate.ps1   Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env           # Linux/Mac: cp .env.example .env
```

No `.env`: `DATABASE_URL` = connection string do Neon (branch `dev`, **sem** "Connection pooling")
e uma `SECRET_KEY` gerada com `python -c "import secrets; print(secrets.token_urlsafe(50))"`.

```bash
python manage.py check
python manage.py criar_admin --nome "Catarina Domingos" --email admin@lab.pt --password "UmaPass#Forte"
python manage.py runserver
```

**Não correr `makemigrations` nem `migrate`**: as tabelas são criadas pelos scripts SQL.

### Backoffice

Menu lateral construído a partir das permissões do perfil (capítulo 3.2.2), identidade preto/dourado com variante
clara (botão no topo), Inter e IBM Plex Mono para códigos e datas, uma cor por estado.

| Zona | Páginas | Perfil |
| --- | --- | --- |
| Painel | Dashboard: indicadores, prazos próximos e em atraso, pedidos por aceitar, os meus trabalhos | Administrador |
| Encomendas | Pedidos por aceitar · Todas as encomendas (filtro por estado e pesquisa) · Nova encomenda em nome do cliente · Detalhe em separadores: resumo, etapas, notas, fotografias e ficheiros, histórico | Administrador |
| Execução | Os meus trabalhos (em curso e encaminhados) · Trabalhos disponíveis · Trabalhos realizados · Trabalho: assumir etapa, finalizar e encaminhar, colocar em espera, retomar, concluir, notas, fotografias | Administrador e colaborador |
| Gestão | Clientes (criar, editar, ativar) · Colaboradores (criar, ativar) · Utilizadores (repor palavra-passe, ativar) · Tipos de trabalho com processo e etapas | Administrador |
| Sistema | Permissões (matriz perfil × funcionalidade) · Logs (filtros por tabela, ação e utilizador) | Administrador |
| Área do cliente | Início · Nova encomenda (odontograma, cor VITA, ficheiros) · As minhas encomendas · Detalhe só com o estado simplificado, notas e ficheiros visíveis | Cliente |

Em todos os perfis: notificações (sino no topo) e conta (dados e alterar palavra-passe).

| App | Usa |
| --- | --- |
| `core` | `db.py` (SQL direto, `chamar`, `como_utilizador`), `auth.py` (login e permissões), `consultas.py`, `ficheiros.py`, menu, notificações, conta |
| `dashboard` | `vw_dashboard`, `vw_pedidos_por_aceitar`, `vw_trabalhos_atribuidos` |
| `encomendas` | `sp_criar_encomenda`, `sp_aceitar_encomenda`, `sp_alterar_estado_trabalho`, `vw_encomendas_cliente`, `vw_pedidos_por_aceitar` |
| `trabalhos` | `sp_assumir_etapa`, `sp_concluir_etapa`, `sp_alterar_estado_trabalho`, `vw_trabalhos_atribuidos`, `vw_trabalhos_disponiveis`, `vw_trabalhos_realizados` |
| `gestao` | `vw_colaboradores`, `perfil_funcionalidade`, tipos, processos e etapas |
| `logs` | `vw_logs` |

Os erros dos procedimentos (`RAISE EXCEPTION`) aparecem ao utilizador como mensagem. Para um
`INSERT`/`UPDATE`/`DELETE` feito diretamente no Django ficar nos logs com o nome de quem o fez:

```python
with como_utilizador(request.session["id_utilizador"]):
    execute("UPDATE cliente SET ativo = NOT ativo WHERE id_cliente = %s", [id_cliente])
```

**Fotografias e ficheiros:** em desenvolvimento ficam na pasta `django/media/` (não vai para o GitHub).
No Render o disco é temporário, por isso em produção têm de passar para o armazenamento S3 previsto na
arquitetura; o único sítio a mudar é `core/ficheiros.py`.

### Regras para o grupo

- O `.env` tem a password da BD: **nunca vai para o GitHub**.
- Cada um desenvolve no branch `dev` do Neon; o `production` é a versão estável.
- Ninguém altera tabelas à mão no Neon: só através de scripts SQL numerados no repositório.

### Em produção (Render ou Vercel)

Variáveis de ambiente: `DATABASE_URL` (branch `production`), `SECRET_KEY` (nova), `DEBUG=False`, `ALLOWED_HOSTS`.
Comando de arranque: `python manage.py collectstatic --noinput && gunicorn backoffice.wsgi` (o CSS é servido pelo WhiteNoise).
Render: connection string sem `-pooler`. Vercel: com `-pooler` (o `settings.py` ajusta-se sozinho).
