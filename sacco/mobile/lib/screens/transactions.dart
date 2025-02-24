import 'package:flutter/material.dart';
import 'package:mobile/services/api_service.dart';
import 'package:mobile/models/transaction_model.dart'; // Ensure to import the correct TransactionModel

class TransactionsScreen extends StatefulWidget {
  const TransactionsScreen({super.key});

  @override
  _TransactionsScreenState createState() => _TransactionsScreenState();
}

class _TransactionsScreenState extends State<TransactionsScreen> {
  final _amountController = TextEditingController();
  bool _isLoading = false;
  String _errorMessage = '';
  String _transactionType = 'Deposit'; // or 'Withdrawal' or 'Loan Payment'
  
  final ApiService _apiService = ApiService();
  
  // Method to handle transaction request
  void _performTransaction() async {
    setState(() {
      _isLoading = true;
      _errorMessage = '';
    });

    final amount = double.tryParse(_amountController.text) ?? 0.0;

    // Validating the amount entered
    if (amount <= 0) {
      setState(() {
        _errorMessage = 'Please enter a valid amount.';
        _isLoading = false;
      });
      return;
    }

    try {
      // Assuming 'userId' should be passed to the API service. Replace with the correct user ID.
      String userId = 'sampleUserId'; // Replace with actual user ID logic
      final response = await _apiService.makeTransaction(userId, amount);

      // Adjust this part to match your actual TransactionModel response structure
      if (response.status == 'success') {
        setState(() {
          _errorMessage = 'Transaction successful!';
        });
      } else {
        setState(() {
          _errorMessage = response.message; // Accessing the message from the model
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Transaction failed: $e';
      });
    }

    setState(() {
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Transactions')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: <Widget>[
            DropdownButton<String>(
              value: _transactionType,
              onChanged: (String? newValue) {
                setState(() {
                  _transactionType = newValue!;
                });
              },
              items: <String>['Deposit', 'Withdrawal', 'Loan Payment']
                  .map<DropdownMenuItem<String>>((String value) {
                return DropdownMenuItem<String>(
                  value: value,
                  child: Text(value),
                );
              }).toList(),
            ),
            TextField(
              controller: _amountController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: 'Amount'),
            ),
            if (_errorMessage.isNotEmpty) 
              Text(_errorMessage, style: const TextStyle(color: Colors.red)),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _isLoading ? null : _performTransaction,
              child: _isLoading ? const CircularProgressIndicator() : const Text('Submit Transaction'),
            ),
          ],
        ),
      ),
    );
  }
}
