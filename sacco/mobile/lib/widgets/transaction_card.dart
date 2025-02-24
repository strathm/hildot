import 'package:flutter/material.dart';
import 'package:mobile/models/transaction_model.dart';

class TransactionCard extends StatelessWidget {
  final TransactionModel transaction;

  const TransactionCard({super.key, required this.transaction});

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 5,
      margin: const EdgeInsets.symmetric(vertical: 10),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            // Replaced 'transaction.id' with 'transaction.transactionId'
            Text('Transaction ID: ${transaction.transactionId}', style: const TextStyle(fontSize: 14)),
            Text('Amount: KSh ${transaction.amount}', style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold)),
            Text('Date: ${transaction.date}', style: const TextStyle(fontSize: 12)),
          ],
        ),
      ),
    );
  }
}
