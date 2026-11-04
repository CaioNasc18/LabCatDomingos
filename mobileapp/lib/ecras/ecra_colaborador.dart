import 'package:flutter/material.dart';

import '../dados/dados_exemplo.dart';
import '../widgets/widgets_comuns.dart';

/*
Área do Colaborador, com NavigationBar de 5 destinos (padrão da Aula 5):
Início, Disponíveis, Meus Trabalhos, Notificações e Perfil.
Todos os colaboradores têm as mesmas funcionalidades.
*/
class EcraColaborador extends StatefulWidget {
  const EcraColaborador({super.key});

  @override
  State<EcraColaborador> createState() => _EcraColaboradorState();
}

class _EcraColaboradorState extends State<EcraColaborador> {
  int _indiceAtual = 0;

  static const _titulos = <String>[
    'Carlos Mendes',
    'Trabalhos Disponíveis',
    'Meus Trabalhos',
    'Notificações',
    'Conta',
  ];

  void _selecionarDestino(int index) {
    setState(() {
      _indiceAtual = index;
    });
  }

  void _abrirNotificacoes() {
    _selecionarDestino(3);
  }

  void _sair() {
    Navigator.pop(context);
  }

  Widget _construirCorpo() {
    switch (_indiceAtual) {
      case 0:
        return const InicioColaborador();
      case 1:
        return const EcraEmConstrucao(nome: 'Trabalhos disponíveis');
      case 2:
        return const EcraEmConstrucao(nome: 'Meus trabalhos');
      case 3:
        return const EcraEmConstrucao(nome: 'Notificações');
      default:
        return PerfilProvisorio(nome: 'Carlos Mendes', aoSair: _sair);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: MinhaAppBar(
        titulo: _titulos[_indiceAtual],
        subtitulo: 'Laboratório Catarina Domingos',
        acoes: [
          BotaoIcone(
            icone: Icons.notifications_outlined,
            aoPressionar: _abrirNotificacoes,
          ),
        ],
      ),
      body: _construirCorpo(),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _indiceAtual,
        onDestinationSelected: _selecionarDestino,
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home),
            label: 'Início',
          ),
          NavigationDestination(
            icon: Icon(Icons.layers_outlined),
            selectedIcon: Icon(Icons.layers),
            label: 'Disponíveis',
          ),
          NavigationDestination(
            icon: Icon(Icons.work_outline),
            selectedIcon: Icon(Icons.work),
            label: 'Meus Trabalhos',
          ),
          NavigationDestination(
            icon: Icon(Icons.notifications_outlined),
            selectedIcon: Icon(Icons.notifications),
            label: 'Notificações',
          ),
          NavigationDestination(
            icon: Icon(Icons.person_outline),
            selectedIcon: Icon(Icons.person),
            label: 'Perfil',
          ),
        ],
      ),
    );
  }
}

// Separador Início do colaborador: resumo e trabalhos em curso
class InicioColaborador extends StatelessWidget {
  const InicioColaborador({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        GrelhaResumo(
          cartoes: [
            const CartaoResumo(valor: 6, legenda: 'Disponíveis'),
            CartaoResumo(
              valor: contarTrabalhos('Em processamento'),
              legenda: 'Em execução por mim',
            ),
            CartaoResumo(
              valor: contarTrabalhos('Em espera'),
              legenda: 'Em espera',
            ),
            const CartaoResumo(valor: 8, legenda: 'Concluídos'),
          ],
        ),
        const SizedBox(height: 6),
        const TituloSeccao(texto: 'Trabalhos em curso'),
        for (var trabalho in trabalhosColaborador)
          CartaoTrabalho(trabalho: trabalho),
      ],
    );
  }
}

// Cartão de um trabalho do colaborador (mostra a etapa atual)
class CartaoTrabalho extends StatelessWidget {
  const CartaoTrabalho({super.key, required this.trabalho});

  final Trabalho trabalho;

  @override
  Widget build(BuildContext context) {
    return Cartao(
      filho: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                trabalho.codigo,
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              EtiquetaEstado(estado: trabalho.estado),
            ],
          ),
          const SizedBox(height: 6),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                trabalho.tipo,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),
              EtiquetaEtapa(etapa: trabalho.etapa),
            ],
          ),
          const SizedBox(height: 4),
          TextoSecundario(texto: '${trabalho.clinica} · ${trabalho.paciente}'),
          const SizedBox(height: 6),
          TextoSecundario(texto: 'Prazo: ${trabalho.prazo}'),
        ],
      ),
    );
  }
}
