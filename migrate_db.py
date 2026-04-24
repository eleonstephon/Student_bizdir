import sqlite3
import os

DATABASE_PATH = "bizdir.db"

def migrate():
    if not os.path.exists(DATABASE_PATH):
        print("❌ bizdir.db not found. Run python app.py first.")
        return

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    print("🔄 Starting Phase 2 migration...")

    # Step 1 — Create users table with Phase 2 requirements
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name     TEXT NOT NULL,
            email         TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            date_created  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ users table ready")

    # Step 2 — Add user_id column to businesses table
    # This uses PRAGMA to check if the column exists first to prevent errors
    existing_cols = [row[1] for row in cursor.execute("PRAGMA table_info(businesses)")]
    if "user_id" not in existing_cols:
        cursor.execute("ALTER TABLE businesses ADD COLUMN user_id INTEGER")
        print("✅ user_id column added to businesses")
    else:
        print("ℹ️  user_id column already exists — skipping")

    conn.commit()

    # Step 3 — Verification of your 48 businesses
    total = cursor.execute("SELECT COUNT(*) FROM businesses").fetchone()[0]
    print(f"\n📊 Migration complete:")
    print(f"   Businesses preserved: {total}")
    
    if total == 48:
        print("   ✅ All 48 businesses are safe and intact.")
    else:
        print(f"   ⚠️ Note: Database contains {total} businesses.")

    conn.close()

if __name__ == "__main__":
    migrate()