"""
Django management command to populate the database with realistic test data.
This creates products, users, orders, and reviews to showcase the ML recommendation system.
"""
import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify
from shop.models import Category, Product, Order, OrderItem, Review, Rating

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate database with realistic test data for the e-commerce shop'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            Review.objects.all().delete()
            Rating.objects.all().delete()
            OrderItem.objects.all().delete()
            Order.objects.all().delete()
            Product.objects.all().delete()
            # Don't delete categories - keep existing ones
            # Only delete test users (not admin)
            User.objects.filter(email__endswith='@test.com').delete()
            self.stdout.write(self.style.SUCCESS('[OK] Data cleared'))

        self.stdout.write(self.style.SUCCESS('Starting data population...'))

        # Create test users
        users = self.create_users()

        # Get or create categories
        categories = self.ensure_categories()

        # Create products
        products = self.create_products(categories)

        # Create orders with realistic patterns
        self.create_orders(users, products)

        # Create reviews and ratings
        self.create_reviews(users, products)

        self.stdout.write(self.style.SUCCESS('[OK] Database populated successfully!'))
        self.stdout.write(self.style.SUCCESS(f'  - {len(users)} test users created'))
        self.stdout.write(self.style.SUCCESS(f'  - {len(products)} products created'))
        self.stdout.write(self.style.SUCCESS(f'  - Multiple orders and reviews generated'))
        self.stdout.write(self.style.SUCCESS('\nTest user credentials (use username to login):'))
        for user in users[:3]:
            self.stdout.write(f'  Username: {user.username} | Password: test123')

    def create_users(self):
        """Create diverse test users with different purchasing patterns"""
        self.stdout.write('Creating test users...')

        users_data = [
            {'username': 'ana_popescu', 'email': 'ana@test.com', 'first_name': 'Ana', 'last_name': 'Popescu'},
            {'username': 'ion_ionescu', 'email': 'ion@test.com', 'first_name': 'Ion', 'last_name': 'Ionescu'},
            {'username': 'maria_gheorghe', 'email': 'maria@test.com', 'first_name': 'Maria', 'last_name': 'Gheorghe'},
            {'username': 'alex_dumitru', 'email': 'alex@test.com', 'first_name': 'Alex', 'last_name': 'Dumitru'},
            {'username': 'elena_stan', 'email': 'elena@test.com', 'first_name': 'Elena', 'last_name': 'Stan'},
            {'username': 'cristian_popa', 'email': 'cristian@test.com', 'first_name': 'Cristian', 'last_name': 'Popa'},
            {'username': 'diana_radu', 'email': 'diana@test.com', 'first_name': 'Diana', 'last_name': 'Radu'},
        ]

        users = []
        for data in users_data:
            user, created = User.objects.get_or_create(
                email=data['email'],
                defaults={
                    'username': data['username'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                }
            )
            if created:
                user.set_password('test123')
                user.save()
            users.append(user)

        return users

    def ensure_categories(self):
        """Ensure all necessary categories exist"""
        self.stdout.write('Ensuring categories exist...')

        category_names = [
            'Electronice',
            'Îmbrăcăminte',
            'Casă & Grădină',
            'Cărți',
            'Sport & Outdoor',
            'Jucării',
            'Cosmetice & Îngrijire',
            'Alimentare',
        ]

        categories = {}
        for name in category_names:
            cat, created = Category.objects.get_or_create(
                name=name,
                defaults={'slug': slugify(name)}
            )
            categories[name] = cat

        return categories

    def create_products(self, categories):
        """Create diverse products across categories"""
        self.stdout.write('Creating products...')

        products_data = [
            # Electronice
            ('Laptop Gaming ASUS ROG', 'Electronice', 4999, 'Laptop performant cu procesor Intel i7, 16GB RAM, RTX 3060, perfect pentru gaming și aplicații profesionale.'),
            ('Smartphone Samsung Galaxy S23', 'Electronice', 3499, 'Telefon flagship cu ecran AMOLED, cameră de 50MP și baterie de lungă durată.'),
            ('Tabletă iPad Air', 'Electronice', 2999, 'Tabletă Apple cu procesor M1, display Retina și suport Apple Pencil.'),
            ('Căști Wireless Sony WH-1000XM5', 'Electronice', 1299, 'Căști premium cu noise cancelling, sunet Hi-Res și baterie 30h.'),
            ('Smart Watch Garmin Fenix 7', 'Electronice', 2199, 'Ceas sport multisport cu GPS, monitorizare avansată și autonomie extinsă.'),
            ('Cameră Foto Canon EOS R6', 'Electronice', 8999, 'Cameră mirrorless full-frame cu 20MP, video 4K și stabilizare în corp.'),
            ('Consolă PlayStation 5', 'Electronice', 2499, 'Consolă next-gen cu SSD ultra-rapid, ray tracing și controller haptic.'),
            ('Monitor Gaming LG UltraGear', 'Electronice', 1899, 'Monitor 27" QHD, 144Hz, timp răspuns 1ms, perfect pentru gaming competitiv.'),
            ('Router WiFi 6 ASUS', 'Electronice', 899, 'Router dual-band cu WiFi 6, AiMesh și protecție AiProtection Pro.'),
            ('Boxe Bluetooth JBL Charge 5', 'Electronice', 599, 'Boxă portabilă waterproof cu sunet puternic și baterie 20h.'),

            # Îmbrăcăminte
            ('Geacă de Iarnă The North Face', 'Îmbrăcăminte', 899, 'Geacă călduroasă și impermeabilă, perfectă pentru temperaturi extreme.'),
            ('Adidași Nike Air Max', 'Îmbrăcăminte', 549, 'Adidași sport confortabili cu tehnologia Air pentru amortizare superioară.'),
            ('Costum Elegant Hugo Boss', 'Îmbrăcăminte', 1999, 'Costum business din lână premium, croială modernă și finisaje impecabile.'),
            ('Rochie de Seară Elegantă', 'Îmbrăcăminte', 499, 'Rochie elegantă din mătase, design rafinat pentru ocazii speciale.'),
            ('Jeans Levis 501', 'Îmbrăcăminte', 399, 'Jeans clasici din denim de calitate, croială relaxată și durabilitate garantată.'),
            ('Pulover Cashmere', 'Îmbrăcăminte', 699, 'Pulover din cashmere 100%, mătăsos și cald pentru sezonul rece.'),

            # Casă & Grădină
            ('Aspirator Robot iRobot Roomba', 'Casă & Grădină', 1799, 'Aspirator inteligent cu mapare cameră, navigare smart și golire automată.'),
            ('Set Oale Tefal Ingenio', 'Casă & Grădină', 699, 'Set 10 piese cu mânere detașabile, înveliș antiaderent și compatibilitate cuptor.'),
            ('Mașină de Cafea DeLonghi', 'Casă & Grădină', 2199, 'Espressor automat cu râșniță integrată, spumant lapte și display tactil.'),
            ('Scaun Gaming ergonomic', 'Casă & Grădină', 899, 'Scaun cu suport lombar, tetieră ajustabilă și piele ecologică respirabilă.'),
            ('Canapea Modulară 3 locuri', 'Casă & Grădină', 3499, 'Canapea modernă și confortabilă, tapițerie rezistentă și perne incluse.'),
            ('Masă Extensibilă din Lemn', 'Casă & Grădină', 1599, 'Masă din lemn masiv de stejar, extensibilă până la 8 persoane.'),

            # Cărți
            ('Sapiens - Yuval Noah Harari', 'Cărți', 59, 'Bestseller internațional despre istoria omenirii și evoluția societății.'),
            ('Atomic Habits - James Clear', 'Cărți', 49, 'Ghid practic pentru formarea obiceiurilor bune și eliminarea celor rele.'),
            ('Mândrie și Prejudecată - Jane Austen', 'Cărți', 39, 'Roman clasic despre dragoste, orgoliu și transformare personală.'),
            ('1984 - George Orwell', 'Cărți', 45, 'Distopie clasică despre totalitarism și supraveghere.'),
            ('Înțelepciunea Incertitudinii', 'Cărți', 55, 'Carte de dezvoltare personală despre acceptarea incertitudinii.'),

            # Sport & Outdoor
            ('Bicicletă Montană Trek', 'Sport & Outdoor', 3499, 'Bicicletă MTB cu suspensie completă, frâne hidraulice și 27 viteze.'),
            ('Cort 4 Persoane Coleman', 'Sport & Outdoor', 799, 'Cort rezistent la apă, ventilație optimă și montare rapidă.'),
            ('Rucsac Trekking 50L', 'Sport & Outdoor', 449, 'Rucsac ergonomic cu sistem de hidratare, compartimente multiple și husă ploaie.'),
            ('Barcă Gonflabilă Intex', 'Sport & Outdoor', 599, 'Barcă pentru 3 persoane, material rezistent și vâsle incluse.'),
            ('Set Greutăți Reglabile', 'Sport & Outdoor', 899, 'Set gantere ajustabile 2-24kg, compacte și versatile pentru antrenament acasă.'),

            # Jucării
            ('LEGO Star Wars Millennium Falcon', 'Jucării', 799, 'Set LEGO iconic cu 1351 piese, detalii autentice și minifigurine.'),
            ('Barbie Dreamhouse', 'Jucării', 599, 'Casă de vis în 3 etaje cu piscină, tobogan și 8 camere.'),
            ('Dronă cu Cameră 4K', 'Jucării', 1299, 'Dronă pentru copii și adulți, cameră UHD, stabilizare și RC.'),
            ('Set Trăsuri Hot Wheels', 'Jucării', 149, 'Pistă cu looping-uri, rampe și 3 mașinuțe incluse.'),

            # Cosmetice & Îngrijire
            ('Ser Facial Vitamin C', 'Cosmetice & Îngrijire', 149, 'Ser anti-aging cu vitamina C pură, iluminează și uniformizează tenul.'),
            ('Parfum Chanel No. 5', 'Cosmetice & Îngrijire', 599, 'Parfum iconic feminin, arome florale clasice și eleganță atemporală.'),
            ('Set Pensule Machiaj Professional', 'Cosmetice & Îngrijire', 299, 'Set 15 pensule premium, păr sintetic moale și husă elegantă.'),
            ('Cremă de Față La Roche-Posay', 'Cosmetice & Îngrijire', 89, 'Cremă hidratantă pentru ten sensibil, apă termală și protecție.'),

            # Alimentare
            ('Cafea Boabe Lavazza', 'Alimentare', 79, 'Cafea premium arabica, aromă intensă și note ciocolatate, 1kg.'),
            ('Miere de Salcâm Bio', 'Alimentare', 45, 'Miere naturală 100%, din zone montane, fără aditivi.'),
            ('Set Condimente Internaționale', 'Alimentare', 129, 'Colecție 20 condimente premium din întreaga lume.'),
            ('Ceai Verde Organic', 'Alimentare', 35, 'Ceai verde japonez, antioxidanți naturali, 100 plicuri.'),
        ]

        products = []
        for name, category_name, price, description in products_data:
            slug = slugify(name)
            product, created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'category': categories[category_name],
                    'price': price,
                    'description': description,
                }
            )
            products.append(product)

        return products

    def create_orders(self, users, products):
        """Create realistic purchase patterns to enable collaborative filtering"""
        self.stdout.write('Creating orders with realistic patterns...')

        # Define user personas with specific buying patterns
        electronics_lover = users[0]  # Ana - loves electronics
        fashion_enthusiast = users[1]  # Ion - fashion and accessories
        home_decorator = users[2]  # Maria - home and garden
        book_reader = users[3]  # Alex - books and education
        sports_person = users[4]  # Elena - sports and outdoor
        mixed_shopper_1 = users[5]  # Cristian - varied interests
        mixed_shopper_2 = users[6]  # Diana - varied interests

        # Electronics lover orders
        self._create_user_orders(electronics_lover, products, [
            (['Laptop Gaming ASUS ROG', 'Mouse Gaming'], 7),
            (['Smart Watch Garmin Fenix 7', 'Căști Wireless Sony WH-1000XM5'], 14),
            (['Monitor Gaming LG UltraGear', 'Boxe Bluetooth JBL Charge 5'], 21),
        ])

        # Fashion enthusiast orders
        self._create_user_orders(fashion_enthusiast, products, [
            (['Adidași Nike Air Max', 'Jeans Levis 501'], 5),
            (['Geacă de Iarnă The North Face', 'Pulover Cashmere'], 12),
            (['Costum Elegant Hugo Boss'], 18),
        ])

        # Home decorator orders
        self._create_user_orders(home_decorator, products, [
            (['Aspirator Robot iRobot Roomba', 'Mașină de Cafea DeLonghi'], 10),
            (['Canapea Modulară 3 locuri', 'Masă Extensibilă din Lemn'], 20),
            (['Set Oale Tefal Ingenio', 'Scaun Gaming ergonomic'], 25),
        ])

        # Book reader orders
        self._create_user_orders(book_reader, products, [
            (['Sapiens - Yuval Noah Harari', 'Atomic Habits - James Clear', '1984 - George Orwell'], 3),
            (['Mândrie și Prejudecată - Jane Austen', 'Înțelepciunea Incertitudinii'], 15),
            (['Cafea Boabe Lavazza', 'Ceai Verde Organic'], 22),
        ])

        # Sports person orders
        self._create_user_orders(sports_person, products, [
            (['Bicicletă Montană Trek', 'Rucsac Trekking 50L'], 8),
            (['Set Greutăți Reglabile', 'Smart Watch Garmin Fenix 7'], 16),
            (['Cort 4 Persoane Coleman', 'Barcă Gonflabilă Intex'], 24),
        ])

        # Mixed shoppers - create overlap for collaborative filtering
        self._create_user_orders(mixed_shopper_1, products, [
            (['Laptop Gaming ASUS ROG', 'Căști Wireless Sony WH-1000XM5'], 6),
            (['Bicicletă Montană Trek', 'Smart Watch Garmin Fenix 7'], 13),
            (['Sapiens - Yuval Noah Harari', 'Cafea Boabe Lavazza'], 19),
        ])

        self._create_user_orders(mixed_shopper_2, products, [
            (['Smartphone Samsung Galaxy S23', 'Set Pensule Machiaj Professional'], 4),
            (['Rochie de Seară Elegantă', 'Parfum Chanel No. 5'], 11),
            (['Aspirator Robot iRobot Roomba', 'Ser Facial Vitamin C'], 17),
        ])

        # Create some open orders (shopping carts)
        self._create_open_order(mixed_shopper_1, products, ['Consolă PlayStation 5', 'Monitor Gaming LG UltraGear'])
        self._create_open_order(fashion_enthusiast, products, ['Geacă de Iarnă The North Face'])

    def _create_user_orders(self, user, products, orders_data):
        """Helper to create completed orders for a user"""
        for product_names, days_ago in orders_data:
            order = Order.objects.create(
                user=user,
                is_open=False,
                created_at=timezone.now() - timedelta(days=days_ago)
            )

            for product_name in product_names:
                product = next((p for p in products if product_name in p.name), None)
                if product:
                    quantity = random.randint(1, 2)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=product.price
                    )

    def _create_open_order(self, user, products, product_names):
        """Helper to create an open order (shopping cart)"""
        order = Order.objects.create(user=user, is_open=True)

        for product_name in product_names:
            product = next((p for p in products if product_name in p.name), None)
            if product:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=1,
                    price=product.price
                )

    def create_reviews(self, users, products):
        """Create diverse reviews and ratings"""
        self.stdout.write('Creating reviews and ratings...')

        review_templates = {
            5: [
                ("Excelent!", "Produsul este extraordinary! Depășește așteptările și calitatea este premium. Recomand cu încredere!"),
                ("Perfect!", "Sunt extrem de mulțumit! Exact ce căutam, calitate superioară și livrare rapidă."),
                ("Cea mai bună achiziție!", "Nu am cuvinte! Este incredibil de bun, merită fiecare ban investit."),
            ],
            4: [
                ("Foarte bun", "Produs de calitate, exact ca în descriere. Mic minus la ambalaj, dar produsul în sine este foarte bun."),
                ("Recomand", "Sunt mulțumit de achiziție. Raport calitate-preț bun, ar putea fi îmbunătățite câteva detalii minore."),
                ("Bună achiziție", "În general mulțumit, produsul face ce trebuie. Poate puțin prea scump pentru ce oferă."),
            ],
            3: [
                ("OK", "Produs decent, nimic special. Face ce trebuie dar am văzut și mai bine pe piață."),
                ("Așteptări medii", "Nici bun, nici rău. Pentru preț am fi așteptat ceva mai mult, dar este folosibil."),
            ],
            2: [
                ("Dezamăgitor", "Nu corespunde descrierii. Calitatea este sub așteptări, nu recomand."),
            ],
        }

        # Create reviews for popular products
        popular_products = random.sample(products, min(30, len(products)))

        for product in popular_products:
            # Each product gets 1-4 reviews
            num_reviews = random.randint(1, 4)
            reviewers = random.sample(users, min(num_reviews, len(users)))

            for user in reviewers:
                # Check if user has purchased this product
                has_purchased = OrderItem.objects.filter(
                    order__user=user,
                    order__is_open=False,
                    product=product
                ).exists()

                if not has_purchased:
                    continue

                # Random rating (weighted towards positive)
                rating = random.choices([5, 4, 3, 2], weights=[50, 30, 15, 5])[0]

                # Get random review template
                if rating in review_templates:
                    title, content = random.choice(review_templates[rating])

                    Review.objects.create(
                        product=product,
                        user=user,
                        rating=rating,
                        title=title,
                        content=content,
                        created_at=timezone.now() - timedelta(days=random.randint(1, 20))
                    )

                    # Also create a Rating object for compatibility
                    Rating.objects.create(
                        product=product,
                        user=user,
                        score=rating
                    )
