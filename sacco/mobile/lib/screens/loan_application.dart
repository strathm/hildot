import 'package:flutter/material.dart';
import 'package:mobile/services/api_service.dart';
import 'package:mobile/models/loan_model.dart';  // Ensure LoanModel is imported

class LoanApplicationScreen extends StatefulWidget {
  const LoanApplicationScreen({super.key});

  @override
  _LoanApplicationScreenState createState() => _LoanApplicationScreenState();
}

class _LoanApplicationScreenState extends State<LoanApplicationScreen> {
  final _loanAmountController = TextEditingController();
  final _loanTermController = TextEditingController();
  bool _isLoading = false;
  String _errorMessage = '';

  // Method to handle loan application
  Future<void> _applyForLoan() async {
    setState(() {
      _isLoading = true;
      _errorMessage = '';
    });

    final loanAmount = double.tryParse(_loanAmountController.text) ?? 0.0;
    final loanTerm = int.tryParse(_loanTermController.text) ?? 0;

    if (loanAmount <= 0 || loanTerm <= 0) {
      setState(() {
        _errorMessage = 'Please enter valid loan amount and term.';
        _isLoading = false;
      });
      return;
    }

    try {
      // Create an instance of ApiService
      ApiService apiService = ApiService();

      // Ensure proper types are passed to the API service
      final LoanModel loan = await apiService.applyForLoan('user123', loanAmount); // Use userId here

      // Assuming LoanModel has fields like 'loanId' and 'status'
      if (loan.loanId != null && loan.status == 'approved') {
        setState(() {
          _errorMessage = 'Loan application submitted successfully! Loan ID: ${loan.loanId}';
        });
      } else {
        setState(() {
          _errorMessage = 'Loan application failed. Status: ${loan.status}';
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Loan application failed: $e';
      });
    }

    setState(() {
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Loan Application')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: <Widget>[
            TextField(
              controller: _loanAmountController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: 'Loan Amount'),
            ),
            TextField(
              controller: _loanTermController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: 'Loan Term (months)'),
            ),
            if (_errorMessage.isNotEmpty)
              Text(_errorMessage, style: const TextStyle(color: Colors.red)),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _isLoading ? null : _applyForLoan,
              child: _isLoading ? const CircularProgressIndicator() : const Text('Apply for Loan'),
            ),
          ],
        ),
      ),
    );
  }
}
