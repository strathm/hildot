import 'package:flutter/material.dart';
import 'package:mobile/models/savings_model.dart';

class SavingsCard extends StatelessWidget {
  final SavingsModel savings;

  const SavingsCard({super.key, required this.savings});

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 5,
      margin: const EdgeInsets.symmetric(vertical: 10),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Use savings.balance and savings.earnedInterest
            Text('Savings Balance: KSh ${savings.balance}', style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            Text('Interest Earned: KSh ${savings.earnedInterest}', style: const TextStyle(fontSize: 14)),
          ],
        ),
      ),
    );
  }
}
