class SavingsModel {
  final String userId;
  final double balance; // Use balance instead of savings
  final double earnedInterest; // Use earnedInterest instead of interest

  SavingsModel({
    required this.userId,
    required this.balance,
    required this.earnedInterest,
  });

  // Factory method to create a SavingsModel from JSON data
  factory SavingsModel.fromJson(Map<String, dynamic> json) {
    return SavingsModel(
      userId: json['userId'] ?? '', // Default to empty string if userId is missing
      balance: json['balance'] != null ? (json['balance'] as num).toDouble() : 0.0, // Ensure double conversion, default to 0.0
      earnedInterest: json['earnedInterest'] != null ? (json['earnedInterest'] as num).toDouble() : 0.0, // Default to 0.0
    );
  }

  // Method to convert the SavingsModel to JSON format
  Map<String, dynamic> toJson() {
    return {
      'userId': userId,
      'balance': balance,
      'earnedInterest': earnedInterest,
    };
  }
}
