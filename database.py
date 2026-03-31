
import sqlite3  
import os       


# CONFIGURATION

# This is the path to our database file.
# It will be created automatically when init_db() runs for the first time.
DATABASE_PATH = "bizdir.db"


# DATABASE SCHEMA

# This is the SQL that creates the businesses table.
# Think of a table like a spreadsheet — each field is a column.
# This runs once when the app starts (see init_db below).

SCHEMA = """
CREATE TABLE IF NOT EXISTS businesses (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    business_name   TEXT NOT NULL,
    owner_name      TEXT NOT NULL,
    category        TEXT NOT NULL,
    description     TEXT NOT NULL,
    whatsapp        TEXT,
    phone           TEXT,
    location        TEXT,
    delivers        INTEGER DEFAULT 0,
    photo_filename  TEXT,
    date_added      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_verified     INTEGER DEFAULT 0
);
"""

# FIELD EXPLANATIONS:
#   id              — Auto-generated unique number for each business (1, 2, 3...)
#   business_name   — e.g. "Amara's Braids"
#   owner_name      — e.g. "Amara Johnson"
#   category        — e.g. "Food", "Fashion", "Tech"
#   description     — At least 20 chars (enforced in app.py validation)
#   whatsapp        — Optional contact number
#   phone           — Optional phone number
#   location        — Optional e.g. "Block C, Room 12"
#   delivers        — 0 = No, 1 = Yes (stored as integer, not true/false)
#   photo_filename  — Just the filename e.g. "photo_abc123.jpg" (NOT full path)
#   date_added      — Auto-set to current time when row is inserted
#   is_verified     — 0 = pending review, 1 = approved and visible
#                     THIS IS YOUR SECURITY FEATURE — show judges this!


# FUNCTION 1: get_connection()


