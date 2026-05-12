import sqlite3  
import os       


# CONFIGURATION
DATABASE_PATH = "bizdir.db"

# DATABASE SCHEMA
SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name     TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    date_created  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS businesses (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER,
    business_name  TEXT NOT NULL,
    owner_name     TEXT NOT NULL,
    category       TEXT NOT NULL,
    description    TEXT NOT NULL,
    whatsapp       TEXT,
    phone          TEXT,
    location       TEXT,
    delivers       INTEGER DEFAULT 0,
    photo_filename TEXT,
    date_added     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_verified    INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
"""

# ==========================================
# ⚙️ CORE DATABASE FUNCTIONS
# ==========================================

def get_connection():
    """ Opens and returns a connection to the SQLite database. """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  
    return conn

def init_db():
    """ Creates the database tables if they don't already exist. """
    conn = get_connection()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
    print("✅ Database initialized — businesses table is ready.")

# ==========================================
# 🏢 BUSINESS LISTING FUNCTIONS
# ==========================================

def get_all_businesses(category=None):
    conn = get_connection()
    if category:
        rows = conn.execute(
            "SELECT * FROM businesses WHERE is_verified = 1 AND category = ? ORDER BY date_added DESC",
            (category,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM businesses WHERE is_verified = 1 ORDER BY date_added DESC"
        ).fetchall()
    conn.close()
    return rows

def get_business_by_id(business_id):
    """ Returns a single business by its ID number. """
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM businesses WHERE id = ?",
        (business_id,)
    ).fetchone()
    conn.close()
    return row

def search_businesses(query):
    """ Searches verified businesses by name, description, or category. """
    if not query:
        return get_all_businesses()

    words = query.strip().split()
    conn = get_connection()
    conditions = []
    params = []
    for word in words:
        term = f"%{word}%"
        conditions.append("(business_name LIKE ? OR description LIKE ? OR category LIKE ?)")
        params.extend([term, term, term])

    where_clause = " OR ".join(conditions)
    rows = conn.execute(
        f"SELECT * FROM businesses WHERE is_verified = 1 AND ({where_clause}) ORDER BY date_added DESC",
        params
    ).fetchall()
    conn.close()
    return rows

def add_business(data):
    """ Inserts a new business into the database. """
    conn = get_connection()
    # FIXED: Corrected syntax and typo 'uer_id' to 'user_id'
    cursor = conn.execute(
        """
        INSERT INTO businesses
            (user_id, business_name, owner_name, category, description,
             whatsapp, phone, location, delivers, photo_filename, is_verified)
        VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.get("user_id"),
            data["business_name"],
            data["owner_name"],
            data["category"],
            data["description"],
            data.get("whatsapp", ""),
            data.get("phone", ""),
            data.get("location", ""),
            data.get("delivers", 0),
            data.get("photo_filename", ""),
            data.get("is_verified", 1)
        )
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

# ==========================================
# 👤 USER MANAGEMENT FUNCTIONS
# ==========================================

def create_user(full_name, email, password_hash):
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO users (full_name, email, password_hash) VALUES (?, ?, ?)",
            (full_name, email, password_hash)
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def get_user_by_email(email):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return row

def get_user_by_id(user_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return row

def get_businesses_by_user(user_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM businesses WHERE user_id = ? ORDER BY date_added DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return rows

# ==========================================
# 🛡️ ADMIN & PHASE 3 SECURITY FUNCTIONS
# ==========================================

def verify_business(business_id):
    conn = get_connection()
    cursor = conn.execute("UPDATE businesses SET is_verified = 1 WHERE id = ?", (business_id,))
    conn.commit()
    rows_changed = cursor.rowcount
    conn.close()
    return rows_changed > 0

def get_pending_businesses():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM businesses WHERE is_verified = 0 ORDER BY date_added ASC").fetchall()
    conn.close()
    return rows

# --- NEW PHASE 3 FUNCTIONS ADDED BELOW ---

def update_business(business_id, data):
    """ 
    FUNCTION 13: Integrations Lead logic to update business records.
    Ensures that edits made in app.py are saved to the database.
    """
    conn = get_connection()
    conn.execute(
        """
        UPDATE businesses 
        SET business_name = ?, category = ?, description = ?, 
            whatsapp = ?, phone = ?, location = ?, delivers = ?, photo_filename = ?
        WHERE id = ?
        """,
        (
            data['business_name'], data['category'], data['description'],
            data['whatsapp'], data['phone'], data['location'], 
            data['delivers'], data.get('photo_filename', ""), business_id
        )
    )
    conn.commit()
    conn.close()

def delete_business(business_id):
    """ 
    FUNCTION 14: Integrations Lead logic to remove a business listing.
    Triggered after ownership security check passes in app.py.
    """
    conn = get_connection()
    conn.execute("DELETE FROM businesses WHERE id = ?", (business_id,))
    conn.commit()
    conn.close()