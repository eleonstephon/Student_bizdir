from PIL import Image, ImageDraw, ImageFont
import os

# Colors for different categories
colors = {
    'default': (100, 150, 200),
    'fashion': (219, 112, 147),   # Pink
    'services': (100, 149, 237),   # Cornflower Blue
    'tech': (46, 139, 87)          # Sea Green
}

# List of missing images with their categories
missing = [
    ('the_tailor_shop.jpg', 'fashion'),
    ('campus_uniforms.jpg', 'fashion'),
    ('cv_pro.jpg', 'services'),
    ('event_planners.jpg', 'services'),
    ('moving_helpers.jpg', 'services'),
    ('study_hub.jpg', 'services'),
    ('tech_support.jpg', 'tech'),
    ('tutoring.jpg', 'services'),
    ('print_go.jpg', 'tech')
]

print('Creating colorful placeholder images...')
print()

for img_name, category in missing:
    try:
        # Choose color based on category
        if category == 'fashion':
            bg_color = (219, 112, 147)  # Pink
        elif category == 'services':
            bg_color = (100, 149, 237)  # Cornflower Blue
        elif category == 'tech':
            bg_color = (46, 139, 87)    # Sea Green
        else:
            bg_color = (100, 150, 200)  # Default
        
        # Create a 400x300 image
        img = Image.new('RGB', (400, 300), color=bg_color)
        d = ImageDraw.Draw(img)
        
        # Draw a white border
        d.rectangle([5, 5, 394, 294], outline=(255, 255, 255), width=4)
        
        # Business name from filename
        business_name = img_name.replace('.jpg', '').replace('_', ' ').title()
        
        # Try to use a font, fall back to default if not available
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        # Split long names into two lines
        if len(business_name) > 25:
            mid = len(business_name) // 2
            line1 = business_name[:mid].strip()
            line2 = business_name[mid:].strip()
            d.text((50, 130), line1, fill=(255, 255, 255), font=font)
            d.text((50, 165), line2, fill=(255, 255, 255), font=font)
        else:
            d.text((50, 140), business_name, fill=(255, 255, 255), font=font)
        
        # Add a "Coming Soon" text
        d.text((140, 220), "Image Coming Soon", fill=(255, 255, 200), font=font)
        
        # Add a simple store icon
        d.rectangle([170, 50, 230, 110], outline=(255, 255, 255), width=2)
        d.rectangle([185, 65, 215, 95], outline=(255, 255, 255), width=2)
        
        # Save the image
        img.save(f'static/uploads/{img_name}')
        print(f'✅ Created: {img_name} ({category})')
        
    except Exception as e:
        print(f'❌ Error creating {img_name}: {e}')

print()
print('✨ Done! Created 9 placeholder images.')