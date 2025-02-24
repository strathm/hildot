import 'package:flutter/material.dart';
import 'package:mobile/models/loan_model.dart';

class LoanCard extends StatelessWidget {
  final LoanModel loan;

  const LoanCard({super.key, required this.loan});

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
            Text('Loan Amount: KSh ${loan.amount}', style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            Text('Interest Rate: ${loan.interestRate}%', style: const TextStyle(fontSize: 14)),
            Text('Term: ${loan.termInMonths} months', style: const TextStyle(fontSize: 14)),
            Text('Status: ${loan.status}', style: const TextStyle(fontSize: 14, color: Colors.green)),
          ],
        ),
      ),
    );
  }
}
