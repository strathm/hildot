from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Savings, Loan, LoanRepayment, Transaction, InterestDistribution, Meeting, MeetingAttendee, Notification, db

member_bp = Blueprint("member", __name__)

# View Savings
@member_bp.route("/savings", methods=["GET"])
@jwt_required()
def view_savings():
    current_user = get_jwt_identity()
    savings = Savings.query.filter_by(user_id=current_user["id"]).all()
    
    total_savings = sum(s.amount for s in savings)
    total_earnings = sum(s.total_earnings or 0 for s in savings)  # Handle None values

    return jsonify({
        "total_savings": total_savings,
        "total_earnings": total_earnings
    }), 200

# Apply for Loan
@member_bp.route("/loan/apply", methods=["POST"])
@jwt_required()
def apply_loan():
    current_user = get_jwt_identity()
    data = request.get_json()

    if not data or not all(key in data for key in ["principal_amount", "interest_rate", "duration_months"]):
        return jsonify({"message": "Missing required fields"}), 400

    if not current_user.get("sacco_id"):
        return jsonify({"message": "User must be associated with a SACCO"}), 400

    try:
        loan = Loan(
            sacco_id=current_user["sacco_id"],
            user_id=current_user["id"],
            principal_amount=data["principal_amount"],
            interest_rate=data["interest_rate"],
            duration_months=data["duration_months"],
            status="pending"
        )
        db.session.add(loan)
        db.session.commit()
        return jsonify({"message": "Loan application submitted successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

# Repay Loan
@member_bp.route("/loan/repay/<int:loan_id>", methods=["POST"])
@jwt_required()
def repay_loan(loan_id):
    current_user = get_jwt_identity()
    loan = Loan.query.get(loan_id)
    
    if not loan or loan.user_id != current_user["id"]:
        return jsonify({"message": "Loan not found or unauthorized"}), 404

    data = request.get_json()
    repayment_amount = data.get("repayment_amount")

    if not repayment_amount or repayment_amount <= 0 or repayment_amount > loan.total_amount_due:
        return jsonify({"message": "Invalid repayment amount"}), 400

    try:
        loan_repayment = LoanRepayment(
            loan_id=loan_id,
            repayment_amount=repayment_amount
        )
        db.session.add(loan_repayment)

        loan.total_amount_due -= repayment_amount
        if loan.total_amount_due <= 0:
            loan.status = "paid"
        
        db.session.commit()
        return jsonify({"message": "Loan repayment successful"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

# View Transactions
@member_bp.route("/transactions", methods=["GET"])
@jwt_required()
def view_transactions():
    current_user = get_jwt_identity()
    transactions = Transaction.query.filter_by(user_id=current_user["id"]).all()
    return jsonify([{
        "amount": t.amount,
        "transaction_type": t.transaction_type,
        "created_at": t.created_at.isoformat()
    } for t in transactions]), 200

# View Interest Distribution
@member_bp.route("/interest-distribution", methods=["GET"])
@jwt_required()
def view_interest_distribution():
    current_user = get_jwt_identity()
    distributions = InterestDistribution.query.filter_by(user_id=current_user["id"]).all()
    return jsonify([{
        "total_interest_earned": d.total_interest_earned,
        "distributed_at": d.distributed_at.isoformat()
    } for d in distributions]), 200

# View Meetings
@member_bp.route("/meetings", methods=["GET"])
@jwt_required()
def view_meetings():
    current_user = get_jwt_identity()
    meetings = Meeting.query.filter_by(sacco_id=current_user["sacco_id"]).all()
    return jsonify([{
        "title": m.title,
        "meeting_date": m.meeting_date.isoformat(),
        "location": m.location,
        "description": m.description
    } for m in meetings]), 200

# Attend Meeting
@member_bp.route("/meeting/attend/<int:meeting_id>", methods=["POST"])
@jwt_required()
def attend_meeting(meeting_id):
    current_user = get_jwt_identity()
    meeting = Meeting.query.get(meeting_id)
    if not meeting or meeting.sacco_id != current_user["sacco_id"]:
        return jsonify({"message": "Meeting not found or unauthorized"}), 404

    if MeetingAttendee.query.filter_by(meeting_id=meeting_id, user_id=current_user["id"]).first():
        return jsonify({"message": "Already marked as attended"}), 400

    try:
        attendee = MeetingAttendee(
            meeting_id=meeting_id,
            user_id=current_user["id"]
        )
        db.session.add(attendee)
        db.session.commit()
        return jsonify({"message": "Attendance recorded successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

# View Notifications
@member_bp.route("/notifications", methods=["GET"])
@jwt_required()
def view_notifications():
    current_user = get_jwt_identity()
    notifications = Notification.query.filter_by(user_id=current_user["id"], is_read=False).all()
    return jsonify([{
        "message": n.message,
        "created_at": n.created_at.isoformat()
    } for n in notifications]), 200

# Mark Notification as Read
@member_bp.route("/notification/read/<int:notification_id>", methods=["POST"])
@jwt_required()
def mark_notification_as_read(notification_id):
    current_user = get_jwt_identity()
    notification = Notification.query.get(notification_id)
    if not notification or notification.user_id != current_user["id"]:
        return jsonify({"message": "Notification not found or unauthorized"}), 404

    try:
        notification.is_read = True
        db.session.commit()
        return jsonify({"message": "Notification marked as read"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500
