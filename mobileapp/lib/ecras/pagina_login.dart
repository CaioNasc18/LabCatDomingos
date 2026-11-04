import 'package:flutter/material.dart';

import '../tema.dart';
import '../widgets/widgets_comuns.dart';
import 'ecra_cliente.dart';
import 'ecra_colaborador.dart';

/*
Página de entrada (login), comum aos perfis Cliente e Colaborador.
Segue o padrão da TextField da Aula 6: controladores criados em
initState, libertados em dispose e lidos num método próprio.
*/
class PaginaLogin extends StatefulWidget {
  const PaginaLogin({super.key});

  @override
  State<PaginaLogin> createState() => _PaginaLoginState();
}

class _PaginaLoginState extends State<PaginaLogin> {
  late TextEditingController _controladorEmail;
  late TextEditingController _controladorSenha;
  String _mensagem = '';

  @override
  void initState() {
    super.initState();
    _controladorEmail = TextEditingController(text: 'clinica@clinica.com');
    _controladorSenha = TextEditingController(text: 'clinica12345');
  }

  @override
  void dispose() {
    _controladorEmail.dispose();
    _controladorSenha.dispose();
    super.dispose();
  }

  // Valida os dados e encaminha para a área do perfil correspondente
  void _entrar() {
    final email = _controladorEmail.text.trim().toLowerCase();
    final senha = _controladorSenha.text;

    if (email.isEmpty || senha.isEmpty || !email.contains('@')) {
      setState(() {
        _mensagem = 'Preencha o e-mail e a senha.';
      });
      return;
    }

    // Provisório: o perfil é deduzido do e-mail até existir a API (JWT)
    if (email.startsWith('admin')) {
      setState(() {
        _mensagem = 'O perfil de Administrador não tem acesso à aplicação '
            'móvel. Utilize o backoffice.';
      });
      return;
    }

    setState(() {
      _mensagem = '';
    });

    if (email.endsWith('@catarinadomingos.pt')) {
      _irParaColaborador();
    } else {
      _irParaCliente();
    }
  }

  void _irParaCliente() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const EcraCliente()),
    );
  }

  void _irParaColaborador() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const EcraColaborador()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.symmetric(horizontal: 28),
          children: [
            const SizedBox(height: 120),
            const LogoLab(),
            const SizedBox(height: 14),
            const Center(
              child: TextoSecundario(
                texto: 'LABORATÓRIO DE PRÓTESE DENTÁRIA',
                tamanho: 11,
              ),
            ),
            const SizedBox(height: 120),
            TextField(
              controller: _controladorEmail,
              keyboardType: TextInputType.emailAddress,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                labelText: 'E-mail',
                prefixIcon: Icon(Icons.mail_outline),
              ),
            ),
            const SizedBox(height: 14),
            TextField(
              controller: _controladorSenha,
              obscureText: true,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                labelText: 'Senha',
                prefixIcon: Icon(Icons.lock_outline),
              ),
            ),
            const SizedBox(height: 14),
            if (_mensagem.isNotEmpty)
              Text(
                _mensagem,
                style: const TextStyle(color: CoresLab.dourado),
              ),
            const SizedBox(height: 32),
            BotaoPrincipal(texto: 'Entrar', aoPressionar: _entrar),
          ],
        ),
      ),
    );
  }
}
