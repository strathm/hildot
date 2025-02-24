import 'dart:convert';
import 'package:http/http.dart' as http;

class MeetingService {
  static const String baseUrl = "https://your-backend-url.com/api";  // Replace with your backend URL

  // Schedule a meeting
  static Future<bool> scheduleMeeting(String date, String time, String userId) async {
    final response = await http.post(
      Uri.parse('$baseUrl/meeting/schedule'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'user_id': userId,
        'date': date,
        'time': time,
      }),
    );

    if (response.statusCode == 200) {
      return true;
    } else {
      print("Failed to schedule meeting: ${response.body}");
      return false;
    }
  }

  // Get meetings for a user
  static Future<List<dynamic>> getMeetings(String userId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/meeting/$userId'),
      headers: {'Content-Type': 'application/json'},
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      print("Failed to fetch meetings: ${response.body}");
      return [];
    }
  }
}
