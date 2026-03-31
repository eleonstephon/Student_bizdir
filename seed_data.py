"""
seed_data.py — Student BizDir
Run this script to populate the database with sample business listings.
"""

import sqlite3
import os

DATABASE_PATH = "bizdir.db"

# Sample business data with all required fields
# Each tuple: (business_name, owner_name, category, description, whatsapp, phone, location, delivers, photo_filename, is_verified)
sample_businesses = [
    # ========== BEAUTY & SKINCARE (10 businesses) ==========
    ("Cecilia's Glow Skincare", "Cecilia Mensah", "Beauty & Skincare",
     "Natural handmade skincare products – organic shea butter, facial scrubs, and body oils made by a level 300 student.",
     "0241234567", "0556789012", "Women's Common Room, Central Hall", 1, "glow_skincare.jpg", 1),
    
    ("HairCraft", "Abena Serwaa", "Beauty & Skincare",
     "Natural hair braiding, styling, and wig making. Book your appointment online or visit our salon.",
     "0209988776", "0241122334", "Hall 2, Common Room", 0, "haircraft.jpg", 1),
    
    ("Nail Haven", "Ama Serwaa", "Beauty & Skincare",
     "Professional manicure, pedicure, and nail art services. Affordable student prices.",
     "0245566778", "0551122334", "Central Cafeteria, 2nd Floor", 0, "nail_haven.jpg", 1),
    
    ("Fresh Face Spa", "Esi Amponsah", "Beauty & Skincare",
     "Facial treatments, acne solutions, and relaxation massages for students.",
     "0278899001", "0501234567", "Near Main Gate", 0, "fresh_face.jpg", 1),
    
    ("The Barber Spot", "Kwame Adjei", "Beauty & Skincare",
     "Professional haircuts, beard trimming, and grooming services.",
     "0241112223", "0203334445", "Hall 7, Basement", 0, "barber_spot.jpg", 1),
    
    ("Lash & Brow Studio", "Nana Ama", "Beauty & Skincare",
     "Eyelash extensions, eyebrow threading, and tinting services.",
     "0547778889", "0249990001", "Unity Hall, Room 5", 0, "lash_studio.jpg", 1),
    
    ("Organic Roots", "Yaa Asantewaa", "Beauty & Skincare",
     "100% natural and organic skincare products made on campus.",
     "0554445556", "0206667778", "Science Block, Lab 3", 1, "organic_roots.jpg", 1),
    
    ("Makeup by Efia", "Efia Osei", "Beauty & Skincare",
     "Professional makeup services for events, parties, and photoshoots.",
     "0247778889", "0559990001", "Hall 5, Room 12", 0, "makeup_efia.jpg", 1),
    
    ("Scent & Soul", "Adwoa Boatemaa", "Beauty & Skincare",
     "Handmade perfumes, body sprays, and essential oils.",
     "0201112223", "0543334445", "Arts Centre", 1, "scent_soul.jpg", 1),
    
    ("Glow Up Clinic", "Dr. Mensah", "Beauty & Skincare",
     "Skincare consultations and treatments for acne, hyperpigmentation, and more.",
     "0556667778", "0248889990", "Health Centre", 0, "glow_clinic.jpg", 1),

    # ========== FOOD & DRINKS (10 businesses) ==========
    ("Campus Chili Kitchen", "Kwame Asare", "Food & Drinks",
     "Spicy homemade chili with jollof rice, available daily at the science cafeteria. Special orders available for events.",
     "0547890123", "0204567890", "Science Cafeteria, near Block B", 1, "chili_kitchen.jpg", 1),
    
    ("Fit Eats", "Esi Amankwah", "Food & Drinks",
     "Healthy meal preps – grilled chicken, mixed vegetables, and fresh smoothies delivered to your hostel.",
     "0278899001", "0551122334", "Delivery only (campus-wide)", 1, "fit_eats.jpg", 1),
    
    ("Sweet Tooth Bakery", "Ama Dadson", "Food & Drinks",
     "Freshly baked cookies, cakes, and pastries. Custom orders for birthdays and events.",
     "0241234567", "0509876543", "Central Cafeteria", 1, "sweet_tooth.jpg", 1),
    
    ("Java Junction", "Kwabena Osei", "Food & Drinks",
     "Specialty coffee, teas, and light snacks. Study-friendly atmosphere.",
     "0541112223", "0204445556", "Library Annex", 0, "java_junction.jpg", 1),
    
    ("Tasty Bites", "Akua Serwaa", "Food & Drinks",
     "Waakye, fried rice, and local dishes prepared fresh daily.",
     "0245556667", "0557778889", "Hall 4, Food Court", 1, "tasty_bites.jpg", 1),
    
    ("Smoothie Bar", "Kofi Mensah", "Food & Drinks",
     "Fresh fruit smoothies, protein shakes, and healthy juices.",
     "0208889990", "0541112223", "Sports Complex", 0, "smoothie_bar.jpg", 1),
    
    ("Pizza Palace", "Yaw Boateng", "Food & Drinks",
     "Student-friendly pizzas with various toppings. Late-night delivery available.",
     "0553334445", "0246667778", "Night Market", 1, "pizza_palace.jpg", 1),
    
    ("Nana's Kitchen", "Nana Yeboah", "Food & Drinks",
     "Authentic Ghanaian home-cooked meals. Daily specials posted on WhatsApp.",
     "0249990001", "0552223334", "Hall 2, Room 8", 1, "nanas_kitchen.jpg", 1),
    
    ("Coffee & Code", "Kojo Asare", "Food & Drinks",
     "Coffee shop with charging ports and quiet spaces for coders and students.",
     "0544445556", "0207778889", "ICT Hub", 0, "coffee_code.jpg", 1),
    
    ("Frozen Delights", "Akosua Adjei", "Food & Drinks",
     "Ice cream, frozen yogurt, and milkshakes. Perfect for hot campus days.",
     "0501112223", "0243334445", "Recreational Centre", 0, "frozen_delights.jpg", 1),

    # ========== TECH & SERVICES (9 businesses) ==========
    ("TechFix Solutions", "Michael Osei", "Tech & Services",
     "Phone screen repairs, laptop troubleshooting, and software installation. Free diagnostics for students.",
     "0204567890", "0249876543", "ICT Centre, Room 12", 0, "techfix.jpg", 1),
    
    ("JS Tutorial Hub", "Yaw Asare", "Tech & Services",
     "Coding lessons for beginners – Python, JavaScript, and web development. One-on-one tutoring available.",
     "0591122334", "0201234567", "Library Study Room 3", 0, "tutorial_hub.jpg", 1),
    
    ("PC Doctors", "Nii Armah", "Tech & Services",
     "Computer repairs, virus removal, and hardware upgrades. Free diagnostics.",
     "0241112223", "0554445556", "ICT Centre, Room 5", 0, "pc_doctors.jpg", 1),
    
    
    
    ("Web Wizards", "Kojo Annan", "Tech & Services",
     "Website design and development for student businesses and projects.",
     "0556667778", "0248889990", "Online/Remote", 0, "web_wizards.jpg", 1),
    
    ("Data Recovery Pros", "Kweku Mensah", "Tech & Services",
     "Data recovery services for corrupted drives and lost files.",
     "0243334445", "0505556667", "ICT Centre, Lab 2", 0, "data_recovery.jpg", 1),
    
    ("Social Media Managers", "Esi Ofori", "Tech & Services",
     "Social media management and digital marketing for student businesses.",
     "0547778889", "0209990001", "Business School", 0, "social_media.jpg", 1),
    
    ("Phone Unlocking", "Kwame Adjei", "Tech & Services",
     "Phone unlocking, screen protectors, and phone accessories.",
     "0245556667", "0557778889", "Night Market, Stall 12", 0, "phone_unlock.jpg", 1),
    
    ("IT Tutoring Hub", "Ama Osei", "Tech & Services",
     "Computer science tutoring for beginners and advanced students.",
     "0201112223", "0543334445", "Science Block", 0, "it_tutoring.jpg", 1),

    # ========== FASHION & CLOTHING (9 businesses) ==========
    ("Afro Threads", "Adwoa Serwaa", "Fashion & Clothing",
     "Custom African print clothing, alterations, and accessories. We make bespoke outfits for any occasion.",
     "0551234567", "0549876543", "Textiles Workshop, Arts Block", 0, "afro_threads.jpg", 1),
    
    ("Campus Couture", "Esi Asare", "Fashion & Clothing",
     "Affordable casual and formal wear for students. Sizes XS-XXL.",
     "0241112223", "0554445556", "Hall 3, Room 10", 0, "campus_couture.jpg", 1),
    
    ("Shoe Haven", "Kwame Boateng", "Fashion & Clothing",
     "Sneakers, sandals, and formal shoes at student-friendly prices.",
     "0207778889", "0541112223", "Night Market", 0, "shoe_haven.jpg", 1),
    
    ("Beads & Bling", "Akua Serwaa", "Fashion & Clothing",
     "Handmade beaded jewelry, bracelets, and accessories.",
     "0556667778", "0248889990", "Arts Centre", 1, "beads_bling.jpg", 1),
    
    ("Threads & Style", "Yaw Asante", "Fashion & Clothing",
     "Urban streetwear, hoodies, and custom t-shirts.",
     "0243334445", "0505556667", "Central Plaza", 0, "threads_style.jpg", 1),
    
    ("Vintage Vibes", "Nana Yaw", "Fashion & Clothing",
     "Vintage and thrift clothing. Unique pieces at affordable prices.",
     "0547778889", "0209990001", "Hall 6, Room 4", 0, "vintage_vibes.jpg", 1),
    
    
    ("Accessory Corner", "Adwoa Boakye", "Fashion & Clothing",
     "Bags, belts, hats, and fashion accessories for students.",
     "0201112223", "0543334445", "Hall 4, Lobby", 0, "accessory_corner.jpg", 1),
    
    
    # ========== LIGHTS & DECOR (9 businesses) ==========
    ("BrightLights Decor", "Samuel Adjei", "Lights & Decor",
     "LED fairy lights, room decoration packages, and custom neon signs for your hall room or events.",
     "0249876543", "0598765432", "Hall 3, Room 45", 1, "brightlights.jpg", 1),
    
    ("Room Revamp", "Esi Amponsah", "Lights & Decor",
     "Dorm room makeovers, wall art, and decorative accessories.",
     "0541112223", "0204445556", "Hall 2, Room 15", 0, "room_revamp.jpg", 1),
    
    ("Party Perfect", "Kwame Agyeman", "Lights & Decor",
     "Event decorations, balloons, and party supplies for campus events.",
     "0245556667", "0557778889", "Event Centre", 1, "party_perfect.jpg", 1),
    
    ("Poster World", "Akua Adjei", "Lights & Decor",
     "Custom posters, wall decals, and photo prints for room decoration.",
     "0208889990", "0541112223", "Arts Centre", 0, "poster_world.jpg", 1),
    
    ("LED Studio", "Yaw Mensah", "Lights & Decor",
     "Custom LED signs, neon lights, and light installations.",
     "0553334445", "0246667778", "Hall 7, Room 8", 0, "led_studio.jpg", 1),
    
    ("Cozy Corners", "Ama Serwaa", "Lights & Decor",
     "Throw pillows, blankets, and cozy room accessories.",
     "0249990001", "0552223334", "Hall 1, Room 22", 0, "cozy_corners.jpg", 1),
    
    ("Wall Art Gallery", "Kojo Asare", "Lights & Decor",
     "Canvas paintings, prints, and custom artwork for rooms.",
     "0544445556", "0207778889", "Arts Block", 0, "wall_art.jpg", 1),
    
    ("Festive Lights", "Nana Ama", "Lights & Decor",
     "Christmas lights, party lights, and decorative lighting.",
     "0501112223", "0243334445", "Hall 5, Common Room", 1, "festive_lights.jpg", 1),
    
    ("Home Essentials", "Kwabena Osei", "Lights & Decor",
     "Storage solutions, organizers, and room essentials for students.",
     "0205556667", "0548889990", "Night Market", 0, "home_essentials.jpg", 1),

    # ========== SERVICES (10 businesses) ==========
    ("Notes & More", "Akosua Boateng", "Services",
     "Printed lecture notes, project binding, laminating, and stationery supplies. Located near the main library.",
     "0501122334", "0209988776", "Main Library, Ground Floor", 0, "notes_more.jpg", 1),
    
    ("SnapShot Studio", "Kofi Annan", "Services",
     "Campus photography for events, portraits, and graduation photos. Affordable student packages.",
     "0245566778", "0501234567", "Creative Arts Centre", 0, "snapshot.jpg", 1),
    
    ("Eco Clean", "Nana Yaw", "Services",
     "Eco-friendly cleaning services for hostels and rooms. We use biodegradable products.",
     "0240001111", "0502223333", "Hall 5, Room 10", 1, "", 0),
    
    
    
    ("Laundry Lounge", "Esi Mensah", "Services",
     "Wash and fold laundry services for students. Pickup and delivery available.",
     "0556667778", "0248889990", "Hall 3, Basement", 1, "laundry.jpg", 1),
    
    
    
    
]

