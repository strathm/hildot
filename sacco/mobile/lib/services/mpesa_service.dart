import 'dart:convert';
import 'package:http/http.dart' as http;

class MpesaService {
  final String baseUrl = 'http://yourbackendapi.com/api/mpesa'; // Replace with your backend URL

  // Method for initiating a payment through M-Pesa
  Future<void> initiatePayment(double amount, String phoneNumber) async {
    final response = await http.post(
      Uri.parse('$baseUrl/payment'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'amount': amount, 'phoneNumber': phoneNumber}),
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to initiate M-Pesa payment');
    }
  }

  // Method for verifying a payment status
  Future<void> verifyPayment(String transactionId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/verify/$transactionId'),
      headers: {'Content-Type': 'application/json'},
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to verify payment');
    }
  }
}
