import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:mobile/models/loan_model.dart';

class LoanService {
  final String baseUrl = 'http://yourbackendapi.com/api/loans'; // Replace with your backend URL

  // Method for applying for a loan
  Future<LoanModel> applyForLoan(double amount, int termInMonths, double interestRate) async {
    final response = await http.post(
      Uri.parse('$baseUrl/apply'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'amount': amount,
        'termInMonths': termInMonths,
        'interestRate': interestRate,
      }),
    );

    if (response.statusCode == 201) {
      return LoanModel.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to apply for loan');
    }
  }

  // Method for checking loan status
  Future<LoanModel> getLoanStatus(String loanId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/$loanId'),
      headers: {'Content-Type': 'application/json'},
    );

    if (response.statusCode == 200) {
      return LoanModel.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to fetch loan status');
    }
  }

  // Method for approving a loan
  Future<void> approveLoan(String loanId) async {
    final response = await http.put(
      Uri.parse('$baseUrl/approve/$loanId'),
      headers: {'Content-Type': 'application/json'},
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to approve loan');
    }
  }
}
