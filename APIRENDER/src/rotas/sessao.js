// POST /login/ e DELETE /logout/ — mesmo formato da API da Aula 9
const express = require('express');
const { consulta } = require('../bd');
const { verificarPassword } = require('../passwords');
const { criarToken, exigeLogin, terminarSessao, assincrono } = require('../autenticacao');

const router = express.Router();

router.post('/login/', assincrono(async (req, res) => {
  const email = String(req.body.email || '').trim().toLowerCase();
  const password = String(req.body.password || '');
  if (!email || !password) {
    return res.status(400).json({ erro: 'Indique o email e a password.' });
  }

  const { rows } = await consulta(
    `SELECT u.id_utilizador, u.nome, u.password_hash, lower(p.nome) AS perfil, c.id_cliente
     FROM   utilizador u
     JOIN   perfil p       ON p.id_perfil = u.id_perfil
     LEFT   JOIN cliente c ON c.id_utilizador = u.id_utilizador
     WHERE  lower(u.email) = $1 AND u.ativo`,
    [email],
  );
  const utilizador = rows[0];
  if (!utilizador || !(await verificarPassword(password, utilizador.password_hash))) {
    return res.status(401).json({ erro: 'Email ou password incorretos.' });
  }

  await consulta('UPDATE utilizador SET ultimo_login = LOCALTIMESTAMP WHERE id_utilizador = $1', [
    utilizador.id_utilizador,
  ]);

  res.json({
    token: criarToken(utilizador),
    utilizador_id: utilizador.id_utilizador,
    nome: utilizador.nome,
    perfil: utilizador.perfil,
    cliente_id: utilizador.id_cliente,
  });
}));

router.delete('/logout/', exigeLogin, (req, res) => {
  terminarSessao(req.jti);
  res.status(204).end();
});

module.exports = router;
