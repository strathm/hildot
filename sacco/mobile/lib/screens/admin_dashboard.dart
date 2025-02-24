import 'package:flutter/material.dart';

class AdminDashboardScreen extends StatelessWidget {
  const AdminDashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Admin Dashboard')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            ElevatedButton(
              onPressed: () {
                Navigator.pushNamed(context, '/add_member');
              },
              child: const Text('Add Member'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.pushNamed(context, '/loan_approval');
              },
              child: const Text('Approve Loan Applications'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.pushNamed(context, '/view_savings');
              },
              child: const Text('View Members Savings'),
            ),
          ],
        ),
      ),
    );
  }
}
