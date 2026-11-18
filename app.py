import os

from dotenv import load_dotenv
from pathlib import Path
from flask import (
    Flask, render_template, request,
    redirect, url_for, session
)
from werkzeug.security import check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME")
ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH")

# Supabase PostgreSQL connection
database_url = os.environ.get("DATABASE_URL", "sqlite:///aps_enterprises.db")

if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
    database_url = database_url.replace(
    "postgresql://", "postgresql+psycopg://", 1
)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}

db = SQLAlchemy(app)


class Enquiry(db.Model):
    __tablename__ = "enquiries"

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    phone = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text)
    service = db.Column(db.Text, nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.now()
    )


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    project_folder = Path(app.static_folder) / "images" / "projects"

    categories = {
        "electrical": "Electrical Works",
        "fabrication": "Fabrication Works",
        "flooring": "Flooring Works",
        "interior": "Interior Works",
        "wallpaper": "Wallpaper Works"
    }

    projects = {}

    for folder, title in categories.items():
        folder_path = project_folder / folder

        photos = []
        if folder_path.exists():
            photos = sorted(
                file.name for file in folder_path.iterdir()
                if file.is_file()
                and file.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]
            )

        projects[title] = [
            f"images/projects/{folder}/{photo}"
            for photo in photos
        ]

    return render_template("index.html", projects=projects)
@app.route("/projects/<category>")
def project_gallery(category):

    categories = {
        "electrical": "Electrical Works",
        "fabrication": "Fabrication Works",
        "flooring": "Flooring Works",
        "interior": "Interior Works",
        "wallpaper": "Wallpaper Works"
    }

    if category not in categories:
        return "Category Not Found", 404

    folder = Path(app.static_folder) / "images" / "projects" / category

    photos = sorted(
        file.name for file in folder.iterdir()
        if file.is_file()
        and file.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]
    )

    return render_template(
        "project_gallery.html",
        title=categories[category],
        photos=photos,
        category=category
    )



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

    enquiry = Enquiry(
        name=name,
        phone=phone,
        email=email,
        service=service,
        message=message
    )

    db.session.add(enquiry)
    db.session.commit()

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

    records = Enquiry.query.order_by(
        Enquiry.created_at.desc()
    ).all()

    enquiries = [
        {
            "id": item.id,
            "name": item.name,
            "phone": item.phone,
            "email": item.email,
            "service": item.service,
            "message": item.message,
            "created_at": item.created_at
        }
        for item in records
    ]

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