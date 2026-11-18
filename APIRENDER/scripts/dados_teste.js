// Cria utilizadores de teste (password: password123) e uma encomenda aceite.
// Pode ser corrido várias vezes: não duplica nada.
//   npm run dados-teste
require('dotenv').config();
const { pool, transacao } = require('../src/bd');
const { gerarHash } = require('../src/passwords');

const PASSWORD = 'password123';

async function criarUtilizador(bd, perfil, nome, email) {
  const { rows } = await bd.query(
    `INSERT INTO utilizador (id_perfil, nome, email, password_hash)
     SELECT id_perfil, $2, $3, $4 FROM perfil WHERE nome = $1
     ON CONFLICT (email) DO NOTHING
     RETURNING id_utilizador`,
    [perfil, nome, email, await gerarHash(PASSWORD)],
  );
  if (rows.length) return { id: rows[0].id_utilizador, novo: true };
  const existente = await bd.query('SELECT id_utilizador FROM utilizador WHERE email = $1', [email]);
  return { id: existente.rows[0].id_utilizador, novo: false };
}

async function main() {
  await transacao(null, async (bd) => {
    const admin = await criarUtilizador(bd, 'Administrador', 'Catarina Domingos', 'admin1@laboratorio.pt');
    if (admin.novo) {
      // o trigger trg_admin_colaborador cria também o registo de colaborador
      await bd.query('INSERT INTO administrador (id_utilizador) VALUES ($1)', [admin.id]);
    }

    const colab = await criarUtilizador(bd, 'Colaborador', 'Carlos Martins', 'colaborador1@laboratorio.pt');
    if (colab.novo) {
      await bd.query('INSERT INTO colaborador (id_utilizador) VALUES ($1)', [colab.id]);
    }

    const cli = await criarUtilizador(bd, 'Cliente', 'Clínica Dente', 'cliente1@exemplo.pt');
    if (cli.novo) {
      await bd.query(
        `INSERT INTO cliente (id_utilizador, nome, nif, morada, tipo_entidade)
         VALUES ($1, 'Clínica Dente', '509123456', 'Viseu', 'Clínica')`,
        [cli.id],
      );
    }

    // Uma encomenda de exemplo, aceite, se o cliente ainda não tiver nenhuma
    const { rows: existentes } = await bd.query(
      `SELECT 1 FROM encomenda e JOIN cliente c ON c.id_cliente = e.id_cliente
       WHERE c.id_utilizador = $1`, [cli.id]);
    if (existentes.length === 0) {
      const { rows: [c] } = await bd.query('SELECT id_cliente FROM cliente WHERE id_utilizador = $1', [cli.id]);
      const { rows: [pac] } = await bd.query(
        `INSERT INTO paciente (nome, data_nascimento, sexo)
         VALUES ('Carla Mendes', '1992-03-10', 'F') RETURNING id_paciente`);
      const { rows: tipos } = await bd.query(
        `SELECT id_tipo_trabalho FROM tipo_trabalho
         WHERE nome IN ('Coroa Zr.', 'Goteira de branqueamento') ORDER BY id_tipo_trabalho`);
      const { rows: [enc] } = await bd.query(
        'CALL sp_criar_encomenda($1, $2, $3::INT[], NULL, $4, $5, NULL)',
        [c.id_cliente, cli.id, tipos.map((t) => t.id_tipo_trabalho), pac.id_paciente,
          'Encomenda de teste criada pelo script'],
      );
      await bd.query(
        "CALL sp_aceitar_encomenda($1, LOCALTIMESTAMP + INTERVAL '10 days', $2)",
        [enc.p_id_encomenda, admin.id],
      );
    }
  });

  console.log('Utilizadores de teste prontos (password: password123):');
  console.log('  admin1@laboratorio.pt  colaborador1@laboratorio.pt  cliente1@exemplo.pt');
  await pool.end();
}

main().catch(async (e) => {
  console.error(e.message);
  await pool.end();
  process.exit(1);
});
