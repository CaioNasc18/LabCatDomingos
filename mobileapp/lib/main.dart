import 'package:flutter/material.dart';

import 'ecras/pagina_login.dart';
import 'tema.dart';

/*
Programa principal da aplicação móvel do LAB Catarina Domingos.
Perfis com acesso: Cliente e Colaborador.
O perfil Administrador só tem acesso ao backoffice.
*/
void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'LAB Catarina Domingos',
      debugShowCheckedModeBanner: false,
      theme: temaLab(),
      home: const PaginaLogin(),
    );
  }
}
