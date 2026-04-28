"""
Seed the Soft Lifee product catalogue.

Usage:
    python manage.py seed_products             # create missing items only
    python manage.py seed_products --update    # also update existing products
    python manage.py seed_products --reset     # WIPE all products/categories first
"""
from django.core.management.base import BaseCommand


CATALOGUE = {
    'categories': [
        {
            'name': 'Home Essentials', 'slug': 'home-essentials', 'order': 1,
            'subcategories': [
                {'name': 'Smart Gadgets',  'slug': 'smart-gadgets',  'order': 1},
                {'name': 'Bathroom',       'slug': 'bathroom',       'order': 2},
                {'name': 'Kitchen',        'slug': 'kitchen',        'order': 3},
                {'name': 'Lighting',       'slug': 'lighting',       'order': 4},
                {'name': 'Personal Care',  'slug': 'personal-care',  'order': 5},
                {'name': 'Organizers',     'slug': 'organizers',     'order': 6},
                {'name': 'Décor',          'slug': 'decor',          'order': 7},
            ],
        },
        {
            'name': 'Accessories', 'slug': 'accessories', 'order': 2,
            'subcategories': [
                {'name': 'Bags',         'slug': 'bags',         'order': 1},
                {'name': 'Jewellery',    'slug': 'jewelry',      'order': 2},
                {'name': 'Drinkware',    'slug': 'drinkware',    'order': 3},
                {'name': 'Smart Gadgets','slug': 'smart-gadgets','order': 4},
                {'name': 'Accessories',  'slug': 'accessories',  'order': 5},
            ],
        },
        {
            'name': 'Skincare', 'slug': 'skincare', 'order': 3,
            'subcategories': [
                {'name': 'Face',        'slug': 'face',        'order': 1},
                {'name': 'Travel Kits', 'slug': 'travel-kits', 'order': 2},
                {'name': 'Body',        'slug': 'body',        'order': 3},
            ],
        },
        {
            'name': "Women's Essentials", 'slug': 'womens-essentials', 'order': 4,
            'subcategories': [
                {'name': 'Personal Care', 'slug': 'personal-care', 'order': 1},
            ],
        },
    ],

    'products': [
        # ── Home Essentials / smart-gadgets ────────────────────────────────
        {
            'name': 'Diffuser', 'slug': 'diffuser',
            'category': 'Home Essentials', 'subcategory': ('Home Essentials', 'smart-gadgets'),
            'price': 15000, 'badge': 'best_seller', 'in_stock': True, 'stock_count': 50,
            'description': 'Transform your space with our premium ultrasonic diffuser. Combines aromatherapy and cool mist humidification to create the perfect ambiance for relaxation, focus, or sleep.',
            'details': ['Ultrasonic cold mist technology', 'Runs up to 8 hours continuously', 'Auto shut-off when water runs out', 'Soft LED mood lighting (7 colours)', 'BPA-free premium materials', 'Ideal room size: up to 30m²'],
            'colors': [],
        },
        {
            'name': '3D Sand Drop', 'slug': '3D-sand-drop',
            'category': 'Home Essentials', 'subcategory': ('Home Essentials', 'smart-gadgets'),
            'price': 10000, 'badge': 'trending', 'in_stock': True, 'stock_count': 30,
            'description': 'A mesmerising kinetic sand sculpture that creates ever-changing landscapes as the coloured sand slowly flows and settles. The ultimate desk art piece.',
            'details': ['Borosilicate glass frame', 'Non-toxic coloured sand', 'Creates unique patterns every time', 'Dimensions: 20cm × 15cm', 'Sealed — no maintenance required', 'Great gift for any occasion'],
            'colors': [],
        },
        {
            'name': 'Foldable Swivel Mosquito Bat', 'slug': 'foldable-swivel-mosquito-bat',
            'category': 'Home Essentials', 'subcategory': ('Home Essentials', 'smart-gadgets'),
            'price': 15000, 'badge': 'new', 'in_stock': True, 'stock_count': 40,
            'description': 'A rechargeable electric mosquito bat with 360° swivel head for hard-to-reach areas. Kills insects on contact with a powerful electric grid — no chemicals needed.',
            'details': ['360° swivel foldable design', 'USB rechargeable battery', 'High-voltage safety electric grid', 'LED indicator light', 'Lightweight & easy to use', 'Safe for indoor use'],
            'colors': [],
        },
        {
            'name': 'AC Cooling Humidifier Fan', 'slug': 'ac-cooling-humidifier-fan',
            'category': 'Home Essentials', 'subcategory': ('Home Essentials', 'smart-gadgets'),
            'price': 25000, 'badge': 'best_seller', 'in_stock': True, 'stock_count': 35,
            'description': 'A 3-in-1 portable air cooler, humidifier, and fan that cools your personal space without a full AC unit. Perfect for desks, bedrooms, and small offices.',
            'details': ['3-in-1: fan, cooler & humidifier', 'USB powered — works anywhere', '3 speed settings', '500ml water tank', 'Quiet operation (<40dB)', 'Compatible with ice for extra cooling'],
            'colors': [],
        },
        {
            'name': 'E-30 Camera Fill Light', 'slug': 'e-30-camera-fill-light',
            'category': 'Home Essentials', 'subcategory': ('Home Essentials', 'smart-gadgets'),
            'price': 32000, 'badge': 'best_seller', 'in_stock': True, 'stock_count': 20,
            'description': 'Professional-grade LED fill light for content creators and video calls. Delivers soft, even lighting with adjustable colour temperature and brightness.',
            'details': ['3 colour temperatures (warm/neutral/cool)', '10 brightness levels', 'Compatible with phones & cameras', 'USB powered', 'Flexible clamp mount', 'Ideal for TikTok, YouTube & Zoom'],
            'colors': [],
        },
        # ── Home Essentials / bathroom ────────────────────────────────────
        {
            'name': 'Bathroom Organizer', 'slug': 'bathroom-organizer',
            'category': 'Home Essentials', 'subcategory': ('Home Essentials', 'bathroom'),
            'price': 15000, 'badge': 'best_seller', 'in_stock': True, 'stock_count': 60,
            'description': 'Keep your bathroom clutter-free with this multi-tier organizer. Perfect for toiletries, skincare products and accessories — everything within reach and beautifully organised.',
            'details': ['Rust-resistant stainless steel', '3-tier storage system', 'Easy install — no drilling required', 'Holds up to 10kg per shelf', 'Dimensions: 25cm × 60cm', 'Wipe clean surface'],
            'colors': [],
        },
        {
            'name': 'Over-The-Toilet Organizer Rack', 'slug': 'over-the-toilet-organizer-rack',
            'category': 'Home Essentials', 'subcategory': ('Home Essentials', 'bathroom'),
            'price': 15000, 'badge': 'new', 'in_stock': True, 'stock_count': 30,
            'description': 'Maximise your bathroom space with this over-the-toilet storage rack. Fits most standard toilets with no tools or drilling required.',
            'details': ['3-shelf design for ample storage', 'No-drill freestanding installation', 'Rust-proof powder-coated steel', 'Adjustable feet for stability', 'Fits toilets up to 38cm wide', 'Easy to assemble in minutes'],
            'colors': [],
        },
        {
            'name': 'Multifunctional Towel Organizer', 'slug': 'multifunctional-towel-organizer',
            'category': 'Home Essentials', 'subcategory': ('Home Essentials', 'bathroom'),
            'price': 12000, 'badge': 'new', 'in_stock': True, 'stock_count': 45,
            'description': 'A sleek wall-mounted or freestanding towel organizer that keeps your bathroom looking neat. Multiple hooks and rails for towels, robes, and accessories.',
            'details': ['Multi-hook + rail design', 'No-drilling adhesive mount or screw option', 'Holds up to 3 towels + accessories', 'Rust-resistant chrome finish', 'Easy to clean', 'Modern minimalist design'],
            'colors': [],
        },
        {
            'name': '5 IN 1 Multipurpose Organizer', 'slug': '5in1-multipurpose-organizer',
            'category': 'Home Essentials', 'subcategory': ('Home Essentials', 'bathroom'),
            'price': 20000, 'badge': 'best_seller', 'in_stock': True, 'stock_count': 40,
            'description': 'The ultimate 5-in-1 bathroom organizer with separate compartments for every essential. Keep your countertop clear and your routine effortless.',
            'details': ['5 separate storage compartments', 'Toothbrush, cup, soap & more', 'Rust-resistant & waterproof', 'Non-slip base', 'Dimensions: 28cm × 10cm × 16cm', 'Easy to clean — removable tray'],
            'colors': [],
        },
        # ── Home Essentials / kitchen ─────────────────────────────────────
        {
            'name': 'Flower Vase', 'slug': 'flower-vase',
            'category': 'Home Essentials', 'subcategory': ('Home Essentials', 'kitchen'),
            'price': 12000, 'badge': 'new', 'in_stock': True, 'stock_count': 35,
            'description': 'A beautifully crafted ceramic flower vase that adds natural elegance to any room. The minimalist design complements both fresh and dried flower arrangements.',
            'details': ['Premium glazed ceramic', 'Height: 28cm, Diameter: 12cm', 'Suitable for fresh & dried flowers', 'Waterproof interior lining', 'Scratch-resistant base', 'Dishwasher safe'],
            'colors': [
                {'label': 'White', 'hex_code': '#FAFAFA'},
                {'label': 'Beige', 'hex_code': '#E8D5B0'},
                {'label': 'Terracotta', 'hex_code': '#C4553A'},
            ],
        },
        {
            'name': 'Ceramic Cup Set', 'slug': 'ceramic-cup-set',
            'category': 'Home Essentials', 'subcategory': ('Home Essentials', 'kitchen'),
            'price': 22000, 'badge': 'new', 'in_stock': True, 'stock_count': 25,
            'description': 'A curated set of artisan ceramic cups that transform your morning ritual into a luxury experience. Each piece is handcrafted with subtle variations that make every cup unique.',
            'details': ['Set of 4 handcrafted cups', 'Capacity: 350ml each', 'Lead-free glazed ceramic', 'Microwave & dishwasher safe', 'Gift box packaging included', 'Available in 3 colour palettes'],
            'colors': [
                {'label': 'Stone', 'hex_code': '#9E9E9E'},
                {'label': 'White', 'hex_code': '#FAFAFA'},
                {'label': 'Sage',  'hex_code': '#8FAF8F'},
            ],
        },
        {
            'name': 'Storage Basket', 'slug': 'storage-basket',
            'category': 'Home Essentials', 'subcategory': ('Home Essentials', 'kitchen'),
            'price': 7500, 'badge': 'new', 'in_stock': True, 'stock_count': 55,
            'description': 'A versatile woven storage basket that combines practicality with aesthetic appeal.',
            'details': ['Durable woven construction', 'Dimensions: 30cm × 20cm × 15cm', 'Handles for easy carrying', 'Collapses flat for storage', 'Holds up to 5kg', 'Easy to clean surface'],
            'colors': [],
        },
        {
            'name': 'Ultra-Portable Juicer Cup', 'slug': 'ultra-portable-multi-functional-juicer-cup',
            'category': 'Home Essentials', 'subcategory': ('Home Essentials', 'kitchen'),
            'price': 14000, 'badge': 'best_seller', 'in_stock': True, 'stock_count': 65,
            'description': 'A powerful 6-blade USB rechargeable juicer that squeezes fresh juice in under 30 seconds.',
            'details': ['6 surgical steel blades', 'USB rechargeable (2hr = 15 uses)', 'Capacity: 380ml', 'Blends in < 30 seconds', 'BPA-free tritan material', 'Dishwasher safe (except motor)'],
            'colors': [],
        },
        {
            'name': 'Cooking Flipper', 'slug': 'cooking-flipper',
            'category': 'Home Essentials', 'subcategory': ('Home Essentials', 'kitchen'),
            'price': 5000, 'badge': 'best_seller', 'in_stock': True, 'stock_count': 80,
            'description': 'A professional-grade silicone cooking flipper that handles everything from pancakes to fish with ease. Heat-resistant up to 230°C and completely non-stick friendly.',
            'details': ['Food-grade silicone head', 'Heat resistant to 230°C', 'Non-scratch — safe for all pans', 'Ergonomic grip handle', 'Dishwasher safe', 'Length: 32cm'],
            'colors': [],
        },
        {
            'name': 'Multifunctional Wall Mounted Trash Can', 'slug': 'multifunctional-wall-mounted-trash-can',
            'category': 'Home Essentials', 'subcategory': ('Home Essentials', 'kitchen'),
            'price': 4500, 'badge': 'new', 'in_stock': True, 'stock_count': 50,
            'description': 'A compact wall-mounted or cabinet-door trash can that keeps your kitchen tidy without taking up counter or floor space. Perfect for small kitchens.',
            'details': ['Wall-mount or cabinet-door installation', 'Capacity: 8L', 'Sturdy plastic with lid', 'Easy removal for emptying', 'No-drill adhesive or screw mount', 'Easy wipe-clean interior'],
            'colors': [],
        },
        # ── Home Essentials / lighting ────────────────────────────────────
        {
            'name': 'Moonlight Lamp', 'slug': 'moonlight-lamp',
            'category': 'Home Essentials', 'subcategory': ('Home Essentials', 'lighting'),
            'price': 14500, 'badge': 'new', 'in_stock': True, 'stock_count': 40,
            'description': 'A stunning rechargeable rotating moon lamp that casts a magical celestial glow. 16 colour options controlled via remote or touch — the perfect mood light for any room.',
            'details': ['16 colour options', 'Remote + touch control', 'USB rechargeable (4hr charge = 8hr use)', '3 brightness levels', 'Diameter: 15cm', 'Auto-off timer: 1hr / 2hr / 4hr'],
            'colors': [],
        },
        {
            'name': 'Crystal Diamond LED Lamp', 'slug': 'crystal-diamond-led-lamp',
            'category': 'Home Essentials', 'subcategory': ('Home Essentials', 'lighting'),
            'price': 13000, 'badge': 'new', 'in_stock': True, 'stock_count': 30,
            'description': 'A gorgeous crystal diamond LED table lamp that creates dazzling light patterns on your walls and ceiling.',
            'details': ['Faceted crystal design', 'Warm white LED bulb included', 'Touch dimmer (3 levels)', 'USB + plug power options', 'Height: 32cm', 'Energy efficient — 5W'],
            'colors': [],
        },
        {
            'name': '360 Motion Sensor Light', 'slug': '360-motion-sensor-light',
            'category': 'Home Essentials', 'subcategory': ('Home Essentials', 'lighting'),
            'price': 13000, 'badge': 'best_seller', 'in_stock': True, 'stock_count': 60,
            'description': 'A smart motion-activated LED night light that turns on automatically when you enter a room and off when you leave. Perfect for hallways, bathrooms, and wardrobes.',
            'details': ['360° motion detection sensor', 'USB rechargeable battery', 'Auto on/off — no touching required', '3 modes: auto, on, off', 'Warm white LED', 'Up to 90 days per charge (auto mode)'],
            'colors': [],
        },
        # ── Home Essentials / personal-care ──────────────────────────────
        {
            'name': 'Relaxation Chair', 'slug': 'relaxation-chair',
            'category': 'Home Essentials', 'subcategory': ('Home Essentials', 'personal-care'),
            'price': 85000, 'badge': 'premium', 'in_stock': True, 'stock_count': 10,
            'description': 'A luxurious zero-gravity relaxation chair with built-in massage nodes, heating, and reclining function. Your personal wellness retreat at home.',
            'details': ['Zero-gravity reclining position', 'Built-in heat & vibration massage', 'Adjustable headrest & armrests', 'Premium faux leather upholstery', 'Weight capacity: 120kg', 'Remote control included'],
            'colors': [],
        },
        {
            'name': 'Quick Shoe Wipe', 'slug': 'quick-shoe-wipe',
            'category': 'Home Essentials', 'subcategory': ('Home Essentials', 'personal-care'),
            'price': 5000, 'badge': 'new', 'in_stock': True, 'stock_count': 100,
            'description': 'A self-cleaning shoe wipe mat that polishes your shoes in seconds — just step and wipe. Perfect for the front door, office entrance, or car.',
            'details': ['Self-cleaning bristle design', 'Works on all shoe types', 'Non-slip rubber base', 'Easy to clean — rinse and dry', 'Dimensions: 40cm × 30cm', 'Durable outdoor material'],
            'colors': [],
        },
        # ── Home Essentials / organizers ─────────────────────────────────
        {
            'name': '3 Layers Jewelry Box With Key', 'slug': '3-layers-jewelry-box-with-key',
            'category': 'Home Essentials', 'subcategory': ('Home Essentials', 'organizers'),
            'price': 32000, 'badge': 'new', 'in_stock': True, 'stock_count': 20,
            'description': 'A luxurious 3-layer lockable jewelry box with a built-in mirror, velvet lining, and separate compartments for rings, necklaces, earrings and bracelets.',
            'details': ['3 pull-out drawers with key lock', 'Built-in mirror', 'Velvet-lined compartments', 'Ring rolls, necklace hooks & earring slots', 'Dimensions: 26cm × 13cm × 20cm', 'Elegant PU leather exterior'],
            'colors': [],
        },
        {
            'name': 'Underwear Organizer', 'slug': 'underwear-organizer',
            'category': 'Home Essentials', 'subcategory': ('Home Essentials', 'organizers'),
            'price': 4000, 'badge': 'new', 'in_stock': True, 'stock_count': 80,
            'description': 'A honeycomb underwear organizer drawer divider that keeps your intimates neatly separated and easy to find. Fits most standard drawers.',
            'details': ['Honeycomb cell design', 'Expandable to fit any drawer', '30 compartments', 'Breathable fabric material', 'Machine washable', 'Dimensions: 30cm × 20cm (expandable)'],
            'colors': [],
        },
        {
            'name': 'Double Sided Nano Tape', 'slug': 'double-sided-nano-tape',
            'category': 'Home Essentials', 'subcategory': ('Home Essentials', 'organizers'),
            'price': 6000, 'badge': 'new', 'in_stock': True, 'stock_count': 120,
            'description': 'Super-strong reusable nano tape that sticks to any smooth surface without leaving marks. Perfect for hanging pictures, mounting accessories, and organising cables.',
            'details': ['Reusable — rinse and re-stick', 'No residue or marks left', 'Holds up to 5kg', 'Works on tiles, glass, wood & plastic', 'Width: 3cm, Length: 3m per roll', 'Waterproof & heat resistant'],
            'colors': [],
        },
        # ── Home Essentials / decor ───────────────────────────────────────
        {
            'name': 'Inspirational Wall Stickers', 'slug': 'inspirational-wall-stickers',
            'category': 'Home Essentials', 'subcategory': ('Home Essentials', 'decor'),
            'price': 9000, 'badge': 'new', 'in_stock': True, 'stock_count': 75,
            'description': 'Beautiful peel-and-stick wall decals with motivational quotes and elegant designs. Instantly transform any wall with zero damage and easy repositioning.',
            'details': ['Self-adhesive vinyl material', 'Removable & repositionable', 'No wall damage', 'Waterproof & fade resistant', 'Includes application squeegee', 'Available in multiple quote styles'],
            'colors': [],
        },
        {
            'name': 'Gold Decor Tape', 'slug': 'gold-decor-tape',
            'category': 'Home Essentials', 'subcategory': ('Home Essentials', 'decor'),
            'price': 5000, 'badge': 'new', 'in_stock': True, 'stock_count': 100,
            'description': 'Luxurious metallic gold decorative tape for adding elegant borders, frames, and accents to walls, furniture, mirrors, and crafts.',
            'details': ['Genuine metallic gold finish', 'Width: 1cm, Length: 10m per roll', 'Peel-and-stick — no glue needed', 'Removable without residue', 'Works on most smooth surfaces', 'Perfect for DIY room makeovers'],
            'colors': [],
        },
        {
            'name': 'Vine Leaf Room Decor', 'slug': 'vine-leaf-room-decor',
            'category': 'Home Essentials', 'subcategory': ('Home Essentials', 'decor'),
            'price': 1800, 'badge': 'new', 'in_stock': True, 'stock_count': 150,
            'description': 'Artificial trailing vine leaves for creating a lush, botanical atmosphere in any room. Perfect for shelves, headboards, window frames, and ceiling decor.',
            'details': ['High-quality silk leaves', 'Natural-looking texture', 'Length: 2m per vine', 'No watering needed', 'Suitable for indoor use', 'Easy to style and arrange'],
            'colors': [],
        },
        {
            'name': 'Decorative Wall Hooks', 'slug': 'decorative-wall-hooks',
            'category': 'Home Essentials', 'subcategory': ('Home Essentials', 'decor'),
            'price': 1500, 'badge': 'new', 'in_stock': True, 'stock_count': 200,
            'description': 'Elegant self-adhesive decorative wall hooks that combine function and style. No drilling required — stick on any smooth wall and hang bags, keys, towels, and more.',
            'details': ['Self-adhesive — no drilling', 'Holds up to 3kg per hook', 'No residue when removed', 'Available in gold & chrome finishes', 'Waterproof — suitable for bathrooms', 'Pack of 4 hooks'],
            'colors': [],
        },
        {
            'name': 'Self-adhesive Countertop Film', 'slug': 'self-adhesive-countertop-film',
            'category': 'Home Essentials', 'subcategory': ('Home Essentials', 'decor'),
            'price': 8000, 'badge': 'best_seller', 'in_stock': True, 'stock_count': 60,
            'description': 'Transform your kitchen or bathroom countertops with this premium self-adhesive marble or wood-effect film. No professional installation needed — just peel and stick.',
            'details': ['Realistic marble/wood finish', 'Self-adhesive PVC film', 'Waterproof & heat resistant', 'Dimensions: 60cm × 2m per roll', 'Removable without residue', 'Suitable for countertops, shelves & furniture'],
            'colors': [],
        },
        # ── Accessories / bags ────────────────────────────────────────────
        {
            'name': 'Tote Bag', 'slug': 'tote-bag',
            'category': 'Accessories', 'subcategory': ('Accessories', 'bags'),
            'price': 8500, 'badge': 'new', 'in_stock': True, 'stock_count': 40,
            'description': 'A versatile and stylish tote bag designed for the modern woman. Spacious enough for everything you need, minimal enough to go everywhere.',
            'details': ['Premium canvas material', 'Reinforced handles', 'Internal zip pocket', 'Dimensions: 40cm × 35cm × 12cm', 'Available in multiple colours', 'Machine washable'],
            'colors': [
                {'label': 'Alpine Blue', 'hex_code': '#4A7FA5'},
                {'label': 'Black',       'hex_code': '#1A1A2E'},
                {'label': 'Blush',       'hex_code': '#F4B8C1'},
            ],
        },
        # ── Accessories / jewelry ─────────────────────────────────────────
        {
            'name': 'Smart-Watch Set', 'slug': 'smart-watch-set',
            'category': 'Accessories', 'subcategory': ('Accessories', 'jewelry'),
            'price': 40000, 'badge': 'premium', 'in_stock': True, 'stock_count': 20,
            'description': 'A premium smart watch bundle that tracks your fitness goals, monitors your health metrics and keeps you connected — all with a sleek, luxury aesthetic.',
            'details': ['Heart rate & SpO2 monitoring', '7-day battery life', 'IP68 water resistant', '100+ sport modes', 'Custom watch faces', 'Compatible: iOS & Android'],
            'colors': [
                {'label': 'Black',  'hex_code': '#1A1A2E'},
                {'label': 'Silver', 'hex_code': '#C0C0C0'},
                {'label': 'Gold',   'hex_code': '#D4AF37'},
            ],
        },
        {
            'name': 'Smart Watch (Series 8)', 'slug': 'smart-watch-series-8',
            'category': 'Accessories', 'subcategory': ('Accessories', 'jewelry'),
            'price': 25000, 'badge': 'new', 'in_stock': True, 'stock_count': 20,
            'description': 'The Series 8 smart watch brings premium health tracking and connectivity in a sleek, modern design.',
            'details': ['Always-on Retina display', 'ECG & blood oxygen monitoring', 'Crash detection feature', 'IP6X dust resistant', '18-hour battery life', 'Compatible with iOS & Android'],
            'colors': [
                {'label': 'Midnight',  'hex_code': '#1A1A2E'},
                {'label': 'Silver',    'hex_code': '#C0C0C0'},
                {'label': 'Rose Gold', 'hex_code': '#B76E79'},
            ],
        },
        # ── Accessories / drinkware ───────────────────────────────────────
        {
            'name': 'Matte Stanley Tumbler', 'slug': 'matte-stanley-tumbler',
            'category': 'Accessories', 'subcategory': ('Accessories', 'drinkware'),
            'price': 18000, 'badge': 'new', 'in_stock': True, 'stock_count': 80,
            'description': 'The iconic Stanley tumbler in a luxurious matte finish. Double-wall vacuum insulation keeps your drinks hot for 7 hours and cold for 24 hours. Elevate your daily hydration.',
            'details': ['Double-wall vacuum insulation', 'Hot: 7hrs · Iced: 24hrs · Cold: 3 days', 'BPA-free 18/8 stainless steel', 'Capacity: 40oz (1.18L)', 'Fits most car cup holders', 'Leak-proof lid with carry handle'],
            'colors': [
                {'label': 'Blush',    'hex_code': '#F4B8C1'},
                {'label': 'Sage',     'hex_code': '#8FAF8F'},
                {'label': 'Charcoal', 'hex_code': '#3D3D3D'},
                {'label': 'Cream',    'hex_code': '#FFF8E7'},
                {'label': 'Lilac',    'hex_code': '#C4A8D4'},
                {'label': 'Navy',     'hex_code': '#1A1A4E'},
            ],
        },
        {
            'name': 'Stanley Cup', 'slug': 'stanley-cup',
            'category': 'Accessories', 'subcategory': ('Accessories', 'drinkware'),
            'price': 17000, 'badge': 'best_seller', 'in_stock': True, 'stock_count': 120,
            'description': 'The legendary Stanley cup — a cultural icon and the ultimate hydration companion. Built to last a lifetime with vacuum insulation that actually works.',
            'details': ['40oz vacuum insulated', 'Keeps cold 2+ days with ice', 'Comfort grip handle', 'Reusable straw included', 'Fits cup holders', 'Lifetime guarantee'],
            'colors': [
                {'label': 'Desert Sage', 'hex_code': '#8FAF8F'},
                {'label': 'Cream',       'hex_code': '#FFF8E7'},
                {'label': 'Charcoal',    'hex_code': '#3D3D3D'},
                {'label': 'Blush',       'hex_code': '#F4B8C1'},
                {'label': 'Alpine Blue', 'hex_code': '#4A7FA5'},
                {'label': 'Terracotta',  'hex_code': '#C4553A'},
            ],
        },
        {
            'name': 'Stanley Cup Accessories', 'slug': 'stanley-cup-accessories',
            'category': 'Accessories', 'subcategory': ('Accessories', 'drinkware'),
            'price': 25000, 'badge': 'trending', 'in_stock': True, 'stock_count': 50,
            'description': 'A complete Stanley cup accessory bundle — includes straws, handles, name tags, lids, and cleaning brushes to personalise and protect your Stanley.',
            'details': ['Compatible with 40oz & 30oz Stanley cups', 'Includes 2 reusable straws + cleaner', 'Silicone protective boot', 'Name tag & handle set', 'Lid cover & straw cap', 'Food-grade BPA-free materials'],
            'colors': [],
        },
        {
            'name': 'Happy Supply Chain Water Bottle', 'slug': 'happy-supply-chain-water-bottle',
            'category': 'Accessories', 'subcategory': ('Accessories', 'drinkware'),
            'price': 7000, 'badge': 'new', 'in_stock': True, 'stock_count': 70,
            'description': 'A stylish motivational water bottle with time markers to keep you on track with your daily hydration goals. Leakproof and perfect for the gym, office, or travel.',
            'details': ['1L capacity with time markers', 'BPA-free Tritan plastic', 'Leakproof flip-top lid', 'Wide mouth for ice cubes', 'Motivational quotes printed on side', 'Fits most cup holders'],
            'colors': [],
        },
        # ── Accessories / smart-gadgets ───────────────────────────────────
        {
            'name': 'Laptop Stand', 'slug': 'laptop-stand',
            'category': 'Accessories', 'subcategory': ('Accessories', 'smart-gadgets'),
            'price': 8000, 'badge': 'trending', 'in_stock': True, 'stock_count': 45,
            'description': 'An ergonomic adjustable laptop stand that raises your screen to eye level, reducing neck and back strain. Folds flat for portability and fits laptops up to 17".',
            'details': ['Adjustable height: 10–32cm', 'Compatible with laptops 10–17"', 'Non-slip silicone pads', 'Open design for ventilation', 'Folds flat — fits in any bag', 'Weight: 360g'],
            'colors': [],
        },
        {
            'name': 'Phone Suction Cup', 'slug': 'phone-suction-cup',
            'category': 'Accessories', 'subcategory': ('Accessories', 'smart-gadgets'),
            'price': 1000, 'badge': 'new', 'in_stock': True, 'stock_count': 200,
            'description': 'A strong suction cup phone holder for car dashboards, mirrors, windows, and tiles. Adjustable 360° rotation for perfect viewing angle.',
            'details': ['Industrial-strength suction cup', '360° rotation ball joint', 'One-handed release button', 'Compatible with all phones up to 6.8"', 'No adhesive residue', 'Reusable — rinse and restick'],
            'colors': [],
        },
        {
            'name': 'RGB Phone LED Light', 'slug': 'rgb-phone-led-light',
            'category': 'Accessories', 'subcategory': ('Accessories', 'smart-gadgets'),
            'price': 8000, 'badge': 'new', 'in_stock': True, 'stock_count': 60,
            'description': 'A clip-on RGB LED light for your phone that transforms your selfies and video calls with professional colour lighting. 16 colour modes via app control.',
            'details': ['16 RGB colour modes', 'Bluetooth app control', 'Clips onto any phone or tablet', 'USB-C rechargeable', 'Adjustable brightness', 'Ideal for selfies, streaming & video calls'],
            'colors': [],
        },
        {
            'name': 'Wireless Fill Light BT Remote Tripod', 'slug': 'wireless-fill-light-bt-remote-tripod',
            'category': 'Accessories', 'subcategory': ('Accessories', 'smart-gadgets'),
            'price': 12000, 'badge': 'new', 'in_stock': True, 'stock_count': 35,
            'description': 'A 3-in-1 content creator kit: wireless ring light, Bluetooth remote shutter, and extendable tripod. Perfect for photos, reels, TikToks, and video calls.',
            'details': ['Extendable tripod: 30–130cm', 'Wireless Bluetooth shutter remote', 'Built-in LED fill light (3 modes)', 'Universal phone clip (fits all phones)', 'USB rechargeable', 'Folds compact for travel'],
            'colors': [],
        },
        {
            'name': 'Bubble Gun', 'slug': 'bubble-gun',
            'category': 'Accessories', 'subcategory': ('Accessories', 'smart-gadgets'),
            'price': 10000, 'badge': 'new', 'in_stock': True, 'stock_count': 50,
            'description': 'An electric automatic bubble gun that shoots hundreds of bubbles per minute with colourful LED lights. Perfect for parties, kids, and outdoor fun.',
            'details': ['Automatic bubble machine', '500+ bubbles per minute', 'Colourful flashing LEDs', 'Battery powered (AA batteries)', 'Includes bubble solution', 'Safe for children — non-toxic solution'],
            'colors': [],
        },
        {
            'name': 'USB Cigarette Lighter Mobile Phone Holder', 'slug': 'usb-cigarettes-lighter-mobile-phone-holder',
            'category': 'Accessories', 'subcategory': ('Accessories', 'smart-gadgets'),
            'price': 10000, 'badge': 'new', 'in_stock': True, 'stock_count': 55,
            'description': 'A 2-in-1 car phone holder and USB charger that plugs into your cigarette lighter socket. Holds your phone securely while keeping it charged on the go.',
            'details': ['2-in-1: phone holder + USB charger', 'Fits cigarette lighter socket', '360° adjustable arm', 'Dual USB ports (5V/2.1A)', 'Compatible with all phones up to 6.8"', 'Non-slip silicone grip'],
            'colors': [],
        },
        # ── Accessories / accessories ─────────────────────────────────────
        {
            'name': 'Fancy Barbie Pen', 'slug': 'fancy-barbie-pen',
            'category': 'Accessories', 'subcategory': ('Accessories', 'accessories'),
            'price': 2000, 'badge': 'new', 'in_stock': True, 'stock_count': 150,
            'description': 'A gorgeous Barbie-themed luxury pen with a fluffy feather topper and smooth gel ink. The perfect accessory for journaling, gifting, or treating yourself.',
            'details': ['Fluffy feather topper', 'Smooth black gel ink', 'Refillable ink cartridge', 'Barrel length: 18cm', 'Fun & stylish gift idea', 'Works on all paper types'],
            'colors': [],
        },
        # ── Skincare / face ───────────────────────────────────────────────
        {
            'name': 'Green Stick Mask', 'slug': 'green-stick-mask',
            'category': 'Skincare', 'subcategory': ('Skincare', 'face'),
            'price': 5000, 'badge': 'top_rated', 'in_stock': True, 'stock_count': 100,
            'description': 'A deep-cleansing green tea infused stick mask that draws out impurities, unclogs pores and leaves skin feeling refreshed, smooth and perfectly balanced.',
            'details': ['Green tea & charcoal formula', 'Suitable for all skin types', 'Dermatologist tested', 'No parabens or sulphates', 'Stick applicator — zero mess', 'Use 2–3 times per week'],
            'colors': [],
        },
        {
            'name': 'Star Pimple Patches', 'slug': 'star-pimple-patches',
            'category': 'Skincare', 'subcategory': ('Skincare', 'face'),
            'price': 1300, 'badge': 'trending', 'in_stock': True, 'stock_count': 200,
            'description': 'Cute star-shaped hydrocolloid pimple patches that absorb impurities, reduce redness, and protect blemishes overnight. Wear them out — they double as fun face stickers.',
            'details': ['Hydrocolloid technology', 'Absorbs pus & reduces inflammation', 'Star-shaped — doubles as cute sticker', 'Transparent & barely visible', 'Pack of 36 patches', 'Vegan & cruelty-free'],
            'colors': [],
        },
        {
            'name': 'Compressed Facial Towel', 'slug': 'compressed-facial-towel',
            'category': 'Skincare', 'subcategory': ('Skincare', 'face'),
            'price': 200, 'badge': 'new', 'in_stock': True, 'stock_count': 500,
            'description': 'A single-use compressed facial towel tablet that expands into a full soft towel when wet. Hygienic, portable, and perfect for travel, gym, or daily cleansing.',
            'details': ['Expands to full towel when wet', '100% pure cotton', 'Single-use & hygienic', 'Compact tablet size', 'Gentle on sensitive skin', 'Pack of 10 tablets'],
            'colors': [],
        },
        {
            'name': 'SADOER Ampoules Facial Mask', 'slug': 'sadoer-ampoules-facial-mask',
            'category': 'Skincare', 'subcategory': ('Skincare', 'face'),
            'price': 800, 'badge': 'new', 'in_stock': True, 'stock_count': 300,
            'description': 'A concentrated ampoule-infused sheet mask that delivers an intense burst of hydration, brightening, and anti-aging ingredients in just 15 minutes.',
            'details': ['High-concentration ampoule formula', 'Deep hydration + brightening', 'Anti-aging antioxidants', 'Suitable for all skin types', 'Leave on for 15–20 minutes', 'Pack of 5 masks'],
            'colors': [],
        },
        {
            'name': 'Tongue Scrubber', 'slug': 'tongue-scrubber',
            'category': 'Skincare', 'subcategory': ('Skincare', 'face'),
            'price': 1000, 'badge': 'new', 'in_stock': True, 'stock_count': 250,
            'description': 'A medical-grade stainless steel tongue scraper that removes bacteria, food debris, and dead cells from your tongue — the key to fresher breath and better oral health.',
            'details': ['Medical-grade stainless steel', 'Removes 99% of bacteria causing bad breath', 'Comfortable curved design', 'Easy to clean & reuse', 'Lasts for years', 'Travel pouch included'],
            'colors': [],
        },
        # ── Skincare / travel-kits ────────────────────────────────────────
        {
            'name': 'Travel Box', 'slug': 'travel-box',
            'category': 'Skincare', 'subcategory': ('Skincare', 'travel-kits'),
            'price': 9500, 'badge': 'new', 'in_stock': True, 'stock_count': 45,
            'description': 'A compact, TSA-approved travel skincare organiser with leak-proof compartments. Keep your entire skincare routine perfectly organised on the go.',
            'details': ['TSA-approved dimensions', '6 leak-proof silicone bottles', 'Clear design for airport security', 'Hanging hook for easy access', 'Waterproof outer shell', 'Fits carry-on luggage perfectly'],
            'colors': [],
        },
        {
            'name': 'Travel Kit', 'slug': 'travel-kit',
            'category': 'Skincare', 'subcategory': ('Skincare', 'travel-kits'),
            'price': 14500, 'badge': 'best_seller', 'in_stock': True, 'stock_count': 40,
            'description': 'A complete travel skincare kit with full-size bottles, organizer bag, and all the essentials for your routine while away from home.',
            'details': ['Complete skincare set for travel', 'Includes cleanser, toner & moisturiser', 'Refillable silicone bottles', 'Compact carry bag included', 'Fits overhead cabin luggage', 'TSA-approved sizes'],
            'colors': [],
        },
        # ── Skincare / body ───────────────────────────────────────────────
        {
            'name': 'Floral & Fruit Fragrance Hand Cream', 'slug': 'floral-fruit-fragrance-hand-cream',
            'category': 'Skincare', 'subcategory': ('Skincare', 'body'),
            'price': 700, 'badge': 'new', 'in_stock': True, 'stock_count': 400,
            'description': 'A richly moisturising hand cream with a delightful blend of floral and fruity fragrances. Absorbs quickly without greasiness, leaving hands soft, smooth and beautifully scented.',
            'details': ['Fast-absorbing formula', 'Long-lasting fragrance', 'Enriched with shea butter', 'No sticky residue', 'Suitable for sensitive skin', 'Tube: 30ml — perfect for handbag'],
            'colors': [],
        },
        # ── Women's Essentials / personal-care ───────────────────────────
        {
            'name': 'Boob Tape', 'slug': 'boob-tape',
            'category': "Women's Essentials", 'subcategory': ("Women's Essentials", 'personal-care'),
            'price': 3500, 'badge': 'best_seller', 'in_stock': True, 'stock_count': 150,
            'description': 'Medical-grade body tape for lifting, shaping, and securing backless, strapless, and low-cut outfits. Waterproof, sweat-proof, and gentle on all skin types.',
            'details': ['Medical-grade cotton tape', 'Waterproof & sweat-resistant', 'Strong hold — lasts all day', 'Gentle on skin — residue-free removal', 'Works with all skin tones', 'Includes nipple covers'],
            'colors': [],
        },
        {
            'name': 'Transparent Boobs Lifter', 'slug': 'transparent-boobs-lifter',
            'category': "Women's Essentials", 'subcategory': ("Women's Essentials", 'personal-care'),
            'price': 4500, 'badge': 'new', 'in_stock': True, 'stock_count': 100,
            'description': 'Invisible adhesive silicone bra lifters that provide natural lift and shape without straps or wires. Compatible with all outfits — your secret weapon for confidence.',
            'details': ['Medical-grade silicone', 'Completely invisible under clothes', 'Self-adhesive — no straps or wires', 'Reusable — wash and reuse 20+ times', 'Suitable for cup sizes A–D', 'Includes storage case'],
            'colors': [],
        },
    ],
}


