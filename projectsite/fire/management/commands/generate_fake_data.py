from django.core.management.base import BaseCommand
from faker import Faker
from decimal import Decimal
import random
from fire.models import (
    Locations,
    Incident,
    FireStation,
    Firefighters,
    FireTruck,
    WeatherConditions,
)


class Command(BaseCommand):
    help = "Generate fake data for testing"

    def handle(self, *args, **kwargs):
        fake = Faker()

        # List of barangays in Puerto Princesa City with approximate latitudes and longitudes
        barangays = [
            {"name": "Bagong Sikat", "latitude": 9.7396, "longitude": 118.7357},
            {"name": "San Pedro", "latitude": 9.7621, "longitude": 118.7513},
            {"name": "Mangingisda", "latitude": 9.6954, "longitude": 118.7555},
            {"name": "San Manuel", "latitude": 9.7696, "longitude": 118.7305},
            {"name": "Santa Monica", "latitude": 9.7811, "longitude": 118.7321},
        ]

        def create_fake_data():
            for _ in range(random.randint(5, 20)):
                barangay = random.choice(barangays)

                location = Locations.objects.create(
                    name=barangay["name"],
                    latitude=Decimal(barangay["latitude"]),
                    longitude=Decimal(barangay["longitude"]),
                    address=fake.address(),
                    city="Puerto Princesa City",
                    country="Philippines",
                )

                fire_station = FireStation.objects.create(
                    name=fake.company(),
                    latitude=Decimal(barangay["latitude"]),
                    longitude=Decimal(barangay["longitude"]),
                    address=fake.address(),
                    city="Puerto Princesa City",
                    country="Philippines",
                )

                firefighter = Firefighters.objects.create(
                    name=fake.name(),
                    rank=random.choice(
                        [
                            "Probationary Firefighter",
                            "Firefighter I",
                            "Firefighter II",
                            "Firefighter III",
                            "Driver",
                            "Captain",
                            "Battalion Chief",
                        ]
                    ),
                    experience_level=random.choice(
                        ["1 year", "3 years", "5 years", "10 years"]
                    ),
                    station=fire_station,
                )

                fire_truck = FireTruck.objects.create(
                    truck_number=fake.license_plate(),
                    model=fake.word(),
                    capacity=f"{random.randint(1000, 5000)} liters",
                    station=fire_station,
                )

                incident = Incident.objects.create(
                    location=location,
                    date_time=fake.date_time_this_year(),
                    severity_level=random.choice(
                        ["Minor Fire", "Moderate Fire", "Major Fire"]
                    ),
                    description=fake.text(max_nb_chars=200),
                )

                weather_conditions = WeatherConditions.objects.create(
                    incident=incident,
                    temperature=Decimal(fake.random_number(digits=2, fix_len=True)),
                    humidity=Decimal(fake.random_number(digits=2, fix_len=True)),
                    wind_speed=Decimal(fake.random_number(digits=2, fix_len=True)),
                    weather_description=fake.word(),
                )

        create_fake_data()
        self.stdout.write(self.style.SUCCESS("Fake data created successfully."))
