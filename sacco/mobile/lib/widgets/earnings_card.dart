import 'package:flutter/material.dart';
import 'package:mobile/models/earnings_model.dart';

class EarningsCard extends StatelessWidget {
  final EarningsModel earnings;

  const EarningsCard({super.key, required this.earnings});

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
            // Use earnings.earnings for the total earnings
            Text('Total Earnings: KSh ${earnings.earnings}', style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            // Remove the interestRate field if not available in the model
            // Text('Interest Rate: ${earnings.interestRate}%', style: const TextStyle(fontSize: 14)),
          ],
        ),
      ),
    );
  }
}
