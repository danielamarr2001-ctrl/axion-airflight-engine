import 'package:flutter/material.dart';

import 'app_shell.dart';

void main() {
  runApp(const AxiomApp());
}

class AxiomApp extends StatelessWidget {
  const AxiomApp({super.key});

  @override
  Widget build(BuildContext context) {
    const seed = Color(0xFF21C9A3);

    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'AXIOM Dashboard',
      themeMode: ThemeMode.dark,
      darkTheme: ThemeData(
        brightness: Brightness.dark,
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          brightness: Brightness.dark,
          seedColor: seed,
        ),
        scaffoldBackgroundColor: const Color(0xFF0A1118),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: const Color(0xFF0C1620),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(10),
            borderSide: const BorderSide(color: Color(0xFF294558)),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(10),
            borderSide: const BorderSide(color: Color(0xFF294558)),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(10),
            borderSide: const BorderSide(color: Color(0xFF3CDDB8), width: 1.1),
          ),
        ),
      ),
      home: const AppShell(),
    );
  }
}
