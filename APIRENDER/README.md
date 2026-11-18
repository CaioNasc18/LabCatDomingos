# API — Laboratório Catarina Domingos (PI IV)

Node.js + Express, ligada ao PostgreSQL do Neon. Para pôr no Render.
Usa as tabelas, procedimentos, triggers e vistas dos scripts `01` a `05`,
por isso as regras de negócio ficam na base de dados, iguais às do backoffice.

As rotas estão em [API.md](API.md). Para testar, importar `postman_colecao.json` no Postman.

## Estrutura

```
src/
  servidor.js       arranque do Express, erros
  bd.js             ligação ao Neon (DATABASE_URL), transações
  autenticacao.js   JWT + permissões (perfil_funcionalidade)
  passwords.js      verificação de password_hash (Django, bcrypt ou salt:hash)
  rotas/
    sessao.js       POST /login/, DELETE /logout/
    sync.js         GET /sync/
    encomendas.js   POST /encomendas/
    trabalhos.js    assumir, concluir etapa, estado, notas, notificações
scripts/
  dados_teste.js    utilizadores de teste + 1 encomenda aceite
```

## 1. Correr no computador

Precisa do Node 20 ou mais recente.

```bash
npm install
cp .env.exemplo .env      # e preencher DATABASE_URL e JWT_SEGREDO
npm run dados-teste       # só na primeira vez (cria os utilizadores de teste)
npm start                 # http://localhost:3000
```

A `DATABASE_URL` está no Neon, em **Dashboard › Connect › Connection string**.
Usem um branch de desenvolvimento (`dev`) para os testes, não o de produção.

## 2. Pôr no Render

1. Criar um repositório no GitHub com esta pasta. O `.gitignore` já deixa de fora o `.env` e o `node_modules`.
2. No Render, ir a **New › Web Service** e escolher o repositório.
   - Runtime: **Node**
   - Build Command: `npm install`
   - Start Command: `npm start`
   - Instance Type: Free
3. Em **Environment**, acrescentar:
   - `DATABASE_URL`, com a connection string do Neon (branch de produção)
   - `JWT_SEGREDO`, com um texto longo e aleatório
   - `JWT_VALIDADE` (opcional), por omissão `7d`
4. Depois do deploy, abrir `https://<nome>.onrender.com/`. Deve aparecer `{"estado":"ok","bd":"ok"}`.
5. Na app Flutter, pôr esse endereço em `urlRender`, no ficheiro `lib/servicos/servidor.dart`.

No plano gratuito, o serviço adormece depois de 15 minutos sem pedidos e o primeiro pedido demora 30 a 60 segundos.
Antes de uma apresentação, abram o endereço `/` para o acordar.

## Utilizadores e passwords

A API lê a tabela `utilizador`. O formato oficial é o do Django, o mesmo que o backoffice grava com `make_password`:

```
pbkdf2_sha256$1500000$<salt>$<hash base64>
```

- As iterações são lidas do próprio hash, porque mudam com a versão do Django. Os utilizadores criados no backoffice entram sempre na app.
- Quando a API cria passwords (por agora, só o `dados-teste`), usa este mesmo formato, com 1 500 000 iterações (Django 6.1). Assim, o backoffice também as aceita.
- bcrypt e `salt:hash` só são aceites ao fazer login, para compatibilidade. A API nunca os grava, porque o `check_password` do Django não os reconhece.
- Um login demora perto de 1 segundo, por causa das 1 500 000 iterações. O cálculo é assíncrono, para não bloquear os outros pedidos.

O `npm run dados-teste` cria estes utilizadores, todos com a password `password123` e em formato Django (o backoffice aceita o mesmo hash):

| Perfil | Email |
|---|---|
| Administrador (também é colaborador) | admin1@laboratorio.pt |
| Colaborador | colaborador1@laboratorio.pt |
| Cliente (Clínica Dente) | cliente1@exemplo.pt |

## O que fica para depois

- **Fotografias e STL (upload e download):** é preciso o bucket S3 (Cloudflare R2). Por agora, o `/sync/` só devolve os registos que já existem nas tabelas `ficheiro` e `fotografia`.
- **Notificações push (Firebase):** as notificações já são criadas pelos triggers e vão no `/sync/`. Falta o envio push.
- **Logout:** os tokens terminados ficam guardados na memória do servidor. Quando o Render reinicia, um token antigo volta a valer até expirar (7 dias). Para ser permanente, é preciso uma tabela na BD.
- **`/sync/` incremental (`desde`):** cada pedido devolve tudo, o que chega para o tamanho do laboratório.
- **Swagger/OpenAPI:** o contrato está em API.md e pode passar para `openapi.yaml`.
