import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:mobile/models/earnings_model.dart';

class EarningsService {
  final String baseUrl = 'http://yourbackendapi.com/api/earnings'; // Replace with your backend URL

  // Method for fetching earnings
  Future<EarningsModel> fetchEarnings(String userId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/$userId'),
      headers: {'Content-Type': 'application/json'},
    );

    if (response.statusCode == 200) {
      return EarningsModel.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to fetch earnings');
    }
  }
}
