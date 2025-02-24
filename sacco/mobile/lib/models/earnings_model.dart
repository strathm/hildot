class EarningsModel {
  final String userId;
  final double earnings;

  EarningsModel({
    required this.userId,
    required this.earnings,
  });

  // Factory method to create an EarningsModel from JSON data
  factory EarningsModel.fromJson(Map<String, dynamic> json) {
    return EarningsModel(
      userId: json['userId'] ?? '', // Default to empty string if userId is missing
      earnings: json['earnings'] != null ? (json['earnings'] as num).toDouble() : 0.0, // Default to 0.0 if earnings is missing or invalid
    );
  }

  // Method to convert the EarningsModel to JSON format
  Map<String, dynamic> toJson() {
    return {
      'userId': userId,
      'earnings': earnings,
    };
  }

  // Getter for total earnings
  double get totalEarnings => earnings;
}
