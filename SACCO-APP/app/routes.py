from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from .models import db, User, Group, GroupMembers, Savings, Loan, Transaction
from .forms import LoginForm, RegistrationForm, CreateGroupForm, SavingsForm, LoanRequestForm
from .utils import assign_role, notify_user, generate_mpesa_request, record_transaction, distribute_interest_earnings
from flask import Blueprint
from app.utils import calculate_interest

bp = Blueprint('main', __name__)

# ---------------------- AUTH ROUTES ----------------------

@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(phone_number=form.phone_number.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("main.dashboard"))
        else:
            flash("Invalid credentials.", "danger")
    return render_template("login.html", form=form)

@bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(
            full_name=form.full_name.data,
            phone_number=form.phone_number.data,
            national_id=form.national_id.data,
            occupation=form.occupation.data,
            county=form.county.data,
            sub_county=form.sub_county.data,
            village_street=form.village_street.data,
            date_of_birth=form.date_of_birth.data
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)

@bp.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "Admin":
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for("dashboard"))

    return render_template("admin.html", group=current_user.group)

@bp.route("/admin/loan-requests")
@login_required
def view_loan_requests():
    if current_user.role != "Admin":
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for("main.dashboard"))
    
    # Query for all loan requests that are pending approval
    loan_requests = Loan.query.filter_by(status="Pending").all()
    return render_template("loan_requests.html", loan_requests=loan_requests)

@bp.route("/admin/manage-members/<int:group_id>")
@login_required
def manage_members(group_id):
    if current_user.role != "Admin":
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for("main.dashboard"))

    # Query for all members in the specified group
    members = GroupMembers.query.filter_by(group_id=group_id).all()
    return render_template("manage_members.html", members=members)


@bp.route("/transactions", methods=["GET"])
@login_required
def transactions():
    transaction_type = request.args.get("transaction_type", "all")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    # Query transactions based on filters
    query = Transaction.query.filter_by(user_id=current_user.id)

    if transaction_type != "all":
        query = query.filter_by(type=transaction_type)

    if start_date:
        query = query.filter(Transaction.date >= start_date)

    if end_date:
        query = query.filter(Transaction.date <= end_date)

    transactions = query.all()

    return render_template("transactions.html", transactions=transactions)


@bp.route("/loans", methods=["GET", "POST"])
@login_required
def loans():
    loan = Loan.query.filter_by(user_id=current_user.id, repayment_status="Pending").first()
    form = LoanRequestForm()
    mpesa_status = None

    # Handle loan request
    if form.validate_on_submit():
        amount = form.amount.data
        interest_rate = form.interest_rate.data
        new_loan = Loan(user_id=current_user.id, amount=amount, interest_rate=interest_rate, repayment_status="Pending")
        db.session.add(new_loan)
        db.session.commit()

        flash("Loan request submitted successfully!", "success")
        return redirect(url_for("loans"))

    # Handle loan repayment
    if request.method == "POST" and "amount" in request.form:
        amount_to_repay = request.form["amount"]
        
        mpesa_response = generate_mpesa_request(amount_to_repay, current_user.phone_number, "Loan Repayment")
        if mpesa_response["status"] == "Success":
            loan.amount_paid += float(amount_to_repay)
            if loan.amount_paid >= loan.amount:
                loan.repayment_status = "Paid"
            db.session.commit()

            # Record the transaction
            record_transaction(current_user.id, None, "Loan Repayment", amount_to_repay)
            mpesa_status = "M-Pesa transaction successful. Loan repayment recorded."
        else:
            mpesa_status = "M-Pesa transaction failed. Please try again."

    return render_template("loans.html", form=form, loan=loan, mpesa_status=mpesa_status)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

# ---------------------- MAIN ROUTES ----------------------

@bp.route("/")
def home():
    return render_template("index.html")

@bp.route("/dashboard")
@login_required
def dashboard():
    user_savings = Savings.query.filter_by(user_id=current_user.id).all()
    total_savings = sum(s.amount for s in user_savings)
    interest_earned = calculate_interest(current_user.id)  # Implement this function
    user_loans = Loan.query.filter_by(user_id=current_user.id).all()
    total_loans = sum(l.amount for l in user_loans)
    repayment_status = "Pending" if any(l.repayment_status == "Pending" for l in user_loans) else "Paid"
    user_group = GroupMembers.query.filter_by(user_id=current_user.id).first()
    group_name = user_group.group.name if user_group else "No Group"
    group_role = user_group.role if user_group else "None"
    
    return render_template("dashboard.html", total_savings=total_savings, interest_earned=interest_earned,
                           total_loans=total_loans, repayment_status=repayment_status,
                           group_name=group_name, group_role=group_role)


