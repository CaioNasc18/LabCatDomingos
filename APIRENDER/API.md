# Rotas da API

Base: `https://<nome>.onrender.com` (ou `http://localhost:3000`)

Corpo e respostas em JSON. Todas as rotas, exceto `/` e `/login/`, precisam do cabeçalho
`Authorization: Bearer <token>`.

Erros: `{"erro": "mensagem"}`, com estes códigos:
- **400**: dados inválidos ou regra de negócio da BD (por exemplo, "A encomenda ainda não foi aceite.");
- **401**: sem token ou token inválido;
- **403**: sem permissão;
- **404**: não encontrado.

As permissões vêm da tabela `perfil_funcionalidade` (funcionalidades "Mobile").

| Método | Rota | Quem | Funcionalidade |
|---|---|---|---|
| GET | `/` | todos | — (estado da API e da BD) |
| POST | `/login/` | todos | — |
| DELETE | `/logout/` | com sessão | — |
| GET | `/sync/` | cliente, colaborador, administrador | — |
| POST | `/encomendas/` | cliente, administrador | Criar Encomenda |
| POST | `/trabalhos/:id/assumir` | colaborador, administrador | Assumir trabalho |
| POST | `/execucoes/:id/concluir` | quem assumiu a etapa | Executar trabalho |
| POST | `/trabalhos/:id/estado` | colaborador, administrador | Alterar situação do trabalho |
| POST | `/trabalhos/:id/notas` | colaborador (Notas) ou cliente (nos seus trabalhos) | Notas |
| POST | `/notificacoes/lidas` | com sessão | — |

`:id` de um trabalho = `id_encomenda_tipo` (tabela `encomenda_tipo_trabalho`).

---

## POST /login/

```json
{ "email": "cliente1@exemplo.pt", "password": "password123" }
```

Resposta 200 (mesmo formato da Aula 9):

```json
{
  "token": "eyJhbGciOi...",
  "utilizador_id": 3,
  "nome": "Clínica Dente",
  "perfil": "cliente",
  "cliente_id": 1
}
```

`perfil` é `administrador`, `colaborador` ou `cliente`. `cliente_id` só vem preenchido para clientes.

## DELETE /logout/

Resposta 204. A partir daí, o token deixa de ser aceite.

## GET /sync/

Devolve sempre todas as secções, mesmo vazias (`[]`).

| Secção | Cliente | Colaborador / administrador |
|---|---|---|
| `clientes` | só o seu | todos os ativos |
| `encomendas` | só as suas; estado simplificado; sem `data_aceitacao` | todas, com o estado real |
| `trabalhos` | só os seus; estado simplificado | todos |
| `pacientes` | os das suas encomendas (`idade`, não a data de nascimento) | todos |
| `medicos` | os das suas encomendas | todos |
| `trabalho_dentes` | dentes (FDI) dos seus trabalhos | todos |
| `tipos_trabalho` | ativos | ativos |
| `etapas` | `[]` | etapas do processo ativo de cada tipo |
| `execucoes` | `[]` | todas (quem, quando, etapa seguinte) |
| `colaboradores` | `[]` | ativos, incluindo os administradores |
| `trabalhos_disponiveis` | `[]` | `vw_trabalhos_disponiveis` |
| `trabalhos_atribuidos` | `[]` | `vw_trabalhos_atribuidos` do próprio |
| `notas` | as visíveis ao cliente e as que escreveu | todas |
| `ficheiros` | os visíveis ao cliente e os que enviou | todos (ficheiros e fotografias) |
| `notificacoes` | as suas | as suas |
| `servidor_em` | hora do servidor (UTC) | |
| `eu` | dados do utilizador autenticado | |

Estados que o cliente vê (`fn_estado_cliente`):
- Em avaliação → **Por iniciar**
- Por iniciar, Em processamento e Em prova → **Em processamento**
- Em espera → **Em espera**
- Concluído e Entregue → **Concluído**

Exemplo de uma linha de `trabalhos`:

```json
{
  "id_encomenda_tipo": 1, "id_encomenda": 1, "codigo": "ENC-2026-0001",
  "id_tipo_trabalho": 1, "tipo_trabalho": "Coroa Zr.", "estado": "Em processamento",
  "natureza": "Físico", "cor": "A2", "material_a_enviar": null,
  "data_prevista_consulta": null, "notas": null, "id_paciente": 1,
  "data_limite": "2026-11-28 11:02:38.703162"
}
```

## POST /encomendas/

```json
{
  "paciente": { "nome": "João Silva", "idade": 40, "sexo": "M" },
  "cedula_medico": "C-1234",
  "observacoes": "Nota extra da clínica",
  "trabalhos": [
    { "id_tipo_trabalho": 1, "natureza": "Físico", "cor": "A2",
      "material_a_enviar": "Moldagem", "data_prevista_consulta": "2026-12-01",
      "notas": "", "dentes": [11, 21] }
  ]
}
```

- O cliente cria sempre para si. O administrador tem de indicar também `"id_cliente": <n>`.
- Em vez de `idade`, pode enviar-se `data_nascimento` (`"1986-05-02"`).
- `natureza` é `"Físico"` ou `"Digital"`.

Resposta 201:

```json
{ "id_encomenda": 2, "codigo": "ENC-2026-0002", "trabalhos": [3] }
```

A encomenda fica "Em avaliação" e os administradores recebem uma notificação (trigger).

## POST /trabalhos/:id/assumir

```json
{ "id_etapa": 1 }
```

Resposta 201: `{ "id_execucao": 1 }`. Chama `sp_assumir_etapa`. A BD recusa quando:
- a encomenda ainda não foi aceite;
- o trabalho está em espera;
- é Faturação ou envio final antes de o trabalho estar concluído;
- a etapa é de outro processo;
- a etapa já está em curso.

## POST /execucoes/:id/concluir

Encaminhar para um colega (ou para o administrador):

```json
{ "id_colaborador_seguinte": 1, "id_etapa_seguinte": 2, "observacoes": "Segue para impressão" }
```

Deixar o trabalho disponível: enviar `{}` ou só `observacoes`.

Chama `sp_concluir_etapa`. Só quem assumiu a etapa a pode concluir. Concluir
"Embalamento e envio final" entrega o trabalho, se as etapas obrigatórias estiverem feitas.

## POST /trabalhos/:id/estado

```json
{ "estado": "Em espera", "justificacao": "Falta o modelo" }
```

O `estado` pode ser:
- `"Em espera"` (a justificação é obrigatória);
- `"Em processamento"` (retomar);
- `"Concluído"` (a qualquer momento).

Chama `sp_alterar_estado_trabalho`. O histórico e a notificação ao cliente são feitos pelos triggers.

## POST /trabalhos/:id/notas

```json
{ "conteudo": "Modelo com bolha", "visibilidade": "interna" }
```

- **Colaborador:** `visibilidade` é `"interna"` (por omissão) ou `"cliente"`.
- **Cliente:** só nos seus trabalhos, e a nota fica sempre visível para ele. Os administradores são notificados.

## POST /notificacoes/lidas

- `{}` marca todas as notificações como lidas.
- `{ "ids": [4, 5] }` marca só essas.

Resposta: `{ "marcadas": 2 }`
