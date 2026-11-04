import 'package:flutter/material.dart';

import '../tema.dart';

/*
Widgets reutilizáveis da aplicação (padrão da Aula 4):
cada widget é uma classe própria que recebe parâmetros.
*/

// AppBar com título dourado e subtítulo (implementa PreferredSizeWidget)
class MinhaAppBar extends StatelessWidget implements PreferredSizeWidget {
  const MinhaAppBar({
    super.key,
    required this.titulo,
    this.subtitulo = '',
    this.acoes = const [],
  });

  final String titulo;
  final String subtitulo;
  final List<Widget> acoes;

  @override
  Size get preferredSize => const Size.fromHeight(72);

  @override
  Widget build(BuildContext context) {
    return AppBar(
      toolbarHeight: 72,
      title: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            titulo,
            style: const TextStyle(
              fontSize: 23,
              fontWeight: FontWeight.w600,
              color: CoresLab.dourado,
            ),
          ),
          TextoSecundario(texto: subtitulo.toUpperCase(), tamanho: 10),
        ],
      ),
      actions: acoes,
    );
  }
}

// Texto em cor secundária (legendas, datas, médicos)
class TextoSecundario extends StatelessWidget {
  const TextoSecundario({
    super.key,
    required this.texto,
    this.tamanho = 12,
  });

  final String texto;
  final double tamanho;

  @override
  Widget build(BuildContext context) => Text(
        texto,
        style: TextStyle(color: CoresLab.secundario, fontSize: tamanho),
      );
}

// Título de secção (ex.: "Encomendas recentes")
class TituloSeccao extends StatelessWidget {
  const TituloSeccao({super.key, required this.texto});

  final String texto;

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.only(top: 8, bottom: 4),
        child: Text(
          texto,
          style: const TextStyle(
            fontSize: 17,
            fontWeight: FontWeight.w600,
            color: CoresLab.dourado,
          ),
        ),
      );
}

// Botão principal (ElevatedButton)
class BotaoPrincipal extends StatelessWidget {
  const BotaoPrincipal({
    super.key,
    required this.texto,
    required this.aoPressionar,
  });

  final String texto;
  final VoidCallback aoPressionar;

  @override
  Widget build(BuildContext context) => ElevatedButton(
        onPressed: aoPressionar,
        child: Text(
          texto,
          style: const TextStyle(fontWeight: FontWeight.w600),
        ),
      );
}

// Botão com contorno (OutlinedButton)
class BotaoComContorno extends StatelessWidget {
  const BotaoComContorno({
    super.key,
    required this.texto,
    required this.aoPressionar,
  });

  final String texto;
  final VoidCallback aoPressionar;

  @override
  Widget build(BuildContext context) => OutlinedButton(
        onPressed: aoPressionar,
        child: Text(texto),
      );
}

// Botão de ícone (IconButton), usado nas ações da AppBar
class BotaoIcone extends StatelessWidget {
  const BotaoIcone({
    super.key,
    required this.icone,
    required this.aoPressionar,
  });

  final IconData icone;
  final VoidCallback aoPressionar;

  @override
  Widget build(BuildContext context) => IconButton(
        onPressed: aoPressionar,
        icon: Icon(icone, color: CoresLab.creme),
      );
}

// Etiqueta de estado (Por iniciar, Em processamento, Em espera, Concluído)
class EtiquetaEstado extends StatelessWidget {
  const EtiquetaEstado({super.key, required this.estado});

  final String estado;

  @override
  Widget build(BuildContext context) => Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
        decoration: BoxDecoration(
          border: Border.all(color: CoresLab.creme),
          borderRadius: BorderRadius.circular(999),
        ),
        child: Text(
          estado,
          style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold),
        ),
      );
}

// Etiqueta dourada da etapa (só aparece ao colaborador)
class EtiquetaEtapa extends StatelessWidget {
  const EtiquetaEtapa({super.key, required this.etapa});

  final String etapa;

  @override
  Widget build(BuildContext context) => Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
        decoration: BoxDecoration(
          color: const Color(0xFF2A2118),
          border: Border.all(color: CoresLab.dourado),
          borderRadius: BorderRadius.circular(999),
        ),
        child: Text(
          etapa,
          style: const TextStyle(
            fontSize: 10,
            fontWeight: FontWeight.bold,
            color: CoresLab.dourado,
          ),
        ),
      );
}

// Caixa base dos cartões (Container com fundo, borda e cantos)
class Cartao extends StatelessWidget {
  const Cartao({super.key, required this.filho});

  final Widget filho;

  @override
  Widget build(BuildContext context) => Container(
        width: double.infinity,
        margin: const EdgeInsets.only(bottom: 10),
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: CoresLab.cartao,
          border: Border.all(color: CoresLab.linha),
          borderRadius: BorderRadius.circular(16),
        ),
        child: filho,
      );
}

// Cartão de resumo do Início (número + legenda)
class CartaoResumo extends StatelessWidget {
  const CartaoResumo({
    super.key,
    required this.valor,
    required this.legenda,
  });

  final int valor;
  final String legenda;

  @override
  Widget build(BuildContext context) => Cartao(
        filho: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '$valor',
              style: const TextStyle(fontSize: 23, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 10),
            TextoSecundario(texto: legenda),
          ],
        ),
      );
}

// Grelha 2x2 de cartões de resumo (Row dentro de Column)
class GrelhaResumo extends StatelessWidget {
  const GrelhaResumo({super.key, required this.cartoes});

  final List<CartaoResumo> cartoes;

  @override
  Widget build(BuildContext context) => Column(
        children: [
          Row(
            children: [
              Expanded(child: cartoes[0]),
              const SizedBox(width: 10),
              Expanded(child: cartoes[1]),
            ],
          ),
          Row(
            children: [
              Expanded(child: cartoes[2]),
              const SizedBox(width: 10),
              Expanded(child: cartoes[3]),
            ],
          ),
        ],
      );
}

// Logótipo do projeto: LAB em dourado, nome à direita
class LogoLab extends StatelessWidget {
  const LogoLab({super.key});

  @override
  Widget build(BuildContext context) => Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Text(
            'LAB',
            style: TextStyle(
              fontSize: 54,
              fontWeight: FontWeight.bold,
              color: CoresLab.dourado,
            ),
          ),
          Container(
            width: 1,
            height: 52,
            margin: const EdgeInsets.symmetric(horizontal: 14),
            color: CoresLab.dourado,
          ),
          const Text(
            'Catarina\nDomingos',
            style: TextStyle(fontSize: 19, fontWeight: FontWeight.w500),
          ),
        ],
      );
}

// Conteúdo provisório dos separadores ainda por desenvolver
class EcraEmConstrucao extends StatelessWidget {
  const EcraEmConstrucao({super.key, required this.nome});

  final String nome;

  @override
  Widget build(BuildContext context) => Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.construction, color: CoresLab.dourado, size: 40),
            const SizedBox(height: 12),
            Text(nome, style: const TextStyle(fontSize: 17)),
            const SizedBox(height: 4),
            const TextoSecundario(texto: 'Ecrã a desenvolver no próximo passo'),
          ],
        ),
      );
}

// Perfil provisório, comum aos dois perfis, só com o botão Sair
class PerfilProvisorio extends StatelessWidget {
  const PerfilProvisorio({
    super.key,
    required this.nome,
    required this.aoSair,
  });

  final String nome;
  final VoidCallback aoSair;

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        Cartao(
          filho: Text(
            nome,
            style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w600),
          ),
        ),
        const SizedBox(height: 20),
        BotaoPrincipal(texto: 'Sair', aoPressionar: aoSair),
      ],
    );
  }
}