def get_connection():
    """
    Opens and returns a connection to the SQLite database.

    WHY row_factory?
      By default, sqlite3 returns rows as plain tuples like (1, "Amara's Braids", ...)
      With Row factory, you can access columns BY NAME like: row["business_name"]
      This makes the rest of the code much easier to read and write.

    CALLED BY: every other function in this file.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Lets us use row["column_name"] syntax
    return conn


# FUNCTION 2: init_db()

def init_db():
    """
    Creates the database tables if they don't already exist.

    WHEN IS THIS CALLED?
      Once at app startup (in app.py, before the first request).
      If bizdir.db already exists with the table, nothing changes.
      The "CREATE TABLE IF NOT EXISTS" in SCHEMA makes it safe to run repeatedly.

    HOW IT WORKS:
      conn.executescript() runs multiple SQL statements at once.
      conn.commit() saves the changes permanently to the file.
    """
    conn = get_connection()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
    print("✅ Database initialized — businesses table is ready.")


# FUNCTION 3: get_all_businesses()

def get_all_businesses(category=None):
    """
    Returns all VERIFIED businesses, newest first.

    WHY only verified?
      is_verified = 1 means the business has been approved.
      is_verified = 0 means it's still pending review.
      We never show unverified listings to the public. - Security feature!

    OPTIONAL: category filter
      If category is passed (e.g. "Food"), only Food businesses are returned.
      This powers the /?category=Food URL filter.

    PARAMETERIZED QUERIES — the (?,) syntax:
      We use ? placeholders and pass values as a tuple.
      This is how you PREVENT SQL INJECTION. -security feature!
      NEVER do: f"WHERE category = '{category}'"  ← vulnerable to SQL injection
      ALWAYS do: "WHERE category = ?", (category,)  ← safe

    RETURNS: list of Row objects (act like dictionaries)
    """
    conn = get_connection()

    if category:
        # Filter by category AND only show verified listings
        rows = conn.execute(
            "SELECT * FROM businesses WHERE is_verified = 1 AND category = ? ORDER BY date_added DESC",
            (category,)   # ← Parameterized query — SQL injection safe ⭐
        ).fetchall()
    else:
        # Return all verified listings, newest first
        rows = conn.execute(
            "SELECT * FROM businesses WHERE is_verified = 1 ORDER BY date_added DESC"
        ).fetchall()

    conn.close()
    return rows


# FUNCTION 4: get_business_by_id(id)

def get_business_by_id(business_id):
    """
    Returns a single business by its ID number.

    USED BY: the /business/<id> route to show a business profile page.

    fetchone() returns one row (or None if not found).
    fetchall() returns a list — we don't use that here since IDs are unique.

    RETURNS: a single Row object, or None if no business has that ID.
    """
    conn = get_connection()

    row = conn.execute(
        "SELECT * FROM businesses WHERE id = ?",
        (business_id,)  # ← Parameterized — always use this for user-supplied values ⭐
    ).fetchone()

    conn.close()
    return row  # Could be None — app.py must handle that case (show 404 page)


# FUNCTION 5: search_businesses(query)

def search_businesses(query):
    """
    Searches verified businesses by name, description, or category.

    HOW LIKE WORKS IN SQL:
      % is a wildcard meaning "anything here"
      So  %braids%  matches:  "Amara's Braids", "Best Braids in Town", "Braids by Kate"
      We wrap the query in % on both sides to find it anywhere in the text.

    USED BY: the homepage when the AI search fails (fallback search).

    RETURNS: list of matching Row objects.
    """
    # Wrap in % wildcards for partial matching
    search_term = f"%{query}%"

    conn = get_connection()

    rows = conn.execute(
        """
        SELECT * FROM businesses
        WHERE is_verified = 1
          AND (
              business_name LIKE ?   OR
              description   LIKE ?   OR
              category      LIKE ?
          )
        ORDER BY date_added DESC
        """,
        (search_term, search_term, search_term)  # ← Safe parameterized query 
    ).fetchall()

    conn.close()
    return rows


# FUNCTION 6: add_business(data)

def add_business(data):
    """
    Inserts a new business registration into the database.

    CALLED BY: the POST /register route in app.py, AFTER validation passes.

    WHAT 'data' LOOKS LIKE (a dictionary from app.py):
    {
        "business_name":  "Amara's Braids",
        "owner_name":     "Amara Johnson",
        "category":       "Fashion",
        "description":    "Affordable braiding services on campus",
        "whatsapp":       "0712345678",
        "phone":          "0712345678",
        "location":       "Block C, Room 12",
        "delivers":       0,
        "photo_filename": "photo_abc123.jpg"   ← just the filename, not the full path
    }

    NOTE: is_verified is NOT in the data dict — it defaults to 0 in the schema.
    New listings always start as unverified (pending). ⭐ Security feature!

    RETURNS: the ID of the newly inserted row (useful for redirecting to the profile).
    """
    conn = get_connection()

    cursor = conn.execute(
        """
        INSERT INTO businesses
            (business_name, owner_name, category, description,
             whatsapp, phone, location, delivers, photo_filename)
        VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["business_name"],
            data["owner_name"],
            data["category"],
            data["description"],
            data.get("whatsapp", ""),        # .get() returns "" if key is missing
            data.get("phone", ""),
            data.get("location", ""),
            data.get("delivers", 0),
            data.get("photo_filename", "")
        )
        # Every value is passed as a parameter — never concatenated into the SQL string
    )

    conn.commit()           # Save changes to disk
    new_id = cursor.lastrowid  # The auto-generated ID of the new row
    conn.close()
    return new_id


# FUNCTION 7: verify_business(business_id)   ← BONUS: Admin feature

def verify_business(business_id):
    """
    Sets is_verified = 1 for a business, making it publicly visible.

    USED BY: the /admin route in app.py.
    This is the "approval" step in your security system. 

    RETURNS: True if a row was updated, False if ID not found.
    """
    conn = get_connection()

    cursor = conn.execute(
        "UPDATE businesses SET is_verified = 1 WHERE id = ?",
        (business_id,)
    )

    conn.commit()
    rows_changed = cursor.rowcount  # How many rows were updated (0 or 1)
    conn.close()
    return rows_changed > 0


# FUNCTION 8: get_pending_businesses()   ← BONUS: Admin feature

def get_pending_businesses():
    """
    Returns all businesses that are NOT yet verified (is_verified = 0).

    USED BY: the /admin route so you can see what needs approval.

    RETURNS: list of Row objects with is_verified = 0.
    """
    conn = get_connection()

    rows = conn.execute(
        "SELECT * FROM businesses WHERE is_verified = 0 ORDER BY date_added ASC"
    ).fetchall()

    conn.close()
    return rows