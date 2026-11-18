// Passwords da tabela utilizador (password_hash).
// Formato oficial do projeto: o do Django (make_password do backoffice):
//   pbkdf2_sha256$<iterações>$<salt em texto>$<hash base64, 32 bytes>
// As iterações são lidas do próprio hash (mudam com a versão do Django).
// bcrypt e salt:hash só são aceites na verificação; a API nunca os grava,
// porque o backoffice (check_password) não os reconhece.
const crypto = require('crypto');
const bcrypt = require('bcryptjs');

// Valor do Django 6.1 (o instalado no backoffice)
const ITERACOES = 1500000;

// PBKDF2 assíncrono: com 1,5 milhões de iterações demora perto de 1 s,
// e a versão síncrona bloquearia a API para os outros pedidos.
const pbkdf2 = (password, salt, iteracoes) => new Promise((resolve, reject) => {
  crypto.pbkdf2(password, salt, iteracoes, 32, 'sha256', (erro, chave) => (
    erro ? reject(erro) : resolve(chave.toString('base64'))));
});

function iguais(a, b) {
  const x = Buffer.from(a);
  const y = Buffer.from(b);
  return x.length === y.length && crypto.timingSafeEqual(x, y);
}

async function verificarPassword(password, guardado) {
  if (!guardado) return false;

  if (guardado.startsWith('pbkdf2_sha256$')) {
    const [, iteracoes, salt, hash] = guardado.split('$');
    if (!Number(iteracoes) || !salt || !hash) return false;
    const calculado = await pbkdf2(password, salt, Number(iteracoes));
    return iguais(calculado, hash);
  }

  if (/^\$2[aby]\$/.test(guardado)) {
    return bcrypt.compare(password, guardado);
  }

  if (guardado.includes(':')) {
    const [salt, hash] = guardado.split(':');
    const calculado = crypto.createHash('sha256').update(salt + password).digest('hex');
    return iguais(calculado, hash);
  }

  return false;
}

// Gera um hash no formato do Django, para o backoffice e a API lerem a mesma password.
async function gerarHash(password, iteracoes = ITERACOES) {
  const salt = crypto.randomBytes(16).toString('base64').replace(/[^A-Za-z0-9]/g, '').slice(0, 22);
  const hash = await pbkdf2(password, salt, iteracoes);
  return `pbkdf2_sha256$${iteracoes}$${salt}$${hash}`;
}

module.exports = { verificarPassword, gerarHash };
