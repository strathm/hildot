from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Sacco, User, Loan, Meeting, MeetingAttendee, db
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

admin_bp = Blueprint("admin", __name__)

# Approve Loan
@admin_bp.route("/loan/approve/<int:loan_id>", methods=["POST"])
@jwt_required()
def approve_loan(loan_id):
    current_user = get_jwt_identity()
    user = User.query.get(current_user["id"])

    if user.role != "admin":
        return jsonify({"message": "Unauthorized"}), 403

    loan = Loan.query.get(loan_id)
    if not loan or loan.sacco_id != user.sacco_id:
        return jsonify({"message": "Loan not found or unauthorized"}), 404

    try:
        loan.status = "approved"
        loan.issued_at = datetime.utcnow()
        loan.due_date = loan.issued_at + timedelta(days=loan.duration_months * 30)
        loan.total_amount_due = loan.calculate_total_due()

        if loan.grace_period_days > 0:
            loan.due_date += timedelta(days=loan.grace_period_days)

        db.session.commit()
        return jsonify({
            "message": "Loan approved successfully",
            "total_amount_due": loan.total_amount_due
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

# Add Member
@admin_bp.route("/member/add", methods=["POST"])
@jwt_required()
def add_member():
    current_user = get_jwt_identity()
    user = User.query.get(current_user["id"])

    if user.role != "admin":
        return jsonify({"message": "Unauthorized"}), 403

    data = request.json
    if not data or not all(key in data for key in ["full_name", "email", "phone_number", "password"]):
        return jsonify({"message": "Missing required fields"}), 400

    # Ensure unique email and phone number
    existing_user = User.query.filter(
        (User.email == data["email"]) | (User.phone_number == data["phone_number"])
    ).first()
    if existing_user:
        return jsonify({"message": "User with this email or phone number already exists"}), 400

    try:
        new_member = User(
            sacco_id=user.sacco_id,
            full_name=data["full_name"],
            email=data["email"],
            phone_number=data["phone_number"],
            password=generate_password_hash(data["password"], method="sha256"),
        )
        db.session.add(new_member)
        db.session.commit()
        return jsonify({"message": "Member added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

# Schedule Meeting
@admin_bp.route("/meeting/schedule", methods=["POST"])
@jwt_required()
def schedule_meeting():
    current_user = get_jwt_identity()
    user = User.query.get(current_user["id"])

    if user.role != "admin":
        return jsonify({"message": "Unauthorized"}), 403

    data = request.json
    if not data or not all(key in data for key in ["title", "description", "meeting_date", "location"]):
        return jsonify({"message": "Missing required fields"}), 400

    try:
        meeting_date = datetime.strptime(data["meeting_date"], "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return jsonify({"message": "Invalid meeting_date format. Use 'YYYY-MM-DD HH:MM:SS'"}), 400

    try:
        meeting = Meeting(
            sacco_id=user.sacco_id,
            title=data["title"],
            description=data["description"],
            meeting_date=meeting_date,
            location=data["location"]
        )
        db.session.add(meeting)
        db.session.commit()
        return jsonify({"message": "Meeting scheduled successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

# Add Member to Meeting
@admin_bp.route("/meeting/add-member/<int:meeting_id>", methods=["POST"])
@jwt_required()
def add_member_to_meeting(meeting_id):
    current_user = get_jwt_identity()
    user = User.query.get(current_user["id"])

    if user.role != "admin":
        return jsonify({"message": "Unauthorized"}), 403

    meeting = Meeting.query.get(meeting_id)
    if not meeting or meeting.sacco_id != user.sacco_id:
        return jsonify({"message": "Meeting not found or unauthorized"}), 404

    data = request.json
    member_id = data.get("member_id")

    if not member_id:
        return jsonify({"message": "Missing member_id"}), 400

    member = User.query.get(member_id)
    if not member or member.sacco_id != user.sacco_id:
        return jsonify({"message": "Member not found or unauthorized"}), 404

    # Check if the member is already added to the meeting
    if MeetingAttendee.query.filter_by(meeting_id=meeting_id, user_id=member_id).first():
        return jsonify({"message": "Member already added to the meeting"}), 400

    try:
        attendee = MeetingAttendee(
            meeting_id=meeting_id,
            user_id=member_id
        )
        db.session.add(attendee)
        db.session.commit()
        return jsonify({"message": "Member added to meeting successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500
