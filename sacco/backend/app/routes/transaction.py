from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Transaction, Savings, Loan, db

transaction_bp = Blueprint("transaction", __name__)

# Record Deposit
@transaction_bp.route("/deposit", methods=["POST"])
@jwt_required()
def deposit():
    current_user = get_jwt_identity()
    data = request.json

    # Validate required fields
    if not data or not all(key in data for key in ["amount", "sacco_id", "mpesa_reference"]):
        return jsonify({"message": "Missing required fields"}), 400

    amount = data["amount"]
    if amount <= 0:
        return jsonify({"message": "Amount must be greater than zero"}), 400

    try:
        # Record transaction
        transaction = Transaction(
            sacco_id=data["sacco_id"],
            user_id=current_user["id"],
            amount=amount,
            transaction_type="deposit",
            mpesa_reference=data["mpesa_reference"]
        )
        db.session.add(transaction)

        # Update savings or create new if not present
        saving = Savings.query.filter_by(user_id=current_user["id"], sacco_id=data["sacco_id"]).first()
        if saving:
            saving.amount += amount
        else:
            saving = Savings(user_id=current_user["id"], sacco_id=data["sacco_id"], amount=amount)
            db.session.add(saving)

        db.session.commit()
        return jsonify({"message": "Deposit successful"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500


# Loan Repayment
@transaction_bp.route("/loan/repay", methods=["POST"])
@jwt_required()
def repay_loan():
    current_user = get_jwt_identity()
    data = request.json

    # Validate required fields
    if not data or not all(key in data for key in ["loan_id", "amount", "mpesa_reference"]):
        return jsonify({"message": "Missing required fields"}), 400

    loan = Loan.query.get(data["loan_id"])
    if not loan or loan.user_id != current_user["id"]:
        return jsonify({"message": "Loan not found or unauthorized"}), 404

    repayment_amount = data["amount"]
    if repayment_amount <= 0:
        return jsonify({"message": "Repayment amount must be greater than zero"}), 400

    try:
        # Adjust loan balance
        loan.total_amount_due -= repayment_amount
        if loan.total_amount_due <= 0:
            loan.status = "paid"
            loan.total_amount_due = 0  # Ensure it does not go negative

        # Record transaction
        transaction = Transaction(
            sacco_id=loan.sacco_id,
            user_id=current_user["id"],
            amount=repayment_amount,
            transaction_type="loan_repayment",
            mpesa_reference=data["mpesa_reference"]
        )
        db.session.add(transaction)

        # Optionally update savings balance (if repayment affects savings)
        savings = Savings.query.filter_by(user_id=current_user["id"], sacco_id=loan.sacco_id).first()
        if savings and savings.amount >= repayment_amount:
            savings.amount -= repayment_amount
        elif savings:
            return jsonify({"message": "Insufficient savings balance to complete repayment"}), 400

        db.session.commit()
        return jsonify({"message": "Loan repayment successful"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500