# Cloudinary public_id for each product's primary image.
# These are uploaded once via upload_to_cloudinary_direct.py and never change.
PRODUCT_IMAGE_IDS = {
    'diffuser':                                   'softlifee_products/diffuser',
    '3D-sand-drop':                               'softlifee_products/3D-sand-drop',
    'foldable-swivel-mosquito-bat':               'softlifee_products/foldable-swivel-mosquito-bat',
    'ac-cooling-humidifier-fan':                  'softlifee_products/ac-cooling-humidifier-fan',
    'e-30-camera-fill-light':                     'softlifee_products/e-30-camera-fill-light',
    'bathroom-organizer':                         'softlifee_products/bathroom-organizer',
    'over-the-toilet-organizer-rack':             'softlifee_products/over-the-toilet-organizer-rack',
    'multifunctional-towel-organizer':            'softlifee_products/multifunctional-towel-organizer',
    '5in1-multipurpose-organizer':                'softlifee_products/5in1-multipurpose-organizer',
    'flower-vase':                                'softlifee_products/flower-vase',
    'ceramic-cup-set':                            'softlifee_products/ceramic-cup-set',
    'storage-basket':                             'softlifee_products/storage-basket',
    'ultra-portable-multi-functional-juicer-cup': 'softlifee_products/ultra-portable-multi-functional-juicer-cup',
    'cooking-flipper':                            'softlifee_products/cooking-flipper',
    'multifunctional-wall-mounted-trash-can':     'softlifee_products/multifunctional-wall-mounted-trash-can',
    'moonlight-lamp':                             'softlifee_products/moonlight-lamp',
    'crystal-diamond-led-lamp':                   'softlifee_products/crystal-diamond-led-lamp',
    '360-motion-sensor-light':                    'softlifee_products/360-motion-sensor-light',
    'relaxation-chair':                           'softlifee_products/relaxation-chair',
    'quick-shoe-wipe':                            'softlifee_products/quick-shoe-wipe',
    '3-layers-jewelry-box-with-key':              'softlifee_products/3-layers-jewelry-box-with-key',
    'underwear-organizer':                        'softlifee_products/underwear-organizer',
    'double-sided-nano-tape':                     'softlifee_products/double-sided-nano-tape',
    'inspirational-wall-stickers':                'softlifee_products/inspirational-wall-stickers',
    'gold-decor-tape':                            'softlifee_products/gold-decor-tape',
    'vine-leaf-room-decor':                       'softlifee_products/vine-leaf-room-decor',
    'decorative-wall-hooks':                      'softlifee_products/decorative-wall-hooks',
    'self-adhesive-countertop-film':              'softlifee_products/self-adhesive-countertop-film',
    'tote-bag':                                   'softlifee_products/tote-bag',
    'smart-watch-set':                            'softlifee_products/smart-watch-set',
    'smart-watch-series-8':                       'softlifee_products/smart-watch-series-8',
    'matte-stanley-tumbler':                      'softlifee_products/matte-stanley-tumbler',
    'stanley-cup':                                'softlifee_products/stanley-cup',
    'stanley-cup-accessories':                    'softlifee_products/stanley-cup-accessories',
    'happy-supply-chain-water-bottle':            'softlifee_products/happy-supply-chain-water-bottle',
    'laptop-stand':                               'softlifee_products/laptop-stand',
    'phone-suction-cup':                          'softlifee_products/phone-suction-cup',
    'rgb-phone-led-light':                        'softlifee_products/rgb-phone-led-light',
    'wireless-fill-light-bt-remote-tripod':       'softlifee_products/wireless-fill-light-bt-remote-tripod',
    'bubble-gun':                                 'softlifee_products/bubble-gun',
    'usb-cigarettes-lighter-mobile-phone-holder': 'softlifee_products/usb-cigarettes-lighter-mobile-phone-holder',
    'fancy-barbie-pen':                           'softlifee_products/fancy-barbie-pen',
    'green-stick-mask':                           'softlifee_products/green-stick-mask',
    'star-pimple-patches':                        'softlifee_products/star-pimple-patches',
    'compressed-facial-towel':                    'softlifee_products/compressed-facial-towel',
    'sadoer-ampoules-facial-mask':                'softlifee_products/sadoer-ampoules-facial-mask',
    'tongue-scrubber':                            'softlifee_products/tongue-scrubber',
    'travel-box':                                 'softlifee_products/travel-box',
    'travel-kit':                                 'softlifee_products/travel-kit',
    'floral-fruit-fragrance-hand-cream':          'softlifee_products/floral-fruit-fragrance-hand-cream',
    'boob-tape':                                  'softlifee_products/boob-tape',
    'transparent-boobs-lifter':                   'softlifee_products/transparent-boobs-lifter',
}


