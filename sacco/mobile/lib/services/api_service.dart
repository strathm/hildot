import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:mobile/models/user_model.dart';
import 'package:mobile/models/earnings_model.dart';
import 'package:mobile/models/loan_model.dart';
import 'package:mobile/models/savings_model.dart';
import 'package:mobile/models/transaction_model.dart';

class ApiService {
  final String baseUrl = 'http://127.0.0.1:5000'; // Replace with your backend URL

  // Helper method to handle HTTP requests with a timeout
  Future<http.Response> _getRequest(String url) async {
    try {
      final response = await http.get(Uri.parse(url)).timeout(const Duration(seconds: 10));
      return response;
    } catch (e) {
      throw Exception('Failed to make GET request: $e');
    }
  }

  // Helper method to handle POST requests with a timeout
  Future<http.Response> _postRequest(String url, Map<String, dynamic> body) async {
    try {
      final response = await http.post(
        Uri.parse(url),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(body),
      ).timeout(const Duration(seconds: 10));
      return response;
    } catch (e) {
      throw Exception('Failed to make POST request: $e');
    }
  }

  // Method for login
  Future<UserModel> login(String email, String password) async {
    final response = await _postRequest(
      '$baseUrl/auth/login',
      {'email': email, 'password': password},
    );

    if (response.statusCode == 200) {
      return UserModel.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to log in: ${response.body}');
    }
  }

  // Method for registration
  Future<UserModel> register(String fullName, String email, String phoneNumber, String password, String saccoId) async {
    final response = await _postRequest(
      '$baseUrl/auth/register',
      {
        'full_name': fullName,
        'email': email,
        'phone_number': phoneNumber,
        'password': password,
        'sacco_id': saccoId,
      },
    );

    if (response.statusCode == 201) {
      return UserModel.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to register: ${response.body}');
    }
  }

  // Method for fetching user data
  Future<UserModel> fetchUserData(String userId) async {
    final response = await _getRequest('$baseUrl/users/$userId');

    if (response.statusCode == 200) {
      return UserModel.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to fetch user data: ${response.body}');
    }
  }

  // Method for fetching earnings data
  Future<EarningsModel> getEarnings(String userId) async {
    final response = await _getRequest('$baseUrl/earnings/$userId');

    if (response.statusCode == 200) {
      return EarningsModel.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to fetch earnings data: ${response.body}');
    }
  }

  // Method for applying for a loan
  Future<LoanModel> applyForLoan(String userId, double amount) async {
    final response = await _postRequest(
      '$baseUrl/loans/apply',
      {'userId': userId, 'amount': amount},
    );

    if (response.statusCode == 201) {
      return LoanModel.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to apply for loan: ${response.body}');
    }
  }

  // Method for fetching loan status
  Future<LoanModel> getLoanStatus(String loanId) async {
    final response = await _getRequest('$baseUrl/loans/$loanId');

    if (response.statusCode == 200) {
      return LoanModel.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to fetch loan status: ${response.body}');
    }
  }

  // Method for fetching savings data
  Future<SavingsModel> getSavings(String userId) async {
    final response = await _getRequest('$baseUrl/savings/$userId');

    if (response.statusCode == 200) {
      return SavingsModel.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to fetch savings data: ${response.body}');
    }
  }

  // Method for making a transaction
  Future<TransactionModel> makeTransaction(String userId, double amount) async {
    final response = await _postRequest(
      '$baseUrl/transactions',
      {'userId': userId, 'amount': amount},
    );

    if (response.statusCode == 201) {
      return TransactionModel.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to make transaction: ${response.body}');
    }
  }
}
