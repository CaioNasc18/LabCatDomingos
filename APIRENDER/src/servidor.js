// API REST do Laboratório Catarina Domingos — Node.js + Express + PostgreSQL (Neon)
require('dotenv').config();
const express = require('express');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json({ limit: '1mb' }));

// Para "acordar" o serviço no Render e confirmar a ligação à BD
app.get('/', async (req, res, next) => {
  try {
    const { consulta } = require('./bd');
    await consulta('SELECT 1');
    res.json({ api: 'LAB Catarina Domingos', estado: 'ok', bd: 'ok' });
  } catch (e) {
    next(e);
  }
});

app.use(require('./rotas/sessao'));
app.use(require('./rotas/sync'));
app.use(require('./rotas/encomendas'));
app.use(require('./rotas/trabalhos'));

app.use((req, res) => res.status(404).json({ erro: `Rota inexistente: ${req.method} ${req.path}` }));

// Erros: as regras de negócio da BD (RAISE EXCEPTION) chegam como 400
// eslint-disable-next-line no-unused-vars
app.use((erro, req, res, next) => {
  if (erro.type === 'entity.parse.failed') {
    return res.status(400).json({ erro: 'JSON inválido no corpo do pedido.' });
  }
  if (erro.code === 'P0001') {
    return res.status(400).json({ erro: erro.message });
  }
  if (erro.code && /^(22|23)/.test(erro.code)) {
    return res.status(400).json({ erro: erro.detail || erro.message });
  }
  console.error(erro);
  res.status(500).json({ erro: 'Erro interno do servidor.' });
});

const porta = process.env.PORT || 3001;
app.listen(porta, () => console.log(`API a correr na porta ${porta}`));
