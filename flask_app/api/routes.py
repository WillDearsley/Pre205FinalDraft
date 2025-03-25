import os
import json
from flask import render_template, request, make_response, Blueprint, url_for, flash, redirect, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, current_user
from flask_mail import Message

from flask_app import db, mail  # -------------------> THIS IS THE DATABASE ABJECT <------------------------------------
from flask_app.models import Users, Companies, Invoices
from datetime import datetime

api = Blueprint("api", __name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
with open(f"{APP_ROOT}/resources/sample.json") as f:
    tickers = json.load(f)

# endpoint for signing up users
@api.route("/signupendpoint", methods=["POST"])
def signupendpoint():
    email = request.form.get("email")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm-password")

    if not email or not password or not confirm_password:
        return "<div class='alert error'>All fields are required!</div>"

    if password != confirm_password:
        return "<div class='alert error'>Passwords do not match!</div>"

    if Users.query.filter_by(email=email).first():
        return "<div class='alert error'>Email already exists!</div>"

    hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
    new_user = Users(email=email, password=hashed_password, is_verified=False)
    db.session.add(new_user)
    db.session.commit()
    send_verification_email(new_user)

    return "<div class='alert success'>Account created! Please verify your email.</div>"


@api.route("/loginendpoint", methods=["POST"])
def loginendpoint():
    try:
        email = request.form.get("email")
        password = request.form.get("password")
        remember = True if request.form.get("remember") else False

        if not email or not password:
            return "<div class='alert error'>Please provide both email and password</div>"

        user = Users.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            return "<div class='alert error'>Invalid email or password</div>"

        if not user.is_verified:
            return "<div class='alert error'>Please verify your email before logging in</div>"

        login_user(user, remember=remember)

        return """
           <div class='alert success'>Login successful! Redirecting...</div>
           <script>
            setTimeout(function() {
                window.location.href = '/dashboard';
            }, 1000);
           </script>
           """
    except Exception as e:
        return f"<div class='alert error'>An error occurred: {str(e)}</div>"

def send_verification_email(user):
    token = user.generate_verification_token()
    confirm_url = url_for("api.verify_email", token=token, _external=True)
    print(f"Verification URL: {confirm_url}")  # <-- Log the generated URL
    subject = "Please Confirm Your Email"
    body = f"Click the link to verify your email: {confirm_url}"

    print(f"Sending verification email to: {user.email}")  # <-- Add a print or logging here
    msg = Message(subject, recipients=[user.email], body=body)
    try:
        mail.send(msg)
    except Exception as e:
        print(f"Error sending email: {str(e)}")

@api.route("/verify-email/<token>")
def verify_email(token):
    email = Users.verify_token(token)

    if not email:
        return "<div class='alert error'>Invalid or expired token</div>"

    user = Users.query.filter_by(email=email).first()

    if not user:
        return "<div class='alert error'>User not found</div>"

    if user.is_verified:
        return "<div class='alert success'>Your email is already verified</div>"

    user.is_verified = True
    db.session.commit()

    return "<div class='alert success'>Email verified successfully! You can now log in.</div>"

@api.route("/api/v1/search", methods=["POST"])
def search():
    search_term = request.form.get("search")

    if not len(search_term):
        return render_template("test_table.html", tickers=[])

    res_tickers = []
    for ticker in tickers["data"]:
        if search_term.lower() in ticker["name"].lower():
            res_tickers.append(ticker)

    return render_template("test_table.html", tickers=res_tickers)

# visit https://localhost:5000/users to see the users you added in terminal
@api.route("/users", methods=["GET"])
def get_users():
    # Fetch all users from the database
    users = Users.query.all()
    return {"users": [user.email for user in users]}

@api.route('/create-invoice', methods=['POST'])
@login_required
def create_invoice():
    current_company_id = session.get('current_company_id')
    if not current_company_id:
        return '<div class="text-red-500 text-sm">No company selected</div>', 400

    try:
        client_name = request.form.get('client_name')
        amount = float(request.form.get('amount'))
        due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d')
        status = request.form.get('status', 'pending')

        new_invoice = Invoices(
            company_id=current_company_id,
            client_name=client_name,
            amount=amount,
            due_date=due_date,
            status=status
        )
        db.session.add(new_invoice)
        db.session.commit()

        # Return HTML for the new invoice row
        return f'''
            <tr class="bg-white border-b dark:bg-gray-800 dark:border-gray-700">
                <td class="px-6 py-4 font-medium text-gray-900 dark:text-white">
                    #{new_invoice.invoice_number}
                </td>
                <td class="px-6 py-4 text-gray-900 dark:text-white">
                    {new_invoice.client_name}
                </td>
                <td class="px-6 py-4 text-gray-900 dark:text-white">
                    ${new_invoice.amount:,.2f}
                </td>
                <td class="px-6 py-4">
                    <span class="px-2 py-1 text-xs font-medium rounded-full 
                        {{
                            'paid': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
                            'pending': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
                            'overdue': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
                        }}[new_invoice.status]
                    ">
                        {new_invoice.status.title()}
                    </span>
                </td>
                <td class="px-6 py-4 text-gray-900 dark:text-white">
                    {new_invoice.due_date.strftime('%Y-%m-%d')}
                </td>
                <td class="px-6 py-4">
                    <button class="font-medium text-blue-600 dark:text-blue-500 hover:underline mr-3">Edit</button>
                    <button class="font-medium text-red-600 dark:text-red-500 hover:underline">Delete</button>
                </td>
            </tr>
        ''', 200

    except Exception as e:
        db.session.rollback()
        return f'<div class="text-red-500 text-sm">Error creating invoice: {str(e)}</div>', 400

@api.route('/update-email', methods=['POST'])
@login_required
def update_email():
    try:
        email = request.form.get('email')
        
        # Check if email is already taken
        if email != current_user.email and Users.query.filter_by(email=email).first():
            return '''
                <div class="p-4 mb-4 text-sm text-red-800 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400" role="alert">
                    Email already registered
                </div>
            ''', 400
        
        # Update email
        current_user.email = email
        db.session.commit()
        
        return '''
            <div class="p-4 mb-4 text-sm text-green-800 rounded-lg bg-green-50 dark:bg-gray-800 dark:text-green-400" role="alert">
                Email updated successfully
            </div>
        ''', 200
        
    except Exception as e:
        db.session.rollback()
        return f'''
            <div class="p-4 mb-4 text-sm text-red-800 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400" role="alert">
                Error updating email: {str(e)}
            </div>
        ''', 400

@api.route('/update-password', methods=['POST'])
@login_required
def update_password():
    try:
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Verify current password
        if not check_password_hash(current_user.password, current_password):
            return '''
                <div class="p-4 mb-4 text-sm text-red-800 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400" role="alert">
                    Current password is incorrect
                </div>
            ''', 400
        
        # Verify new password matches confirmation
        if new_password != confirm_password:
            return '''
                <div class="p-4 mb-4 text-sm text-red-800 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400" role="alert">
                    New passwords do not match
                </div>
            ''', 400
        
        # Update password
        current_user.password = generate_password_hash(new_password, method="pbkdf2:sha256")
        db.session.commit()
        
        return '''
            <div class="p-4 mb-4 text-sm text-green-800 rounded-lg bg-green-50 dark:bg-gray-800 dark:text-green-400" role="alert">
                Password updated successfully
            </div>
        ''', 200
        
    except Exception as e:
        db.session.rollback()
        return f'''
            <div class="p-4 mb-4 text-sm text-red-800 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400" role="alert">
                Error updating password: {str(e)}
            </div>
        ''', 400