# ---------------------- SACCO/GROUP ROUTES ----------------------

@bp.route("/sacco/create", methods=["GET", "POST"])
@login_required
def create_sacco():
    form = CreateGroupForm()
    if form.validate_on_submit():
        new_group = Group(
            name=form.name.data,
            purpose=form.purpose.data,
            registration_number=form.registration_number.data,
            county=form.county.data,
            sub_county=form.sub_county.data,
            village_street=form.village_street.data,
            start_date=form.start_date.data,
            sacco_type=form.sacco_type.data,
            created_by=current_user.id  # Assuming the user who creates the group is the creator/admin
        )
        db.session.add(new_group)
        db.session.commit()

        # Assign the current user as an Admin for the newly created SACCO
        assign_role(current_user.id, new_group.id, "Admin")

        flash("SACCO created successfully!", "success")
        return redirect(url_for("dashboard"))
    
    return render_template("create.html", form=form)


@bp.route("/sacco/join/<int:group_id>")
@login_required
def join_sacco(group_id):
    existing_member = GroupMembers.query.filter_by(user_id=current_user.id, group_id=group_id).first()
    if existing_member:
        flash("You are already a member of this SACCO.", "info")
    else:
        membership = GroupMembers(user_id=current_user.id, group_id=group_id, role="Member")
        db.session.add(membership)
        db.session.commit()
        notify_user(current_user.id, "You have successfully joined the SACCO.")
        flash("Joined SACCO successfully!", "success")

    return redirect(url_for("dashboard"))

# ---------------------- TRANSACTIONS (SAVINGS & LOANS) ----------------------

@bp.route("/savings", methods=["GET", "POST"])
@login_required
def savings():
    form = SavingsForm()
    user_savings = Savings.query.filter_by(user_id=current_user.id).all()
    total_savings = sum(s.amount for s in user_savings)

    if form.validate_on_submit():
        mpesa_response = generate_mpesa_request(form.amount.data, current_user.phone_number, "Savings")
        if mpesa_response["status"] == "Success":
            new_savings = Savings(user_id=current_user.id, amount=form.amount.data)
            db.session.add(new_savings)
            db.session.commit()

            record_transaction(current_user.id, None, "Savings", form.amount.data)
            flash("Savings added successfully!", "success")
        else:
            flash("M-Pesa transaction failed.", "danger")

        return redirect(url_for("savings"))

    return render_template("savings.html", form=form, total_savings=total_savings)

@bp.route("/loan/request", methods=["GET", "POST"])
@login_required
def request_loan():
    form = LoanRequestForm()
    if form.validate_on_submit():
        new_loan = Loan(user_id=current_user.id, amount=form.amount.data, interest_rate=form.interest_rate.data)
        db.session.add(new_loan)
        db.session.commit()
        flash("Loan request submitted!", "success")

        return redirect(url_for("loans"))

    return render_template("request_loan.html", form=form)

@bp.route("/loan/pay", methods=["POST"])
@login_required
def pay_loan():
    amount = request.form.get("amount", type=float)
    
    mpesa_response = generate_mpesa_request(amount, current_user.phone_number, "Loan Repayment")
    if mpesa_response["status"] == "Success":
        loan = Loan.query.filter_by(user_id=current_user.id, repayment_status="Pending").first()
        if loan:
            loan.amount -= amount
            if loan.amount <= 0:
                loan.repayment_status = "Paid"
            db.session.commit()

            record_transaction(current_user.id, None, "Loan Repayment", amount)
            flash("Loan repaid successfully!", "success")
        else:
            flash("No pending loans found.", "info")
    else:
        flash("M-Pesa transaction failed.", "danger")

    return redirect(url_for("loans"))

@bp.route("/interest/distribute")
@login_required
def distribute_interest():
    distribute_interest_earnings(current_user.id)
    flash("Interest earnings distributed!", "success")
    return redirect(url_for("savings"))
