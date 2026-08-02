import os
import time
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import database
import re

# ==========================================
# ⚙️ APP SETUP
# ==========================================
app = Flask(__name__)
app.secret_key = "bizdirapp-hackathon-secret-2026"

# ==========================================
# 🔑 FLASK-LOGIN SETUP 
# ==========================================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login_page"
login_manager.login_message = "Please log in to access that page."
login_manager.login_message_category = "error"

# ==========================================
# ⭐ USER CLASS — Required by Flask-Login
# ==========================================
class User(UserMixin):
    def __init__(self, user_row):
        self.id            = user_row["id"]
        self.full_name     = user_row["full_name"]
        self.email         = user_row["email"]
        self.password_hash = user_row["password_hash"]

@login_manager.user_loader
def load_user(user_id):
    row = database.get_user_by_id(int(user_id))
    if row:
        return User(row)
    return None

# ==========================================
# 📁 FILE UPLOAD CONFIGURATION
# ==========================================
UPLOAD_FOLDER = os.path.join("static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ==========================================
# 📱 WHATSAPP NUMBER NORMALIZATION
# ==========================================
# WhatsApp's click-to-chat links (wa.me/<number>) need the FULL international
# number: country code + number, no leading 0, no "+", no spaces/dashes.
# Change this if StuBiz is used outside Ghana.
WHATSAPP_COUNTRY_CODE = "233"

def normalize_whatsapp(raw_number):
    """ Converts whatever the user typed into the wa.me-ready format. """
    digits = re.sub(r"\D", "", raw_number or "")
    if not digits:
        return ""
    if digits.startswith(WHATSAPP_COUNTRY_CODE):
        return digits
    if digits.startswith("0"):
        digits = digits[1:]
    return f"{WHATSAPP_COUNTRY_CODE}{digits}"

with app.app_context():
    database.init_db()

# ==========================================
# 🏠 ROUTE 1: GET / (Homepage)
# ==========================================
@app.route("/")
def homepage():
    search_query = request.args.get("search", "").strip()
    category_filter = request.args.get("category", "").strip()
    if search_query:
        businesses = database.search_businesses(search_query)
    elif category_filter:
        businesses = database.get_all_businesses(category=category_filter)
    else:
        businesses = database.get_all_businesses()
    return render_template("index.html", businesses=businesses, search_query=search_query, category_filter=category_filter)

# ==========================================
# 🏢 ROUTE 2: GET /business/<id> (Profile Page)
# ==========================================
@app.route("/business/<int:business_id>")
def business_profile(business_id):
    business = database.get_business_by_id(business_id)
    if business is None:
        return render_template("404.html"), 404
    return render_template("business.html", business=business)

# ==========================================
# 📝 ROUTE 4: GET+POST /signup (Create Account)
# ==========================================

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)


@app.route("/signup", methods=["GET", "POST"])
def signup_page():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email     = request.form.get("email", "").strip().lower()
        password  = request.form.get("password", "")
        confirm   = request.form.get("confirm_password", "")
        if not full_name or not email or not password:
            flash("All fields are required.", "error")
            return redirect(url_for("signup_page"))
        
        if not is_valid_email(email):
            flash("Please enter a valid email address.", "error")
            return redirect(url_for("signup_page"))

        if password != confirm:
            flash("Passwords do not match.", "error")
            return redirect(url_for("signup_page"))
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return redirect(url_for("signup_page"))
        hashed = generate_password_hash(password)
        new_id = database.create_user(full_name, email, hashed)
        if new_id is None:
            flash("An account with that email already exists.", "error")
            return redirect(url_for("signup_page"))
        flash("Account created! Please log in.", "success")
        return redirect(url_for("login_page"))
    return render_template("signup.html")

# ==========================================
# 🔑 ROUTE 5: GET+POST /login (Login)
# ==========================================
@app.route("/login", methods=["GET", "POST"])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user_row = database.get_user_by_email(email)
        if not user_row or not check_password_hash(user_row["password_hash"], password):
            flash("Invalid email or password.", "error")
            return redirect(url_for("login_page"))
        user = User(user_row)
        login_user(user)
        flash(f"Welcome back, {user.full_name}!", "success")
        return redirect(url_for("dashboard"))
    return render_template("login.html")

# ==========================================
# 🚪 ROUTE 6: GET /logout (Logout)
# ==========================================
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("homepage"))

# ==========================================
# 📊 ROUTE 7: GET /dashboard (User Dashboard)
# ==========================================
@app.route("/dashboard")
@login_required
def dashboard():
    businesses = database.get_businesses_by_user(current_user.id)
    return render_template("dashboard.html", businesses=businesses)

