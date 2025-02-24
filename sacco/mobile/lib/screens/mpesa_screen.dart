// lib/screens/mpesa_screen.dart
import 'package:flutter/material.dart';

class MpesaScreen extends StatelessWidget {
  const MpesaScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('MPesa Integration'),
      ),
      body: Center(
        child: const Text('MPesa Screen (Functionality goes here)'),
      ),
    );
  }
}
