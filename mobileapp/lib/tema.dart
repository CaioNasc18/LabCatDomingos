import 'package:flutter/material.dart';

// Cores da identidade visual (iguais ao protótipo em Figma)
class CoresLab {
  static const Color fundo = Color(0xFF0B0B0B);
  static const Color cartao = Color(0xFF141414);
  static const Color linha = Color(0xFF2A2A2A);
  static const Color creme = Color(0xFFF4E8C8);
  static const Color secundario = Color(0xFFA89A73);
  static const Color dourado = Color(0xFFC7A24A);
}

// Tema geral da aplicação, usado no MaterialApp
ThemeData temaLab() {
  return ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    scaffoldBackgroundColor: CoresLab.fundo,
    colorScheme: ColorScheme.fromSeed(
      seedColor: CoresLab.dourado,
      brightness: Brightness.dark,
      primary: CoresLab.creme,
      onPrimary: CoresLab.fundo,
      surface: CoresLab.fundo,
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: CoresLab.fundo,
      foregroundColor: CoresLab.dourado,
      elevation: 0,
    ),
    navigationBarTheme: const NavigationBarThemeData(
      backgroundColor: CoresLab.cartao,
      indicatorColor: CoresLab.linha,
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: CoresLab.creme,
        foregroundColor: CoresLab.fundo,
        minimumSize: const Size.fromHeight(52),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: CoresLab.creme,
        side: const BorderSide(color: CoresLab.creme),
        minimumSize: const Size.fromHeight(48),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
    ),
  );
}