def seed_database():
    """Populate the database with sample data if the businesses table is empty."""
    if not os.path.exists(DATABASE_PATH):
        print(f"Database file '{DATABASE_PATH}' not found. Please run the app first to create it.")
        return
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM businesses")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"Database already has {count} businesses. Skipping seed to avoid duplicates.")
        conn.close()
        return
    
    insert_sql = """
        INSERT INTO businesses
        (business_name, owner_name, category, description, whatsapp, phone, location, delivers, photo_filename, is_verified)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    for biz in sample_businesses:
        cursor.execute(insert_sql, biz)
    
    conn.commit()
    inserted = len(sample_businesses)
    conn.close()
    
    print(f"✅ Seeded {inserted} businesses into {DATABASE_PATH}.")

def verify_data():
    """Print a quick summary of the seeded data."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM businesses")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM businesses WHERE is_verified = 1")
    verified = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM businesses WHERE is_verified = 0")
    pending = cursor.fetchone()[0]
    
    print(f"\n📊 Database Summary:")
    print(f"   Total businesses: {total}")
    print(f"   Verified (live): {verified}")
    print(f"   Pending approval: {pending}")
    
    if total > 0:
        print("\n   Sample businesses by category:")
        cursor.execute("SELECT category, COUNT(*) FROM businesses GROUP BY category")
        for row in cursor.fetchall():
            print(f"   - {row[0]}: {row[1]} businesses")
    
    conn.close()

if __name__ == "__main__":
    print("🌱 Seeding Student Business Directory Database...\n")
    seed_database()
    verify_data()
    print("\n✨ Done. Run the app to see the seeded businesses.")