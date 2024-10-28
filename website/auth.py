import string
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import *
from .email import sendEmail
from . import db
from random import choice

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect to home page if the user is verified, or remove account if authenticated but not verified
    if current_user.is_authenticated:
        if current_user.isVerified:
            return redirect(url_for("views.quizzes"))
        else:
            db.session.delete(current_user)
            db.session.commit()
            logout_user()

    if request.method == "POST":
        # Get submitted form data
        email = request.form.get("email")
        password = request.form.get("password")

        # Check if the user exists and the password is correct, reloading the login page if not
        user = User.query.filter_by(email=email).first()
        if user is None or not check_password_hash(user.passwordHash, password):
            flash("The email or password entered is incorrect.", "danger")
            return redirect(url_for("auth.login"))

        # Log-in user if username and password matched for some account, and direct to home page
        login_user(user)
        flash("You have successfully logged in.", "success")
        return redirect(url_for("views.quizzes"))

    return render_template("authentication/login.html")

@auth.route('/logout')
def logout():
    # Redirect to the log-in page if the user is not authenticated
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))
    
    logout_user()
    flash("You have logged out.", "success")
    return redirect(url_for("auth.login"))

@auth.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if current_user.is_authenticated:
        if current_user.isVerified:
            return redirect(url_for("views.quizzes"))
        else:
            db.session.delete(current_user)
            db.session.commit()
            logout_user()

    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if len(username) < 3:
            flash('Username must be at least 3 characters', category="danger")
            return redirect(url_for("auth.sign_up"))

        if password1 != password2:
            flash('Passwords do not match', category="danger")
            return redirect(url_for("auth.sign_up"))
        
        if len(password1) < 7:
            flash('Password must be at least 7 characters', category="danger")
            return redirect(url_for("auth.sign_up"))
        
        user = User.query.filter_by(email = email).first()
        if user is not None   :
            flash("This email is already registered to another account. Please use a different one", category = "danger")
            return redirect(url_for("auth.sign_up"))  
        
        user = User.query.filter_by(username = username).first()
        if user is not None   :
            flash("This username is already taken. Please use a different one", category = "danger")
            return redirect(url_for("auth.sign_up"))

        #add user to database
        user = User(username = username, email = email, passwordHash = generate_password_hash(password1))
        db.session.add(user)
        db.session.commit()
        flash('Account created', category="success")
        login_user(user)

        return sendVerifyEmail()


    return render_template('authentication/sign_up.html')

@auth.route("/verifyEmail", methods=['POST', 'GET'])
def verifyEmail():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))
    
    if current_user.isVerified:
        return redirect(url_for("views.quizzes"))
    
    if request.method == "POST":
        if request.form.get("code") == session['verifyCode']:
            current_user.isVerified = True
            db.session.commit()
            flash("Your account has been verified.", category="success")
            return redirect(url_for("views.quizzes"))
        else:
            flash("The verification code entered was incorrect.", category="danger")
            return redirect(url_for("auth.verifyEmail"))
        
    return render_template("authentication/verify-email.html")

@auth.route("/sendVerifyEmail", methods=['POST', 'GET'])
def sendVerifyEmail():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))
    
    if current_user.isVerified:
        return redirect(url_for("views.quizzes"))
    
    verifyCode = "".join([choice(string.ascii_letters + string.digits) for i in range(6)])
    session['verifyCode'] = verifyCode

    sendEmail("Email Verification for UWCS Quiz app", "noreplycs261@gmail.com", current_user.email, f"<h1>Your verification code is <b>{verifyCode}<b>.<h1>")
    
    flash(f"A 6-character verification code has been sent to {current_user.email}.", "success")
    return redirect(url_for("auth.verifyEmail"))