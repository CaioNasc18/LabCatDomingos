// JWT + RBAC: o token identifica o utilizador; as permissões vêm da
// matriz perfil_funcionalidade da base de dados (fn_tem_funcionalidade).
const crypto = require('crypto');
const jwt = require('jsonwebtoken');
const { consulta } = require('./bd');

const SEGREDO = process.env.JWT_SEGREDO;
if (!SEGREDO) {
  throw new Error('Falta a variável de ambiente JWT_SEGREDO (ver .env.exemplo).');
}
const VALIDADE = process.env.JWT_VALIDADE || '7d';

// Tokens terminados com /logout/ (em memória: limpa-se ao reiniciar o servidor,
// e nessa altura os tokens antigos continuam válidos até expirarem).
const terminados = new Set();

function criarToken(utilizador) {
  return jwt.sign(
    { sub: utilizador.id_utilizador, perfil: utilizador.perfil, jti: crypto.randomUUID() },
    SEGREDO,
    { expiresIn: VALIDADE },
  );
}

// Aceita "Authorization: Bearer <token>" (e "Token <token>", como na Aula 9)
async function exigeLogin(req, res, next) {
  const cabecalho = req.headers.authorization || '';
  const [, token] = cabecalho.match(/^(?:Bearer|Token)\s+(.+)$/i) || [];
  if (!token) {
    return res.status(401).json({ erro: 'Falta o token (Authorization: Bearer <token>).' });
  }

  let dados;
  try {
    dados = jwt.verify(token, SEGREDO);
  } catch (e) {
    return res.status(401).json({ erro: 'Token inválido ou expirado.' });
  }
  if (terminados.has(dados.jti)) {
    return res.status(401).json({ erro: 'Sessão terminada.' });
  }

  const { rows } = await consulta(
    `SELECT u.id_utilizador, u.nome, u.email, lower(p.nome) AS perfil,
            c.id_cliente, col.id_colaborador
     FROM   utilizador u
     JOIN   perfil p           ON p.id_perfil = u.id_perfil
     LEFT   JOIN cliente c     ON c.id_utilizador = u.id_utilizador AND c.ativo
     LEFT   JOIN colaborador col ON col.id_utilizador = u.id_utilizador AND col.ativo
     WHERE  u.id_utilizador = $1 AND u.ativo`,
    [dados.sub],
  );
  if (rows.length === 0) {
    return res.status(401).json({ erro: 'Utilizador inexistente ou inativo.' });
  }

  req.utilizador = rows[0];
  req.jti = dados.jti;
  next();
}

// Exige uma funcionalidade "Mobile" da matriz de permissões
function exigeFuncionalidade(nome) {
  return async (req, res, next) => {
    const { rows } = await consulta(
      "SELECT fn_tem_funcionalidade($1, $2, 'Mobile') AS pode",
      [req.utilizador.id_utilizador, nome],
    );
    if (!rows[0].pode) {
      return res.status(403).json({ erro: `Sem permissão: ${nome}.` });
    }
    next();
  };
}

// Só para quem tem registo de colaborador (colaboradores e administradores)
function exigeColaborador(req, res, next) {
  if (!req.utilizador.id_colaborador) {
    return res.status(403).json({ erro: 'Só para colaboradores.' });
  }
  next();
}

function terminarSessao(jti) {
  terminados.add(jti);
}

// O Express 4 não apanha erros de funções async: passam para o next()
const assincrono = (fn) => (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);

module.exports = {
  criarToken,
  exigeLogin: assincrono(exigeLogin),
  exigeFuncionalidade: (nome) => assincrono(exigeFuncionalidade(nome)),
  exigeColaborador,
  terminarSessao,
  assincrono,
};
