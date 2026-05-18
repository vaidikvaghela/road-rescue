import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from services.models import ServiceType, ServiceProvider
from emergency.models import EmergencyRequest

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Seeding database...'))

        # Superuser
        if not User.objects.filter(email='admin@roadrescue.com').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@roadrescue.com',
                password='admin123',
                first_name='Admin',
                last_name='RoadRescue',
                role='admin',
            )
            self.stdout.write(self.style.SUCCESS('  Created superuser: admin@roadrescue.com / admin123'))

        # Service Types
        types_data = [
            ('Engine Repair', 'Full engine diagnostics and repair', '⚙️'),
            ('Tyre Change',   'Flat tyre replacement and repair',   '🛞'),
            ('Towing',        'Vehicle towing and recovery',        '🚛'),
            ('Battery Jump',  'Dead battery jump start',            '🔋'),
            ('Fuel Delivery', 'Emergency fuel delivery',            '⛽'),
            ('Electrical',    'Electrical system repair',           '⚡'),
            ('AC Repair',     'Air conditioning repair',            '❄️'),
            ('Denting',       'Denting and painting',               '🎨'),
        ]
        service_types = []
        for name, desc, icon in types_data:
            st, _ = ServiceType.objects.get_or_create(name=name, defaults={'description': desc, 'icon': icon})
            service_types.append(st)
        self.stdout.write(self.style.SUCCESS(f'  {len(service_types)} service types ready'))

        # Providers
        providers_data = [
            ('AutoFix Pro',         'Ahmedabad', 'Gujarat', '380001', 23.0300, 72.5600, 350),
            ('SpeedTow Services',   'Ahmedabad', 'Gujarat', '380006', 23.0150, 72.5820, 500),
            ('QuickRepair Mobile',  'Surat',     'Gujarat', '395001', 21.1702, 72.8311, 280),
            ('Mechanic 24x7',       'Vadodara',  'Gujarat', '390001', 22.3072, 73.1812, 400),
            ('City Auto Works',     'Ahmedabad', 'Gujarat', '380009', 23.0400, 72.5600, 320),
        ]

        for i, (biz, city, state, pin, lat, lon, fee) in enumerate(providers_data, 1):
            email = f'provider{i}@roadrescue.com'
            if not User.objects.filter(email=email).exists():
                u = User.objects.create_user(
                    username=f'provider{i}',
                    email=email,
                    password='provider123',
                    role='provider',
                    first_name=biz.split()[0],
                    last_name='Services',
                )
                sp = ServiceProvider.objects.create(
                    user=u,
                    business_name=biz,
                    city=city, state=state, pincode=pin,
                    phone=f'+91 9810{i:05d}',
                    email=email,
                    address=f'{random.randint(1,999)}, Main Road, {city}',
                    latitude=lat, longitude=lon,
                    base_fee=fee,
                    status='active',
                    is_available=True,
                    is_24_7=random.choice([True, False]),
                    rating=round(random.uniform(3.8, 5.0), 1),
                )
                sp.service_types.set(random.sample(service_types, k=random.randint(2, 4)))
        self.stdout.write(self.style.SUCCESS(f'  {len(providers_data)} providers seeded'))

        # Emergency Requests
        issues   = ['flat_tyre', 'engine_failure', 'battery_dead', 'out_of_fuel', 'other']
        vehicles = ['car', 'suv', 'motorcycle', 'truck']
        statuses = ['pending', 'assigned', 'en_route', 'completed', 'completed']

        for i in range(10):
            EmergencyRequest.objects.create(
                requester_name=f'Test User {i+1}',
                requester_phone=f'+91 98765 {i:05d}',
                location_address=f'NH-{random.randint(1,99)}, Ahmedabad',
                vehicle_type=random.choice(vehicles),
                issue_type=random.choice(issues),
                status=random.choice(statuses),
                priority=random.choice(['low', 'medium', 'high']),
                notes='Sample seeded request.',
            )
        self.stdout.write(self.style.SUCCESS('  10 emergency requests seeded'))

        self.stdout.write(self.style.SUCCESS('\nDone! Run: python manage.py runserver'))
        self.stdout.write(self.style.WARNING('  Portal:    http://127.0.0.1:8000/'))
        self.stdout.write(self.style.WARNING('  Admin:     http://127.0.0.1:8000/admin/'))
        self.stdout.write(self.style.WARNING('  Register:  http://127.0.0.1:8000/register/'))
        self.stdout.write(self.style.WARNING('  Login:     http://127.0.0.1:8000/login/'))
        self.stdout.write(self.style.WARNING('  API Docs:  http://127.0.0.1:8000/api/docs/'))
