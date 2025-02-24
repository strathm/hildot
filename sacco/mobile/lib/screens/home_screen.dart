import 'package:flutter/material.dart';
import 'login_screen.dart';
import 'register_screen.dart';

class HomeScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Welcome to Your SACCO Platform"),
        backgroundColor: Colors.green,  // A color often associated with financial services
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Add an image or icon representing SACCO
              Image.asset(
                'assets/images/sacco_logo.png',  // Replace with your logo path
                width: 100,
                height: 100,
              ),
              SizedBox(height: 20),
              
              // Welcome message and description of the platform
              Text(
                "Join us today and start managing your savings and loans in a secure and transparent environment.",
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 18, color: Colors.black54),
              ),
              SizedBox(height: 30),

              // Button for Login
              ElevatedButton(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => LoginScreen()),
                  );
                },
                child: Text("Login"),
                style: ElevatedButton.styleFrom(
                  padding: EdgeInsets.symmetric(horizontal: 50, vertical: 15),
                  primary: Colors.blue, // Blue color for login
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10),
                  ),
                ),
              ),
              SizedBox(height: 10),

              // Button for Registration
              ElevatedButton(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => RegisterScreen()),
                  );
                },
                child: Text("Register"),
                style: ElevatedButton.styleFrom(
                  padding: EdgeInsets.symmetric(horizontal: 50, vertical: 15),
                  primary: Colors.green, // Green color for register
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10),
                  ),
                ),
              ),

              // Optional: Add a "Learn More" button
              SizedBox(height: 20),
              TextButton(
                onPressed: () {
                  // Add action for learning more about the SACCO
                },
                child: Text(
                  "Learn More About Us",
                  style: TextStyle(fontSize: 16, color: Colors.blue),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
