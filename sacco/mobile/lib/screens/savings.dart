import 'package:flutter/material.dart';
import 'package:mobile/services/api_service.dart';
import 'package:mobile/models/savings_model.dart'; // Ensure to import the SavingsModel

class SavingsScreen extends StatefulWidget {
  const SavingsScreen({super.key});

  @override
  _SavingsScreenState createState() => _SavingsScreenState();
}

class _SavingsScreenState extends State<SavingsScreen> {
  double _savingsAmount = 0.0;
  double _earnedInterest = 0.0;

  bool _isLoading = true;
  String _errorMessage = '';

  final ApiService _apiService = ApiService();

  // Method to fetch savings data
  void _fetchSavings() async {
    setState(() {
      _isLoading = true;
      _errorMessage = '';
    });

    // Replace with actual logic to get the current user ID
    String userId = 'sampleUserId'; // This should be dynamically fetched
    try {
      final SavingsModel response = await _apiService.getSavings(userId);

      setState(() {
        _savingsAmount = response.balance; // Corrected field: balance
        _earnedInterest = response.earnedInterest; // Corrected field: earnedInterest
      });
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to fetch savings data: $e';
      });
    }

    setState(() {
      _isLoading = false;
    });
  }

  @override
  void initState() {
    super.initState();
    _fetchSavings();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Savings Overview')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: <Widget>[
            if (_isLoading)
              const CircularProgressIndicator(),
            if (_errorMessage.isNotEmpty)
              Text(_errorMessage, style: const TextStyle(color: Colors.red)),
            if (!_isLoading && _errorMessage.isEmpty) ...[
              Text('Total Savings: \$$_savingsAmount'),
              Text('Earned Interest: \$$_earnedInterest'),
            ],
          ],
        ),
      ),
    );
  }
}
