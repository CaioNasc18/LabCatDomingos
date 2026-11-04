import 'package:flutter/material.dart';

import '../dados/dados_exemplo.dart';
import '../widgets/widgets_comuns.dart';

/*
Área do Cliente, com NavigationBar de 5 destinos (padrão da Aula 5):
Início, Encomendas, Novo, Notificações e Perfil.
O cliente vê apenas o estado das encomendas, nunca as etapas.
*/
class EcraCliente extends StatefulWidget {
  const EcraCliente({super.key});

  @override
  State<EcraCliente> createState() => _EcraClienteState();
}

class _EcraClienteState extends State<EcraCliente> {
  int _indiceAtual = 0;

  static const _titulos = <String>[
    'Clínica Dente',
    'Encomendas',
    'Nova Encomenda',
    'Notificações',
    'Conta',
  ];

  void _selecionarDestino(int index) {
    setState(() {
      _indiceAtual = index;
    });
  }

  void _novaEncomenda() {
    _selecionarDestino(2);
  }

  void _abrirNotificacoes() {
    _selecionarDestino(3);
  }

  void _sair() {
    Navigator.pop(context);
  }

  // Devolve o conteúdo do separador selecionado
  Widget _construirCorpo() {
    switch (_indiceAtual) {
      case 0:
        return InicioCliente(aoNovaEncomenda: _novaEncomenda);
      case 1:
        return const EcraEmConstrucao(nome: 'Lista de encomendas');
      case 2:
        return const EcraEmConstrucao(nome: 'Nova encomenda (4 passos)');
      case 3:
        return const EcraEmConstrucao(nome: 'Notificações');
      default:
        return PerfilProvisorio(nome: 'Clínica Dente', aoSair: _sair);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: MinhaAppBar(
        titulo: _titulos[_indiceAtual],
        subtitulo: 'Área do cliente',
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
            icon: Icon(Icons.assignment_outlined),
            selectedIcon: Icon(Icons.assignment),
            label: 'Encomendas',
          ),
          NavigationDestination(
            icon: Icon(Icons.add_circle_outline),
            selectedIcon: Icon(Icons.add_circle),
            label: 'Novo',
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

// Separador Início do cliente: resumo por estado e encomendas recentes
class InicioCliente extends StatelessWidget {
  const InicioCliente({super.key, required this.aoNovaEncomenda});

  final VoidCallback aoNovaEncomenda;

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        GrelhaResumo(
          cartoes: [
            CartaoResumo(
              valor: contarEncomendas('Por iniciar'),
              legenda: 'Por iniciar',
            ),
            CartaoResumo(
              valor: contarEncomendas('Em processamento'),
              legenda: 'Em processamento',
            ),
            CartaoResumo(
              valor: contarEncomendas('Em espera'),
              legenda: 'Em espera',
            ),
            CartaoResumo(
              valor: contarEncomendas('Concluído'),
              legenda: 'Concluídos',
            ),
          ],
        ),
        const SizedBox(height: 6),
        BotaoPrincipal(texto: '+ Nova Encomenda', aoPressionar: aoNovaEncomenda),
        const SizedBox(height: 12),
        const TituloSeccao(texto: 'Encomendas recentes'),
        for (var encomenda in encomendasCliente)
          CartaoEncomenda(encomenda: encomenda),
      ],
    );
  }
}

// Cartão de uma encomenda na lista do cliente
class CartaoEncomenda extends StatelessWidget {
  const CartaoEncomenda({super.key, required this.encomenda});

  final Encomenda encomenda;

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
                encomenda.codigo,
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              EtiquetaEstado(estado: encomenda.estado),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            encomenda.paciente,
            style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
          ),
          TextoSecundario(texto: encomenda.medico),
          const SizedBox(height: 4),
          Text(encomenda.trabalhos, style: const TextStyle(fontSize: 12)),
          const SizedBox(height: 6),
          TextoSecundario(texto: 'Prazo: ${encomenda.prazo}'),
        ],
      ),
    );
  }
}
