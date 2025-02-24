import 'package:flutter/material.dart';
import 'package:mobile/services/api_service.dart';
import 'package:mobile/models/loan_model.dart';  // Ensure LoanModel is imported

class LoanStatusScreen extends StatefulWidget {
  const LoanStatusScreen({super.key});

  @override
  _LoanStatusScreenState createState() => _LoanStatusScreenState();
}

class _LoanStatusScreenState extends State<LoanStatusScreen> {
  String _loanStatus = 'Loading...';
  bool _isLoading = true;

  // Function to fetch loan status
  void _fetchLoanStatus() async {
    try {
      // Assuming ApiService is a singleton or use an instance of ApiService
      ApiService apiService = ApiService();

      // Replace 'sampleLoanId' with the actual loan ID you want to fetch
      final LoanModel loan = await apiService.getLoanStatus('sampleLoanId');  // Pass the loan ID

      // Assuming LoanModel has fields like 'loanBalance' and 'repaymentStatus'
      setState(() {
        _loanStatus = 'Loan Balance: \$${loan.loanBalance} | Repayment Status: ${loan.repaymentStatus}';
      });
    } catch (e) {
      setState(() {
        _loanStatus = 'Error: $e';
      });
    }

    setState(() {
      _isLoading = false;
    });
  }

  @override
  void initState() {
    super.initState();
    _fetchLoanStatus();  // Call the function to fetch loan status when the screen initializes
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Loan Status')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: <Widget>[
            if (_isLoading)
              const CircularProgressIndicator(), // Show loading indicator while fetching
            if (!_isLoading)
              Text(_loanStatus), // Display the loan status or error message
          ],
        ),
      ),
    );
  }
}
