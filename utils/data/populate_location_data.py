import os
import sys
import django
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogs.settings')
django.setup()

from django.utils.text import slugify

from country.models import Country
from state.models import State
from region.models import Region

# Country data
countries_data = [
    {"country_name": "India", "country_code": "IN", "continent": "Asia", "country_description": "Republic of India"},
    {"country_name": "United States", "country_code": "US", "continent": "North America", "country_description": "United States of America"},
    {"country_name": "United Kingdom", "country_code": "GB", "continent": "Europe", "country_description": "United Kingdom of Great Britain and Northern Ireland"},
    {"country_name": "Canada", "country_code": "CA", "continent": "North America", "country_description": "Canada"},
    {"country_name": "Australia", "country_code": "AU", "continent": "Oceania", "country_description": "Commonwealth of Australia"},
]

# State data
states_data = [
    {"state_name": "Karnataka", "state_code": "KA", "country_code": "IN"},
    {"state_name": "Maharashtra", "state_code": "MH", "country_code": "IN"},
    {"state_name": "Tamil Nadu", "state_code": "TN", "country_code": "IN"},
    {"state_name": "California", "state_code": "CA", "country_code": "US"},
    {"state_name": "Texas", "state_code": "TX", "country_code": "US"},
    {"state_name": "New York", "state_code": "NY", "country_code": "US"},
    {"state_name": "Ontario", "state_code": "ON", "country_code": "CA"},
    {"state_name": "Quebec", "state_code": "QC", "country_code": "CA"},
    {"state_name": "New South Wales", "state_code": "NSW", "country_code": "AU"},
    {"state_name": "Victoria", "state_code": "VIC", "country_code": "AU"},

    {"state_name": "Karnataka", "state_code": "KA", "country_code": "IN"},
    {"state_name": "Maharashtra", "state_code": "MH", "country_code": "IN"},
    {"state_name": "Tamil Nadu", "state_code": "TN", "country_code": "IN"},
    {"state_name": "California", "state_code": "CA", "country_code": "US"},
    {"state_name": "Texas", "state_code": "TX", "country_code": "US"},
    {"state_name": "New York", "state_code": "NY", "country_code": "US"},
    {"state_name": "Ontario", "state_code": "ON", "country_code": "CA"},
    {"state_name": "Quebec", "state_code": "QC", "country_code": "CA"},
    {"state_name": "New South Wales", "state_code": "NSW", "country_code": "AU"},
    {"state_name": "Victoria", "state_code": "VIC", "country_code": "AU"},

    {"state_name": "Andhra Pradesh", "state_code": "AP", "country_code": "IN"},
    {"state_name": "Arunachal Pradesh", "state_code": "AR", "country_code": "IN"},
    {"state_name": "Assam", "state_code": "AS", "country_code": "IN"},
    {"state_name": "Bihar", "state_code": "BR", "country_code": "IN"},
    {"state_name": "Chhattisgarh", "state_code": "CT", "country_code": "IN"},
    {"state_name": "Goa", "state_code": "GA", "country_code": "IN"},
    {"state_name": "Gujarat", "state_code": "GJ", "country_code": "IN"},
    {"state_name": "Haryana", "state_code": "HR", "country_code": "IN"},
    {"state_name": "Himachal Pradesh", "state_code": "HP", "country_code": "IN"},
    {"state_name": "Jharkhand", "state_code": "JH", "country_code": "IN"},
    {"state_name": "Kerala", "state_code": "KL", "country_code": "IN"},
    {"state_name": "Madhya Pradesh", "state_code": "MP", "country_code": "IN"},
    {"state_name": "Manipur", "state_code": "MN", "country_code": "IN"},
    {"state_name": "Meghalaya", "state_code": "ML", "country_code": "IN"},
    {"state_name": "Mizoram", "state_code": "MZ", "country_code": "IN"},
    {"state_name": "Nagaland", "state_code": "NL", "country_code": "IN"},
    {"state_name": "Odisha", "state_code": "OR", "country_code": "IN"},
    {"state_name": "Punjab", "state_code": "PB", "country_code": "IN"},
    {"state_name": "Rajasthan", "state_code": "RJ", "country_code": "IN"},
    {"state_name": "Sikkim", "state_code": "SK", "country_code": "IN"},
    {"state_name": "Telangana", "state_code": "TG", "country_code": "IN"},
    {"state_name": "Tripura", "state_code": "TR", "country_code": "IN"},
    {"state_name": "Uttar Pradesh", "state_code": "UP", "country_code": "IN"},
    {"state_name": "Uttarakhand", "state_code": "UT", "country_code": "IN"},
    {"state_name": "West Bengal", "state_code": "WB", "country_code": "IN"},

    {"state_name": "Andaman and Nicobar Islands", "state_code": "AN", "country_code": "IN"},
    {"state_name": "Chandigarh", "state_code": "CH", "country_code": "IN"},
    {"state_name": "Dadra and Nagar Haveli and Daman and Diu", "state_code": "DH", "country_code": "IN"},
    {"state_name": "Delhi", "state_code": "DL", "country_code": "IN"},
    {"state_name": "Jammu and Kashmir", "state_code": "JK", "country_code": "IN"},
    {"state_name": "Ladakh", "state_code": "LA", "country_code": "IN"},
    {"state_name": "Lakshadweep", "state_code": "LD", "country_code": "IN"},
    {"state_name": "Puducherry", "state_code": "PY", "country_code": "IN"}

]

