
import os
import time
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import database

# APP SETUP


app = Flask(__name__)
app.secret_key = "bizdirapp-hackathon-secret-2026"

# FLASK-LOGIN SETUP 

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login_page"  # redirect here if @login_required fails
login_manager.login_message = "Please log in to access that page."
login_manager.login_message_category = "error"

# USER CLASS — Required by Flask-Login ⭐

class User(UserMixin):
    """
    Flask-Login needs a User class with these properties.
    UserMixin provides default implementations of:
    - is_authenticated (True if logged in)
    - is_active (True by default)
    - is_anonymous (False if logged in)
    - get_id() (returns self.id as string)
    """
    def init(self, user_row):
        self.id           = user_row["id"]
        self.full_name    = user_row["full_name"]
        self.email        = user_row["email"]
        self.password_hash = user_row["password_hash"]


@login_manager.user_loader
def load_user(user_id):
    """
    Flask-Login calls this on EVERY request to get the current user.
    Must return a User object or None.
    """
    row = database.get_user_by_id(int(user_id))
    if row:
        return User(row)
    return None


# FILE UPLOAD CONFIGURATION

UPLOAD_FOLDER = os.path.join("static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# HELPER: File type validation 

def allowed_file(filename):
    """
    Returns True if the file has an allowed image extension.
    Prevents malicious file uploads.
    """
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# DATABASE SETUP

with app.app_context():
    database.init_db()


# ROUTE 1: GET /  (Homepage)

@app.route("/")
def homepage():
    """
    The main landing page showing all verified business listings.
    Supports search and category filter.
    """
    search_query = request.args.get("search", "").strip()
    category_filter = request.args.get("category", "").strip()

    if search_query:
        try:
            from ai_search import ai_search
            businesses = ai_search(search_query)
        except Exception:
            businesses = database.search_businesses(search_query)

    elif category_filter:
        businesses = database.get_all_businesses(category=category_filter)

    else:
        businesses = database.get_all_businesses()

    return render_template(
        "index.html",
        businesses=businesses,
        search_query=search_query,
        category_filter=category_filter
    )


# ROUTE 2: GET /business/<id>  (Business Profile Page)

@app.route("/business/<int:business_id>")
def business_profile(business_id):
    """
    Shows the full profile page for a single business.
    Returns 404 if business not found.
    """
    business = database.get_business_by_id(business_id)

    if business is None:
        return render_template("404.html"), 404

    return render_template("business.html", business=business)


# ROUTE 3: GET /register  (Old Registration — kept for compatibility)

@app.route("/register")
def register_page():
    """
    Redirects old /register URL to new /signup page.
    Kept for backwards compatibility.
    """
    return redirect(url_for("signup_page"))


# ROUTE 4: GET+POST /signup  (Create Account) 

@app.route("/signup", methods=["GET", "POST"])
def signup_page():
    """
    Shows signup form and handles account creation.

    SECURITY FEATURES:
    - Password is hashed using Werkzeug — never stored as plain text 
    - Duplicate emails rejected (UNIQUE constraint in database)
    - Password minimum length enforced
    - Passwords must match confirmation
    """
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))  # already logged in

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email     = request.form.get("email", "").strip().lower()
        password  = request.form.get("password", "")
        confirm   = request.form.get("confirm_password", "")

        # Validation
        if not full_name or not email or not password:
            flash("All fields are required.", "error")
            return redirect(url_for("signup_page"))

        if password != confirm:
            flash("Passwords do not match.", "error")
            return redirect(url_for("signup_page"))

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return redirect(url_for("signup_page"))

        # Hash the password — NEVER store plain text ⭐ Security feature
        hashed = generate_password_hash(password)

        # Save to database
        new_id = database.create_user(full_name, email, hashed)

        if new_id is None:
            flash("An account with that email already exists.", "error")
            return redirect(url_for("signup_page"))

        flash("Account created! Please log in.", "success")
        return redirect(url_for("login_page"))

    return render_template("signup.html")


# ROUTE 5: GET+POST /login  (Login) ⭐ Phase 2

