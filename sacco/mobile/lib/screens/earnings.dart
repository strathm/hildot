import 'package:flutter/material.dart';
import 'package:mobile/services/api_service.dart';
import 'package:mobile/models/earnings_model.dart';  // Ensure EarningsModel is public

class EarningsScreen extends StatefulWidget {
  const EarningsScreen({super.key});

  @override
  _EarningsScreenState createState() => _EarningsScreenState();
}

class _EarningsScreenState extends State<EarningsScreen> {
  bool _isLoading = false;
  String _errorMessage = '';
  EarningsModel? _earnings;

  // Method to get earnings
  void _getEarnings(String userId) async {
    setState(() {
      _isLoading = true;
      _errorMessage = '';
    });

    try {
      // Create an instance of ApiService
      ApiService apiService = ApiService();

      // Call the ApiService to fetch earnings
      final earnings = await apiService.getEarnings(userId);

      if (earnings != null) {
        setState(() {
          _earnings = earnings;
        });
      } else {
        setState(() {
          _errorMessage = 'Failed to fetch earnings.';
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Error fetching earnings: $e';
      });
    }

    setState(() {
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Earnings')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: <Widget>[
            ElevatedButton(
              onPressed: _isLoading ? null : () => _getEarnings('user123'), // Example userId
              child: _isLoading ? const CircularProgressIndicator() : const Text('Get Earnings'),
            ),
            if (_errorMessage.isNotEmpty)
              Text(_errorMessage, style: const TextStyle(color: Colors.red)),
            if (_earnings != null)
              // Access _earnings directly without null check
              Text('Total Earnings: \$${_earnings?.totalEarnings.toStringAsFixed(2)}'),
          ],
        ),
      ),
    );
  }
}