# ==========================================
# ➕ ROUTE 8: GET+POST /new-listing (Add Business)
# ==========================================
@app.route("/new-listing", methods=["GET", "POST"])
@login_required
def new_listing():
    if request.method == "POST":
        business_name = request.form.get("business_name", "").strip()
        category      = request.form.get("category", "").strip()
        description   = request.form.get("description", "").strip()
        whatsapp      = normalize_whatsapp(request.form.get("whatsapp", ""))
        phone         = request.form.get("phone", "").strip()
        location      = request.form.get("location", "").strip()
        delivers      = 1 if request.form.get("delivers") else 0

        if not business_name or not category or len(description) < 20:
            flash("Please fill in all fields correctly.", "error")
            return render_template("new_listing.html", form_data=request.form)

        photo_filename = ""
        photo_file = request.files.get("photo")
        if photo_file and photo_file.filename:
            if allowed_file(photo_file.filename):
                filename = secure_filename(photo_file.filename)
                unique_filename = f"biz_{int(time.time())}_{uuid.uuid4().hex[:8]}_{filename}"
                photo_file.save(os.path.join(app.config["UPLOAD_FOLDER"], unique_filename))
                photo_filename = unique_filename
            else:
                flash("That photo file type isn't supported (use PNG, JPG, JPEG, GIF, or WEBP). Your listing was saved without a photo.", "error")

        business_data = {
            "user_id": current_user.id,
            "business_name": business_name,
            "owner_name": current_user.full_name,
            "category": category,
            "description": description,
            "whatsapp": whatsapp,
            "phone": phone,
            "location": location,
            "delivers": delivers,
            "photo_filename": photo_filename,
            "is_verified": 1
        }
        database.add_business(business_data)
        flash("Business listed successfully!", "success")
        return redirect(url_for("dashboard"))
    return render_template("new_listing.html")

# ==========================================
# 🛡️ ROUTE 9: GET+POST /admin (Admin Panel)
# ==========================================
@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    if request.method == "POST":
        business_id = request.form.get("business_id")
        if business_id and business_id.isdigit():
            database.verify_business(int(business_id))
            flash(f"Business #{business_id} approved.", "success")
        return redirect(url_for("admin_panel"))
    pending = database.get_pending_businesses()
    return render_template("admin.html", pending=pending)

# ==========================================
# 🛠️ ROUTE 10: GET+POST /business/<id>/edit  (Edit Business) ⭐ PHASE 3
# ==========================================
@app.route("/business/<int:business_id>/edit", methods=["GET", "POST"])
@login_required
def edit_business(business_id):
    """ Allows owners to update their listings with ownership verification """
    business = database.get_business_by_id(business_id)

    # 🛑 CRITICAL SECURITY GATE: Check if user owns the business
    if not business or business['user_id'] != current_user.id:
        flash("Security Alert: You do not have permission to edit this listing.", "error")
        return redirect(url_for('dashboard'))

    if request.method == "POST":
        business_name = request.form.get("business_name", "").strip()
        category      = request.form.get("category", "").strip()
        description   = request.form.get("description", "").strip()
        whatsapp      = normalize_whatsapp(request.form.get("whatsapp", ""))
        phone         = request.form.get("phone", "").strip()
        location      = request.form.get("location", "").strip()
        delivers      = 1 if request.form.get("delivers") else 0

        # 🛑 Same validation rules as new_listing — edits shouldn't be able to
        # save a blank name/category or an under-length description.
        if not business_name or not category or len(description) < 20:
            flash("Please fill in all fields correctly (description must be at least 20 characters).", "error")
            return render_template("edit_business.html", business=business)

        updated_data = {
            "business_name": business_name,
            "category":      category,
            "description":   description,
            "whatsapp":      whatsapp,
            "phone":         phone,
            "location":      location,
            "delivers":      delivers
        }

        photo_file = request.files.get("photo")
        if photo_file and photo_file.filename:
            if allowed_file(photo_file.filename):
                filename = secure_filename(photo_file.filename)
                unique_filename = f"biz_{int(time.time())}_{uuid.uuid4().hex[:8]}_{filename}"
                photo_file.save(os.path.join(app.config["UPLOAD_FOLDER"], unique_filename))
                updated_data["photo_filename"] = unique_filename
            else:
                flash("That photo file type isn't supported (use PNG, JPG, JPEG, GIF, or WEBP). Your existing photo was kept.", "error")
                updated_data["photo_filename"] = business["photo_filename"]
        else:
            # No new photo selected — keep the existing one instead of wiping it out
            updated_data["photo_filename"] = business["photo_filename"]

        database.update_business(business_id, updated_data)
        flash("Business updated successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template("edit_business.html", business=business)

# ==========================================
# 🗑️ ROUTE 11: POST /business/<id>/delete  (Delete Business) ⭐ PHASE 3
# ==========================================
@app.route("/business/<int:business_id>/delete", methods=["POST"])
@login_required
def delete_business(business_id):
    """ Deletes a listing only after verifying ownership """
    business = database.get_business_by_id(business_id)

    # 🛑 CRITICAL SECURITY GATE: Check if user owns the business
    if not business or business['user_id'] != current_user.id:
        flash("Security Alert: You do not have permission to delete this listing.", "error")
        return redirect(url_for('dashboard'))

    # Clean up the uploaded photo on disk so deleted listings don't leave orphaned files
    if business["photo_filename"]:
        photo_path = os.path.join(app.config["UPLOAD_FOLDER"], business["photo_filename"])
        if os.path.exists(photo_path):
            os.remove(photo_path)

    database.delete_business(business_id)
    flash("Listing deleted successfully.", "success")
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    app.run(debug=True)