class Command(BaseCommand):
    help = 'Seed the database with all 52 Soft Lifee products'

    def add_arguments(self, parser):
        parser.add_argument('--update', action='store_true', help='Update existing products with latest data.')
        parser.add_argument('--reset',  action='store_true', help='DELETE all products and categories first.')

    def handle(self, *args, **options):
        from apps.products.models import Category, Subcategory, Product, ColorVariant, ProductImage

        if options['reset']:
            self.stdout.write(self.style.WARNING('Resetting catalogue…'))
            Product.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.WARNING('  ✓ Cleared.\n'))

        # ── Categories & subcategories ─────────────────────────────────────────
        self.stdout.write('Syncing categories…')
        # (category_name, sub_slug) → Subcategory  — handles same slug in multiple categories
        sub_lookup = {}

        for cat_data in CATALOGUE['categories']:
            cat, cat_created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={'name': cat_data['name'], 'order': cat_data['order']},
            )
            if not cat_created and options['update']:
                cat.name = cat_data['name']
                cat.order = cat_data['order']
                cat.save(update_fields=['name', 'order'])

            self.stdout.write(f'  [{"created" if cat_created else "exists"}] {cat.name}')

            for sub_data in cat_data.get('subcategories', []):
                sub, sub_created = Subcategory.objects.get_or_create(
                    category=cat, slug=sub_data['slug'],
                    defaults={'name': sub_data['name'], 'order': sub_data['order']},
                )
                if not sub_created and options['update']:
                    sub.name = sub_data['name']
                    sub.order = sub_data['order']
                    sub.save(update_fields=['name', 'order'])

                sub_lookup[(cat_data['name'], sub_data['slug'])] = sub
                self.stdout.write(f'      [{"created" if sub_created else "exists"}] {sub.name}')

        # ── Products ───────────────────────────────────────────────────────────
        self.stdout.write('\nSyncing products…')
        created = updated = skipped = 0

        for p in CATALOGUE['products']:
            try:
                category = Category.objects.get(name=p['category'])
            except Category.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'  ✗ Category "{p["category"]}" not found — skip {p["name"]}'))
                continue

            sub_key     = p.get('subcategory')
            subcategory = sub_lookup.get(sub_key) if sub_key else None

            fields = dict(
                name        = p['name'],
                category    = category,
                subcategory = subcategory,
                description = p['description'],
                details     = p['details'],
                price       = p['price'],
                badge       = p.get('badge', ''),
                in_stock    = p.get('in_stock', True),
                stock_count = p.get('stock_count', 0),
            )

            product, p_created = Product.objects.get_or_create(slug=p['slug'], defaults=fields)

            if not p_created:
                if options['update']:
                    for k, v in fields.items():
                        setattr(product, k, v)
                    product.save()
                    updated += 1
                    self.stdout.write(f'  [updated] {product.name}')
                else:
                    skipped += 1
                    self.stdout.write(f'  [exists]  {product.name}')
                    continue
            else:
                created += 1
                self.stdout.write(self.style.SUCCESS(f'  [created] {product.name}'))

            # Colour variants
            existing = set(ColorVariant.objects.filter(product=product).values_list('label', flat=True))
            for i, c in enumerate(p.get('colors', [])):
                if c['label'] not in existing:
                    ColorVariant.objects.create(
                        product=product, label=c['label'], hex_code=c['hex_code'],
                        image='placeholder', order=i,
                    )
                    self.stdout.write(f'        + colour: {c["label"]}')

            # Primary image — create from known Cloudinary public_id if missing
            cloudinary_id = PRODUCT_IMAGE_IDS.get(p['slug'])
            if cloudinary_id:
                has_primary = ProductImage.objects.filter(product=product, is_primary=True).exists()
                if not has_primary:
                    # Store as image/upload/<public_id> to match cloudinary_storage format
                    ProductImage.objects.create(
                        product    = product,
                        image      = f'image/upload/{cloudinary_id}',
                        alt_text   = p['name'],
                        is_primary = True,
                        order      = 0,
                    )
                    self.stdout.write(f'        + image: {cloudinary_id}')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Done. Created: {created}  |  Updated: {updated}  |  Skipped: {skipped}'
        ))
