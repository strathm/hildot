class TransactionModel {
  final String transactionId;
  final String userId;
  final double amount;
  final String type; // e.g., 'deposit', 'withdrawal', 'loan repayment'
  final DateTime date;
  final String status; // Added status field
  final String message; // Added message field

  // Constructor
  TransactionModel({
    required this.transactionId,
    required this.userId,
    required this.amount,
    required this.type,
    required this.date,
    required this.status,  // Include status in the constructor
    required this.message, // Include message in the constructor
  });

  // Factory method to create a TransactionModel from JSON data
  factory TransactionModel.fromJson(Map<String, dynamic> json) {
    return TransactionModel(
      transactionId: json['transactionId'] ?? '', // Default to empty string if missing
      userId: json['userId'] ?? '',               // Default to empty string if missing
      amount: json['amount'] != null ? (json['amount'] as num).toDouble() : 0.0, // Ensure double conversion
      type: json['type'] ?? '',                    // Default to empty string if missing
      date: json['date'] != null ? DateTime.parse(json['date']) : DateTime.now(), // Default to current date if missing
      status: json['status'] ?? '', // Default to empty string if missing
      message: json['message'] ?? '', // Default to empty string if missing
    );
  }

  // Method to convert the TransactionModel to JSON format
  Map<String, dynamic> toJson() {
    return {
      'transactionId': transactionId,
      'userId': userId,
      'amount': amount,
      'type': type,
      'date': date.toIso8601String(),
      'status': status, // Include status in the JSON
      'message': message, // Include message in the JSON
    };
  }
}