@app.route("/login", methods=["GET", "POST"])
def login_page():
    """
    Shows login form and handles authentication.

    SECURITY FEATURES:
    - Password checked against hash using check_password_hash ⭐
    - Plain text password never stored or compared directly
    - Generic error messages (don't reveal if email exists)
    """
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))  # already logged in

    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # Find user by email
        user_row = database.get_user_by_email(email)

        if not user_row:
            flash("No account found with that email.", "error")
            return redirect(url_for("login_page"))
 # Check password against stored hash ⭐ Security feature
        if not check_password_hash(user_row["password_hash"], password):
            flash("Incorrect password.", "error")
            return redirect(url_for("login_page"))

        # Log the user in — Flask-Login handles the session
        user = User(user_row)
        login_user(user)

        flash(f"Welcome back, {user.full_name}!", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


# ROUTE 6: GET /logout  (Logout) 


@app.route("/logout")
@login_required
def logout():
    """
    Logs the current user out and redirects to homepage.
    @login_required means only logged-in users can access this.
    """
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("homepage"))


# ROUTE 7: GET /dashboard  (User Dashboard) ⭐ Phase 2

@app.route("/dashboard")
@login_required
def dashboard():
    """
    Shows the logged-in user's own business listings.
    @login_required redirects to /login if not authenticated.

    VARIABLES SENT TO TEMPLATE:
    - businesses: list of user's own businesses
    - current_user: Flask-Login provides this automatically
      (current_user.full_name, current_user.email etc.)
    """
    businesses = database.get_businesses_by_user(current_user.id)
    return render_template("dashboard.html", businesses=businesses)



# ROUTE 8: GET+POST /new-listing  (Add Business) 


@app.route("/new-listing", methods=["GET", "POST"])
@login_required
def new_listing():
    """
    Allows logged-in users to add a new business listing.
    Replaces the old /register route.

    KEY DIFFERENCE FROM OLD REGISTER:
    - user_id is set from current_user.id (logged-in user)
    - owner_name is set from current_user.full_name automatically
    - Redirects to dashboard after successful submission
    """
    if request.method == "POST":
        business_name = request.form.get("business_name", "").strip()
        category      = request.form.get("category", "").strip()
        description   = request.form.get("description", "").strip()
        whatsapp      = request.form.get("whatsapp", "").strip()
        phone         = request.form.get("phone", "").strip()
        location      = request.form.get("location", "").strip()
        delivers      = 1 if request.form.get("delivers") else 0

        # Validation
        errors = []
        if not business_name:
            errors.append("Business name is required.")
        if not category:
            errors.append("Please select a category.")
        if len(description) < 20:
            errors.append("Description must be at least 20 characters.")

        valid_categories = ["Food", "Fashion", "Beauty", "Tech", "Tutoring", "Art", "Other"]
        if category and category not in valid_categories:
            errors.append("Please select a valid category.")

        if errors:
            for error in errors:
                flash(error, "error")
            return redirect(url_for("new_listing"))

        # Handle photo upload
        photo_filename = ""
        photo_file = request.files.get("photo")

        if photo_file and photo_file.filename:
            if not allowed_file(photo_file.filename):
                flash("Only image files are allowed (PNG, JPG, GIF, WEBP).", "error")
                return redirect(url_for("new_listing"))

            safe_name = secure_filename(photo_file.filename)
            unique_filename = f"biz_{int(time.time())}_{safe_name}"
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
            photo_file.save(save_path)
            photo_filename = unique_filename

# Save to database
        business_data = {
            "user_id":        current_user.id,
            "business_name":  business_name,
            "owner_name":     current_user.full_name,  # from logged-in user
            "category":       category,
            "description":    description,
            "whatsapp":       whatsapp,
            "phone":          phone,
            "location":       location,
            "delivers":       delivers,
            "photo_filename": photo_filename,
            "is_verified":    1  # Auto-verify for prototype
        }

        database.add_business(business_data)
        flash("Business listed successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("new_listing.html")


# ROUTE 9: GET+POST /admin  (Admin Panel)

@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    """
    Admin page for approving pending business listings.
    """
    if request.method == "POST":
        business_id = request.form.get("business_id")

        if business_id and business_id.isdigit():
            success = database.verify_business(int(business_id))
            if success:
                flash(f"✅ Business #{business_id} approved and now live.", "success")
            else:
                flash(f"❌ Business #{business_id} not found.", "error")
        else:
            flash("Invalid business ID.", "error")

        return redirect(url_for("admin_panel"))

    pending = database.get_pending_businesses()
    return render_template("admin.html", pending=pending)


# RUN THE APP


if __name__ == "__main__":
    app.run(debug=True)