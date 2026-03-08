#app/routes/auth_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.config.roles import Roles
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# ------------------------
# Register
# ------------------------

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if User.objects(email=email).first():
            flash("Email already exists.", "danger")
            return redirect(url_for("auth.register"))

        user = User(
            name=name,
            email=email
        )

        user.set_password(password)
        user.save()

        flash("Registration successful. Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


# ------------------------
# Login
# ------------------------

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.objects(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Login successful.", "success")
            if current_user.role == Roles.ADMIN:
                return redirect(url_for("admin.dashboard"))
            elif current_user.role == Roles.PHARMACY:
                return redirect(url_for("pharmacy.medicines"))
            elif current_user.role == Roles.USER:
                return redirect(url_for("main.home"))
            else:
                pass

        flash("Invalid credentials.", "danger")

    return render_template("auth/login.html")


# ------------------------
# Logout
# ------------------------

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for("auth.login"))