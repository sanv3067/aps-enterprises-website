import os
import sqlite3

from dotenv import load_dotenv
from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash
)
from werkzeug.security import check_password_hash

from database import create_database

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME")
ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH")

DATABASE = "aps_enterprises.db"

create_database()


@app.route("/")
def home():
    return render_template("index.html")


# CUSTOMER ENQUIRY
@app.route("/enquiry", methods=["POST"])
def submit_enquiry():

    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()
    service = request.form.get("service", "").strip()
    message = request.form.get("message", "").strip()

    if not name or not phone or not service or not message:
        return "Please fill all required fields.", 400

    if len(name) > 100 or len(phone) > 20 or len(email) > 150:
        return "Input is too long.", 400

    if len(service) > 100 or len(message) > 2000:
        return "Input is too long.", 400

    conn = sqlite3.connect(DATABASE)

    conn.execute("""
        INSERT INTO enquiries
        (name, phone, email, service, message)
        VALUES (?, ?, ?, ?, ?)
    """, (name, phone, email, service, message))

    conn.commit()
    conn.close()

    return """
    <h2>Thank you!</h2>
    <p>Your enquiry has been submitted successfully.</p>
    <a href="/">Back to Website</a>
    """


# ADMIN LOGIN
@app.route("/admin", methods=["GET", "POST"])
def admin_login():

    if not app.secret_key or not ADMIN_USERNAME or not ADMIN_PASSWORD_HASH:
        return "Admin security settings are not configured.", 503

    if request.method == "POST":

        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if username == ADMIN_USERNAME and check_password_hash(
            ADMIN_PASSWORD_HASH, password
        ):
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))

        return render_template(
            "admin_login.html",
            error="Invalid username or password"
        )

    return render_template("admin_login.html")


# ADMIN DASHBOARD
@app.route("/admin/dashboard")
def admin_dashboard():

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    enquiries = conn.execute("""
        SELECT * FROM enquiries
        ORDER BY created_at DESC
    """).fetchall()

    conn.close()

    return render_template(
        "admin_dashboard.html",
        enquiries=enquiries,
        enquiry_count=len(enquiries)
    )


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


if __name__ == "__main__":
    app.run(debug=True, port=5005)