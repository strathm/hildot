from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import User, Sacco, db

auth_bp = Blueprint("auth", __name__)

# User Registration
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json

    # Validate request data
    sacco_id = data.get("sacco_id")
    full_name = data.get("full_name")
    email = data.get("email")
    phone_number = data.get("phone_number")
    password = data.get("password")
    
    if not all([sacco_id, full_name, email, phone_number, password]):
        return jsonify({"message": "All fields are required"}), 400

    # Ensure the sacco exists before creating a user
    sacco = Sacco.query.get(sacco_id)
    if not sacco:
        return jsonify({"message": "Sacco not found"}), 400

    # Check if the email already exists
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 400

    # Hash the password
    hashed_password = generate_password_hash(password, method="sha256")

    # Create and save the new user
    user = User(
        sacco_id=sacco_id,
        full_name=full_name,
        email=email,
        phone_number=phone_number,
        password=hashed_password
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


# User Login
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json

    # Validate request data
    email = data.get("email")
    password = data.get("password")
    if not all([email, password]):
        return jsonify({"message": "Email and password are required"}), 400

    # Fetch user from database
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid email or password"}), 401

    # Generate JWT token
    access_token = create_access_token(identity={"id": user.id, "role": user.role})

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user_id": user.id
    }), 200


# Get Current User Info
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    current_user = get_jwt_identity()
    
    # Fetch user info from database
    user = User.query.get(current_user["id"])
    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "phone_number": user.phone_number,
        "role": user.role
    }), 200
