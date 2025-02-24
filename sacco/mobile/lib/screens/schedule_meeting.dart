import 'package:flutter/material.dart';
import 'package:mobile/services/meeting_service.dart';

class ScheduleMeetingScreen extends StatefulWidget {
  @override
  _ScheduleMeetingScreenState createState() => _ScheduleMeetingScreenState();
}

class _ScheduleMeetingScreenState extends State<ScheduleMeetingScreen> {
  final _formKey = GlobalKey<FormState>();
  final _dateController = TextEditingController();
  final _timeController = TextEditingController();
  final String userId = "your-user-id";  // Replace with actual user ID

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Schedule a Meeting"),
      ),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              TextFormField(
                controller: _dateController,
                decoration: InputDecoration(labelText: 'Meeting Date (YYYY-MM-DD)'),
                validator: (value) {
                  if (value!.isEmpty) {
                    return 'Please enter the date of the meeting';
                  }
                  return null;
                },
              ),
              TextFormField(
                controller: _timeController,
                decoration: InputDecoration(labelText: 'Meeting Time (HH:MM)'),
                validator: (value) {
                  if (value!.isEmpty) {
                    return 'Please enter the time of the meeting';
                  }
                  return null;
                },
              ),
              SizedBox(height: 20),
              ElevatedButton(
                onPressed: () {
                  if (_formKey.currentState!.validate()) {
                    MeetingService.scheduleMeeting(
                      _dateController.text,
                      _timeController.text,
                      userId,
                    ).then((success) {
                      if (success) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(content: Text('Meeting scheduled successfully')),
                        );
                        Navigator.pop(context);
                      } else {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(content: Text('Failed to schedule meeting')),
                        );
                      }
                    });
                  }
                },
                child: Text("Schedule Meeting"),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
