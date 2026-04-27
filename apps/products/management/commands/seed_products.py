"""
Usage:
    python manage.py seed_products             # create missing items only
    python manage.py seed_products --update    # also update existing products
    python manage.py seed_products --reset     # WIPE all products/categories first
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify


# ── Catalogue definition ──────────────────────────────────────────────────────
CATALOGUE = {
    'categories': [
        {
            'name': 'Home Essentials',
            'slug': 'home-essentials',
            'order': 1,
            'subcategories': [
                {'name': 'Smart Gadgets',  'slug': 'smart-gadgets', 'order': 1},
                {'name': 'Bathroom',       'slug': 'bathroom',      'order': 2},
                {'name': 'Kitchen',        'slug': 'kitchen',       'order': 3},
                {'name': 'Lighting',       'slug': 'lighting',      'order': 4},
            ],
        },
        {
            'name': 'Accessories',
            'slug': 'accessories',
            'order': 2,
            'subcategories': [
                {'name': 'Bags',      'slug': 'bags',      'order': 1},
                {'name': 'Jewellery', 'slug': 'jewelry',   'order': 2},
                {'name': 'Drinkware', 'slug': 'drinkware', 'order': 3},
            ],
        },
        {
            'name': 'Skincare',
            'slug': 'skincare',
            'order': 3,
            'subcategories': [
                {'name': 'Face',        'slug': 'face',        'order': 1},
                {'name': 'Travel Kits', 'slug': 'travel-kits', 'order': 2},
            ],
        },
    ],

    'products': [
        {
            'name':        'Diffuser',
            'slug':        'diffuser',
            'category':    'Home Essentials',
            'subcategory': 'smart-gadgets',
            'price':       15000,
            'badge':       'best_seller',
            'in_stock':    True,
            'stock_count': 50,
            'description': (
                'Transform your space with our premium ultrasonic diffuser. '
                'Combines aromatherapy and cool mist humidification to create '
                'the perfect ambiance for relaxation, focus, or sleep.'
            ),
            'details': [
                'Ultrasonic cold mist technology',
                'Runs up to 8 hours continuously',
                'Auto shut-off when water runs out',
                'Soft LED mood lighting (7 colours)',
                'BPA-free premium materials',
                'Ideal room size: up to 30m²',
            ],
            'colors': [],
            'sizes':  [],
        },
        {
            'name':        'Green Stick Mask',
            'slug':        'green-stick-mask',
            'category':    'Skincare',
            'subcategory': 'face',
            'price':       5000,
            'badge':       'top_rated',
            'in_stock':    True,
            'stock_count': 100,
            'description': (
                'A deep-cleansing green tea infused stick mask that draws out '
                'impurities, unclogs pores and leaves skin feeling refreshed, '
                'smooth and perfectly balanced.'
            ),
            'details': [
                'Green tea & charcoal formula',
                'Suitable for all skin types',
                'Dermatologist tested',
                'No parabens or sulphates',
                'Stick applicator — zero mess',
                'Use 2–3 times per week',
            ],
            'colors': [],
            'sizes':  [],
        },
        {
            'name':        'Tote Bag',
            'slug':        'tote-bag',
            'category':    'Accessories',
            'subcategory': 'bags',
            'price':       8500,
            'badge':       'new',
            'in_stock':    True,
            'stock_count': 40,
            'description': (
                'A versatile and stylish tote bag designed for the modern woman. '
                'Spacious enough for everything you need, minimal enough to go everywhere.'
            ),
            'details': [
                'Premium canvas material',
                'Reinforced handles',
                'Internal zip pocket',
                'Dimensions: 40cm × 35cm × 12cm',
                'Available in multiple colours',
                'Machine washable',
            ],
            'colors': [
                {'label': 'Alpine Blue', 'hex_code': '#4A7FA5'},
                {'label': 'Black',       'hex_code': '#1A1A2E'},
                {'label': 'Blush',       'hex_code': '#F4B8C1'},
            ],
            'sizes': [],
        },
        {
            'name':        '3D Sand Drop',
            'slug':        '3d-sand-drop',
            'category':    'Home Essentials',
            'subcategory': 'smart-gadgets',
            'price':       10000,
            'badge':       'trending',
            'in_stock':    True,
            'stock_count': 30,
            'description': (
                'A mesmerising kinetic sand sculpture that creates ever-changing '
                'landscapes as the coloured sand slowly flows and settles. '
                'The ultimate desk art piece.'
            ),
            'details': [
                'Borosilicate glass frame',
                'Non-toxic coloured sand',
                'Creates unique patterns every time',
                'Dimensions: 20cm × 15cm',
                'Sealed — no maintenance required',
                'Great gift for any occasion',
            ],
            'colors': [],
            'sizes':  [],
        },
        {
            'name':        'Bathroom Organizer',
            'slug':        'bathroom-organizer',
            'category':    'Home Essentials',
            'subcategory': 'bathroom',
            'price':       15000,
            'badge':       'best_seller',
            'in_stock':    True,
            'stock_count': 60,
            'description': (
                'Keep your bathroom clutter-free with this multi-tier organizer. '
                'Perfect for toiletries, skincare products and accessories — '
                'everything within reach and beautifully organised.'
            ),
            'details': [
                'Rust-resistant stainless steel',
                '3-tier storage system',
                'Easy install — no drilling required',
                'Holds up to 10kg per shelf',
                'Dimensions: 25cm × 60cm',
                'Wipe clean surface',
            ],
            'colors': [],
            'sizes':  [],
        },
        {
            'name':        'Smart-Watch Set',
            'slug':        'smart-watch-set',
            'category':    'Accessories',
            'subcategory': 'jewelry',
            'price':       40000,
            'badge':       'premium',
            'in_stock':    True,
            'stock_count': 20,
            'description': (
                'A premium smart watch bundle that tracks your fitness goals, '
                'monitors your health metrics and keeps you connected — '
                'all with a sleek, luxury aesthetic.'
            ),
            'details': [
                'Heart rate & SpO2 monitoring',
                '7-day battery life',
                'IP68 water resistant',
                '100+ sport modes',
                'Custom watch faces',
                'Compatible: iOS & Android',
            ],
            'colors': [
                {'label': 'Black',  'hex_code': '#1A1A2E'},
                {'label': 'Silver', 'hex_code': '#C0C0C0'},
                {'label': 'Gold',   'hex_code': '#D4AF37'},
            ],
            'sizes': [],
        },
        {
            'name':        'Matte Stanley Tumbler',
            'slug':        'matte-stanley-tumbler',
            'category':    'Accessories',
            'subcategory': 'drinkware',
            'price':       18000,
            'badge':       'new',
            'in_stock':    True,
            'stock_count': 80,
            'description': (
                'The iconic Stanley tumbler in a luxurious matte finish. '
                'Double-wall vacuum insulation keeps your drinks hot for 7 hours '
                'and cold for 24 hours. Elevate your daily hydration.'
            ),
            'details': [
                'Double-wall vacuum insulation',
                'Hot: 7hrs · Iced: 24hrs · Cold: 3 days',
                'BPA-free 18/8 stainless steel',
                'Capacity: 40oz (1.18L)',
                'Fits most car cup holders',
                'Leak-proof lid with carry handle',
            ],
            'colors': [
                {'label': 'Blush',    'hex_code': '#F4B8C1'},
                {'label': 'Sage',     'hex_code': '#8FAF8F'},
                {'label': 'Charcoal', 'hex_code': '#3D3D3D'},
                {'label': 'Cream',    'hex_code': '#FFF8E7'},
                {'label': 'Lilac',    'hex_code': '#C4A8D4'},
                {'label': 'Navy',     'hex_code': '#1A1A4E'},
            ],
            'sizes': [],
        },
        {
            'name':        'Flower Vase',
            'slug':        'flower-vase',
            'category':    'Home Essentials',
            'subcategory': 'kitchen',
            'price':       12000,
            'badge':       'new',
            'in_stock':    True,
            'stock_count': 35,
            'description': (
                'A beautifully crafted ceramic flower vase that adds natural '
                'elegance to any room. The minimalist design complements both '
                'fresh and dried flower arrangements.'
            ),
            'details': [
                'Premium glazed ceramic',
                'Height: 28cm, Diameter: 12cm',
                'Suitable for fresh & dried flowers',
                'Waterproof interior lining',
                'Scratch-resistant base',
                'Dishwasher safe',
            ],
            'colors': [
                {'label': 'White',      'hex_code': '#FAFAFA'},
                {'label': 'Beige',      'hex_code': '#E8D5B0'},
                {'label': 'Terracotta', 'hex_code': '#C4553A'},
            ],
            'sizes': [],
        },
        {
            'name':        'Ceramic Cup Set',
            'slug':        'ceramic-cup-set',
            'category':    'Home Essentials',
            'subcategory': 'kitchen',
            'price':       22000,
            'badge':       'new',
            'in_stock':    True,
            'stock_count': 25,
            'description': (
                'A curated set of artisan ceramic cups that transform your '
                'morning ritual into a luxury experience. Each piece is '
                'handcrafted with subtle variations that make every cup unique.'
            ),
            'details': [
                'Set of 4 handcrafted cups',
                'Capacity: 350ml each',
                'Lead-free glazed ceramic',
                'Microwave & dishwasher safe',
                'Gift box packaging included',
                'Available in 3 colour palettes',
            ],
            'colors': [
                {'label': 'Stone', 'hex_code': '#9E9E9E'},
                {'label': 'White', 'hex_code': '#FAFAFA'},
                {'label': 'Sage',  'hex_code': '#8FAF8F'},
            ],
            'sizes': [],
        },
        {
            'name':        'Travel Box',
            'slug':        'travel-box',
            'category':    'Skincare',
            'subcategory': 'travel-kits',
            'price':       9500,
            'badge':       'new',
            'in_stock':    True,
            'stock_count': 45,
            'description': (
                'A compact, TSA-approved travel skincare organiser with '
                'leak-proof compartments. Keep your entire skincare routine '
                'perfectly organised on the go.'
            ),
            'details': [
                'TSA-approved dimensions',
                '6 leak-proof silicone bottles',
                'Clear design for airport security',
                'Hanging hook for easy access',
                'Waterproof outer shell',
                'Fits carry-on luggage perfectly',
            ],
            'colors': [],
            'sizes':  [],
        },
        {
            'name':        'Storage Basket',
            'slug':        'storage-basket',
            'category':    'Home Essentials',
            'subcategory': 'kitchen',
            'price':       7500,
            'badge':       'new',
            'in_stock':    True,
            'stock_count': 55,
            'description': (
                'A versatile woven storage basket that combines practicality '
                'with aesthetic appeal.'
            ),
            'details': [
                'Durable woven construction',
                'Dimensions: 30cm × 20cm × 15cm',
                'Handles for easy carrying',
                'Collapses flat for storage',
                'Holds up to 5kg',
                'Easy to clean surface',
            ],
            'colors': [],
            'sizes':  [],
        },
        {
            'name':        'Moonlight Lamp',
            'slug':        'moonlight-lamp',
            'category':    'Home Essentials',
            'subcategory': 'lighting',
            'price':       14500,
            'badge':       'new',
            'in_stock':    True,
            'stock_count': 40,
            'description': (
                'A stunning rechargeable rotating moon lamp that casts a magical '
                'celestial glow. 16 colour options controlled via remote or '
                'touch — the perfect mood light for any room.'
            ),
            'details': [
                '16 colour options',
                'Remote + touch control',
                'USB rechargeable (4hr charge = 8hr use)',
                '3 brightness levels',
                'Diameter: 15cm',
                'Auto-off timer: 1hr / 2hr / 4hr',
            ],
            'colors': [],
            'sizes':  [],
        },
        {
            'name':        'Crystal Diamond LED Lamp',
            'slug':        'crystal-diamond-led-lamp',
            'category':    'Home Essentials',
            'subcategory': 'lighting',
            'price':       13000,
            'badge':       'new',
            'in_stock':    True,
            'stock_count': 30,
            'description': (
                'A gorgeous crystal diamond LED table lamp that creates dazzling '
                'light patterns on your walls and ceiling.'
            ),
            'details': [
                'Faceted crystal design',
                'Warm white LED bulb included',
                'Touch dimmer (3 levels)',
                'USB + plug power options',
                'Height: 32cm',
                'Energy efficient — 5W',
            ],
            'colors': [],
            'sizes':  [],
        },
        {
            'name':        'Smart Watch (Series 8)',
            'slug':        'smart-watch-series-8',
            'category':    'Accessories',
            'subcategory': 'jewelry',
            'price':       25000,
            'badge':       'new',
            'in_stock':    True,
            'stock_count': 20,
            'description': (
                'The Series 8 smart watch brings premium health tracking and '
                'connectivity in a sleek, modern design.'
            ),
            'details': [
                'Always-on Retina display',
                'ECG & blood oxygen monitoring',
                'Crash detection feature',
                'IP6X dust resistant',
                '18-hour battery life',
                'Compatible with iOS & Android',
            ],
            'colors': [
                {'label': 'Midnight',  'hex_code': '#1A1A2E'},
                {'label': 'Silver',    'hex_code': '#C0C0C0'},
                {'label': 'Rose Gold', 'hex_code': '#B76E79'},
            ],
            'sizes': [],
        },
        {
            'name':        'Stanley Cup',
            'slug':        'stanley-cup',
            'category':    'Accessories',
            'subcategory': 'drinkware',
            'price':       17000,
            'badge':       'best_seller',
            'in_stock':    True,
            'stock_count': 120,
            'description': (
                'The legendary Stanley cup — a cultural icon and the ultimate '
                'hydration companion. Built to last a lifetime with vacuum '
                'insulation that actually works.'
            ),
            'details': [
                '40oz vacuum insulated',
                'Keeps cold 2+ days with ice',
                'Comfort grip handle',
                'Reusable straw included',
                'Fits cup holders',
                'Lifetime guarantee',
            ],
            'colors': [
                {'label': 'Desert Sage',  'hex_code': '#8FAF8F'},
                {'label': 'Cream',        'hex_code': '#FFF8E7'},
                {'label': 'Charcoal',     'hex_code': '#3D3D3D'},
                {'label': 'Blush',        'hex_code': '#F4B8C1'},
                {'label': 'Alpine Blue',  'hex_code': '#4A7FA5'},
                {'label': 'Terracotta',   'hex_code': '#C4553A'},
            ],
            'sizes': [],
        },
        {
            'name':        'Ultra-Portable Juicer Cup',
            'slug':        'ultra-portable-multi-functional-juicer-cup',
            'category':    'Home Essentials',
            'subcategory': 'kitchen',
            'price':       14000,
            'badge':       'best_seller',
            'in_stock':    True,
            'stock_count': 65,
            'description': (
                'A powerful 6-blade USB rechargeable juicer that squeezes '
                'fresh juice in under 30 seconds.'
            ),
            'details': [
                '6 surgical steel blades',
                'USB rechargeable (2hr = 15 uses)',
                'Capacity: 380ml',
                'Blends in < 30 seconds',
                'BPA-free tritan material',
                'Dishwasher safe (except motor)',
            ],
            'colors': [],
            'sizes':  [],
        },
    ],
}


class Command(BaseCommand):
    help = 'Seed the database with Soft Lifee product catalogue'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing products with catalogue data.',
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='DELETE all existing products and categories before seeding.',
        )

    def handle(self, *args, **options):
        from apps.products.models import Category, Subcategory, Product, ColorVariant

        do_update = options['update']
        do_reset  = options['reset']

        if do_reset:
            self.stdout.write(self.style.WARNING('Resetting product catalogue…'))
            Product.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.WARNING('  ✓ All products and categories deleted.\n'))

        # ── Categories & subcategories ────────────────────────────────────────
        self.stdout.write('Creating categories…')
        sub_lookup = {}   # slug → Subcategory instance

        for cat_data in CATALOGUE['categories']:
            cat, cat_created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name':  cat_data['name'],
                    'order': cat_data['order'],
                },
            )
            if not cat_created and do_update:
                cat.name  = cat_data['name']
                cat.order = cat_data['order']
                cat.save(update_fields=['name', 'order'])

            label = 'created' if cat_created else 'exists'
            self.stdout.write(f'  [{label}] Category: {cat.name}')

            for sub_data in cat_data.get('subcategories', []):
                sub, sub_created = Subcategory.objects.get_or_create(
                    category=cat,
                    slug=sub_data['slug'],
                    defaults={
                        'name':  sub_data['name'],
                        'order': sub_data['order'],
                    },
                )
                if not sub_created and do_update:
                    sub.name  = sub_data['name']
                    sub.order = sub_data['order']
                    sub.save(update_fields=['name', 'order'])

                sub_lookup[sub_data['slug']] = sub
                label = 'created' if sub_created else 'exists'
                self.stdout.write(f'      [{label}] Subcategory: {sub.name}')

        # ── Products ──────────────────────────────────────────────────────────
        self.stdout.write('\nCreating products…')
        created_count = 0
        updated_count = 0
        skipped_count = 0

        for p_data in CATALOGUE['products']:
            try:
                category = Category.objects.get(name=p_data['category'])
            except Category.DoesNotExist:
                self.stdout.write(self.style.ERROR(
                    f'  ✗ Category "{p_data["category"]}" not found — skipping {p_data["name"]}'
                ))
                continue

            subcategory = sub_lookup.get(p_data.get('subcategory', ''))

            product_fields = {
                'name':        p_data['name'],
                'category':    category,
                'subcategory': subcategory,
                'description': p_data['description'],
                'details':     p_data['details'],
                'price':       p_data['price'],
                'badge':       p_data.get('badge', ''),
                'in_stock':    p_data.get('in_stock', True),
                'stock_count': p_data.get('stock_count', 0),
            }

            product, p_created = Product.objects.get_or_create(
                slug=p_data['slug'],
                defaults=product_fields,
            )

            if not p_created:
                if do_update:
                    for k, v in product_fields.items():
                        setattr(product, k, v)
                    product.save()
                    updated_count += 1
                    self.stdout.write(f'  [updated] {product.name}')
                else:
                    skipped_count += 1
                    self.stdout.write(f'  [exists]  {product.name}')
                    continue
            else:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  [created] {product.name}'))

            # ── Color variants (only on create or --update) ───────────────
            if p_data.get('colors'):
                existing_labels = set(
                    ColorVariant.objects.filter(product=product).values_list('label', flat=True)
                )
                for i, color in enumerate(p_data['colors']):
                    if color['label'] not in existing_labels:
                        ColorVariant.objects.create(
                            product=product,
                            label=color['label'],
                            hex_code=color['hex_code'],
                            image='placeholder',   # upload via admin API
                            order=i,
                        )
                        self.stdout.write(f'        + colour: {color["label"]}')

        # ── Summary ───────────────────────────────────────────────────────────
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Done. Created: {created_count}  |  '
            f'Updated: {updated_count}  |  '
            f'Skipped: {skipped_count}'
        ))
        self.stdout.write(
            'Note: product images are not included — upload via the admin API '
            'or Django admin panel.'
        )
