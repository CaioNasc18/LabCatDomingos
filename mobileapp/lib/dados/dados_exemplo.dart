/*
Classes de dados e dados de exemplo.
Nesta fase os dados são fixos; mais tarde passam a vir da API REST.
*/

// Encomenda, tal como o cliente a vê (sem etapas)
class Encomenda {
  Encomenda({
    required this.codigo,
    required this.paciente,
    required this.medico,
    required this.trabalhos,
    required this.prazo,
    required this.estado,
  });

  final String codigo;
  final String paciente;
  final String medico;
  final String trabalhos;
  final String prazo;
  final String estado; // Por iniciar, Em processamento, Em espera, Concluído
}

// Trabalho, tal como o colaborador o vê (com a etapa)
class Trabalho {
  Trabalho({
    required this.codigo,
    required this.tipo,
    required this.etapa,
    required this.clinica,
    required this.paciente,
    required this.prazo,
    required this.estado,
  });

  final String codigo;
  final String tipo;
  final String etapa;
  final String clinica;
  final String paciente;
  final String prazo;
  final String estado;
}

final encomendasCliente = <Encomenda>[
  Encomenda(
    codigo: 'OT-2026-0049',
    paciente: 'Maria Costa',
    medico: 'Dra. Inês Martins',
    trabalhos: 'Coroa Dissilicato',
    prazo: '09 Nov 2026',
    estado: 'Por iniciar',
  ),
  Encomenda(
    codigo: 'OT-2026-0048',
    paciente: 'Pedro Lopes',
    medico: 'Dra. Inês Martins',
    trabalhos: 'Prótese Acrílica',
    prazo: '05 Nov 2026',
    estado: 'Em espera',
  ),
  Encomenda(
    codigo: 'OT-2026-0047',
    paciente: 'João Silva',
    medico: 'Dr. Ricardo Alves',
    trabalhos: 'Coroa Zr. + Goteira de Bruxismo',
    prazo: '22 Out 2026',
    estado: 'Em processamento',
  ),
  Encomenda(
    codigo: 'OT-2026-0046',
    paciente: 'Rita Gomes',
    medico: 'Dr. Ricardo Alves',
    trabalhos: 'Goteira de Bruxismo',
    prazo: '15 Out 2026',
    estado: 'Concluído',
  ),
];

final trabalhosColaborador = <Trabalho>[
  Trabalho(
    codigo: 'OT-2026-0047',
    tipo: 'Coroa Zr.',
    etapa: 'CAD CAM',
    clinica: 'Clínica Dente',
    paciente: 'João Silva',
    prazo: '22 Out 2026',
    estado: 'Em processamento',
  ),
  Trabalho(
    codigo: 'OT-2026-0051',
    tipo: 'Coroa Dissilicato',
    etapa: 'CAD CAM',
    clinica: 'Clínica Sorriso',
    paciente: 'Sofia Martins',
    prazo: '09 Nov 2026',
    estado: 'Em processamento',
  ),
  Trabalho(
    codigo: 'OT-2026-0048',
    tipo: 'Prótese Acrílica',
    etapa: 'Articulação',
    clinica: 'Clínica Dente',
    paciente: 'Pedro Lopes',
    prazo: '05 Nov 2026',
    estado: 'Em espera',
  ),
];

// Conta quantas encomendas existem num dado estado
int contarEncomendas(String estado) {
  var total = 0;
  for (var encomenda in encomendasCliente) {
    if (encomenda.estado == estado) {
      total++;
    }
  }
  return total;
}

// Conta quantos trabalhos do colaborador estão num dado estado
int contarTrabalhos(String estado) {
  var total = 0;
  for (var trabalho in trabalhosColaborador) {
    if (trabalho.estado == estado) {
      total++;
    }
  }
  return total;
}
