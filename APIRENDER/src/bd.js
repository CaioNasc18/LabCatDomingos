// Ligação ao PostgreSQL (Neon). O endereço vem da variável DATABASE_URL.
const { Pool, types } = require('pg');

// Datas devolvidas tal como estão na BD (sem conversões de fuso horário)
types.setTypeParser(1114, (v) => v); // TIMESTAMP
types.setTypeParser(1082, (v) => v); // DATE
types.setTypeParser(20, (v) => parseInt(v, 10)); // BIGINT (ex.: COUNT)

const ligacao = process.env.DATABASE_URL;
if (!ligacao) {
  throw new Error('Falta a variável de ambiente DATABASE_URL (ver .env.exemplo).');
}

// O Neon exige SSL; uma base de dados local (localhost) não.
const local = /localhost|127\.0\.0\.1|host=\/tmp/.test(ligacao);

const pool = new Pool({
  connectionString: ligacao,
  ssl: local ? false : { rejectUnauthorized: false },
  max: 5,
});

// Consulta simples (sem transação)
function consulta(sql, valores = []) {
  return pool.query(sql, valores);
}

// Corre várias consultas numa transação e indica quem faz a ação,
// para os triggers de logs e histórico (fn_utilizador_atual).
async function transacao(idUtilizador, trabalho) {
  const cliente = await pool.connect();
  try {
    await cliente.query('BEGIN');
    if (idUtilizador) {
      await cliente.query("SELECT set_config('app.id_utilizador', $1, true)", [String(idUtilizador)]);
    }
    const resultado = await trabalho(cliente);
    await cliente.query('COMMIT');
    return resultado;
  } catch (erro) {
    await cliente.query('ROLLBACK');
    throw erro;
  } finally {
    cliente.release();
  }
}

module.exports = { pool, consulta, transacao };
