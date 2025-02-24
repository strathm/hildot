import 'dart:convert';
import 'package:http/http.dart' as http;

class SavingsService {
  final String baseUrl = 'http://yourbackendapi.com/api/savings'; // Replace with your backend URL

  // Method for making a deposit into savings
  Future<void> depositToSavings(double amount, String userId) async {
    final response = await http.post(
      Uri.parse('$baseUrl/deposit'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'amount': amount, 'userId': userId}),
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to deposit into savings');
    }
  }

  // Method for withdrawing from savings
  Future<void> withdrawFromSavings(double amount, String userId) async {
    final response = await http.post(
      Uri.parse('$baseUrl/withdraw'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'amount': amount, 'userId': userId}),
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to withdraw from savings');
    }
  }

  // Method for calculating interest earned on savings
  Future<double> calculateInterest(String userId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/calculate-interest/$userId'),
      headers: {'Content-Type': 'application/json'},
    );

    if (response.statusCode == 200) {
      return double.parse(response.body);
    } else {
      throw Exception('Failed to calculate interest');
    }
  }
}