# Region data
regions_data = [
    {"region_name": "Bangalore Urban", "region_code": "BLR", "state_code": "KA", "region_description": "Bangalore Urban District"},
    {"region_name": "Mysore", "region_code": "MYS", "state_code": "KA", "region_description": "Mysore District"},
    {"region_name": "Mumbai", "region_code": "MUM", "state_code": "MH", "region_description": "Mumbai Metropolitan Region"},
    {"region_name": "Pune", "region_code": "PUN", "state_code": "MH", "region_description": "Pune District"},
    {"region_name": "Chennai", "region_code": "CHN", "state_code": "TN", "region_description": "Chennai Metropolitan Area"},
    {"region_name": "Los Angeles", "region_code": "LA", "state_code": "CA", "region_description": "Los Angeles County"},
    {"region_name": "San Francisco", "region_code": "SF", "state_code": "CA", "region_description": "San Francisco Bay Area"},
    {"region_name": "Houston", "region_code": "HOU", "state_code": "TX", "region_description": "Houston Metropolitan Area"},
    {"region_name": "Manhattan", "region_code": "MAN", "state_code": "NY", "region_description": "Manhattan Borough"},
    {"region_name": "Toronto", "region_code": "TOR", "state_code": "ON", "region_description": "Greater Toronto Area"},
    {"region_name": "Montreal", "region_code": "MTL", "state_code": "QC", "region_description": "Montreal Metropolitan Area"},
    {"region_name": "Sydney", "region_code": "SYD", "state_code": "NSW", "region_description": "Sydney Metropolitan Area"},
    {"region_name": "Melbourne", "region_code": "MEL", "state_code": "VIC", "region_description": "Melbourne Metropolitan Area"},
]

def populate_countries():
    """Populate Country table"""
    print("Populating Countries...")
    for data in countries_data:
        country, created = Country.objects.update_or_create(
            country_code=data["country_code"],
            defaults={
                "country_name": data["country_name"],
                "country_slug": slugify(data["country_name"]),
                "continent": data["continent"],
                "country_description": data["country_description"],
            }
        )
        status = "Created" if created else "Updated"
        print(f"  {status}: {country.country_name}")
    print(f"✅ {len(countries_data)} countries processed\n")

def populate_states():
    """Populate State table"""
    print("Populating States...")
    for data in states_data:
        try:
            country = Country.objects.get(country_code=data["country_code"])
            state, created = State.objects.update_or_create(
                state_code=data["state_code"],
                defaults={
                    "state_name": data["state_name"],
                    "country": country,
                }
            )
            status = "Created" if created else "Updated"
            print(f"  {status}: {state.state_name} ({country.country_name})")
        except Country.DoesNotExist:
            print(f"  ⚠️  Country with code '{data['country_code']}' not found for state '{data['state_name']}'")
    print(f"✅ {len(states_data)} states processed\n")

def populate_regions():
    """Populate Region table"""
    print("Populating Regions...")
    for data in regions_data:
        try:
            state = State.objects.get(state_code=data["state_code"])
            region, created = Region.objects.update_or_create(
                region_code=data["region_code"],
                defaults={
                    "region_name": data["region_name"],
                    "region_slug": slugify(data["region_name"]),
                    "region_description": data["region_description"],
                    "state": state,
                }
            )
            status = "Created" if created else "Updated"
            print(f"  {status}: {region.region_name} ({state.state_name})")
        except State.DoesNotExist:
            print(f"  ⚠️  State with code '{data['state_code']}' not found for region '{data['region_name']}'")
    print(f"✅ {len(regions_data)} regions processed\n")

if __name__ == "__main__":
    print("=" * 60)
    print("Starting Location Data Population")
    print("=" * 60 + "\n")

    populate_countries()
    populate_states()
    populate_regions()

    print("=" * 60)
    print("✅ All location data populated successfully!")
    print("=" * 60)
