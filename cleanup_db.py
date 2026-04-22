import sqlite3
import os

# 1. Path to your uploads and database
upload_dir = "static/uploads"
db_path = "bizdir.db"

# 2. Get list of actual files
actual_files = os.listdir(upload_dir)

# 3. Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 4. Find businesses where the photo_filename is NOT in our folder
cursor.execute("SELECT id, business_name, photo_filename FROM businesses")
all_businesses = cursor.fetchall()

to_delete = []
for biz in all_businesses:
    if biz[2] not in actual_files:
        to_delete.append(biz[0])
        print(f"🗑️ Marking for removal: {biz[1]} (Missing: {biz[2]})")

# 5. Delete them
if to_delete:
    cursor.executemany("DELETE FROM businesses WHERE id = ?", [(d,) for d in to_delete])
    conn.commit()
    print(f"\n✅ Successfully removed {len(to_delete)} broken listings.")
else:
    print("\n✨ No broken listings found!")

conn.close()