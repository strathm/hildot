class LoanModel {
  final String loanId;
  final double amount;
  final double interestRate;
  final int termInMonths;
  final double balance;
  final String status; // e.g., 'approved', 'pending', 'repaid'
  final double loanBalance; // Field to store the loan balance (if you want it separately)
  final String repaymentStatus; // Field to store repayment status (e.g., 'pending', 'paid')

  LoanModel({
    required this.loanId,
    required this.amount,
    required this.interestRate,
    required this.termInMonths,
    required this.balance,
    required this.status,
    required this.loanBalance,   // Add loanBalance to the constructor
    required this.repaymentStatus, // Add repaymentStatus to the constructor
  });

  // Factory method to create a LoanModel from JSON data
  factory LoanModel.fromJson(Map<String, dynamic> json) {
    return LoanModel(
      loanId: json['loanId'] ?? '', 
      amount: json['amount'] != null ? (json['amount'] as num).toDouble() : 0.0, 
      interestRate: json['interestRate'] != null ? (json['interestRate'] as num).toDouble() : 0.0, 
      termInMonths: json['termInMonths'] ?? 0, 
      balance: json['balance'] != null ? (json['balance'] as num).toDouble() : 0.0, 
      status: json['status'] ?? 'unknown', 
      loanBalance: json['loanBalance'] != null ? (json['loanBalance'] as num).toDouble() : 0.0,  // Add loanBalance logic
      repaymentStatus: json['repaymentStatus'] ?? 'pending',  // Default to 'pending' if missing
    );
  }

  // Method to convert the LoanModel to JSON format
  Map<String, dynamic> toJson() {
    return {
      'loanId': loanId,
      'amount': amount,
      'interestRate': interestRate,
      'termInMonths': termInMonths,
      'balance': balance,
      'status': status,
      'loanBalance': loanBalance,  // Add loanBalance to the JSON
      'repaymentStatus': repaymentStatus, // Add repaymentStatus to the JSON
    };
  }
}
