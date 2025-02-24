import 'package:flutter/material.dart';

class MemberDashboardScreen extends StatelessWidget {
  const MemberDashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Member Dashboard')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: <Widget>[
            ElevatedButton(
              onPressed: () {
                Navigator.pushNamed(context, '/loan_application');
              },
              child: const Text('Apply for Loan'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.pushNamed(context, '/loan_status');
              },
              child: const Text('View Loan Status'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.pushNamed(context, '/savings');
              },
              child: const Text('View Savings & Earnings'),
            ),
          ],
        ),
      ),
    );
  }
}
