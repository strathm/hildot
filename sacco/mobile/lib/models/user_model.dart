class UserModel {
  final String id;
  final String username;
  final String email;
  final String role; // 'admin' or 'member'

  UserModel({
    required this.id,
    required this.username,
    required this.email,
    required this.role,
  });

  // Factory method to create a UserModel from JSON data
  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'] ?? '',  // Ensure defaults if values are missing
      username: json['username'] ?? '',
      email: json['email'] ?? '',
      role: json['role'] ?? 'member',  // Default to 'member' if role is not provided
    );
  }

  // Method to convert the UserModel to JSON format
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': username,
      'email': email,
      'role': role,
    };
  }
}
