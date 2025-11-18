"""
Sample Data Loading Script

Loads realistic sample data for the Enterprise Data Analytics Platform.
Includes dimension tables and fact tables for sales analytics.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from backend.api.database import async_session_maker
from backend.api.models.analytics_models import (
    DimDate, DimCustomer, DimProduct, DimLocation, FactSales
)


# Sample data
CUSTOMERS = [
    {"customer_key": 1, "customer_id": "CUST001", "first_name": "John", "last_name": "Smith",
     "email": "john.smith@email.com", "phone": "555-0101", "segment": "Premium", "city": "New York", "state": "NY"},
    {"customer_key": 2, "customer_id": "CUST002", "first_name": "Emma", "last_name": "Johnson",
     "email": "emma.j@email.com", "phone": "555-0102", "segment": "Standard", "city": "Los Angeles", "state": "CA"},
    {"customer_key": 3, "customer_id": "CUST003", "first_name": "Michael", "last_name": "Brown",
     "email": "m.brown@email.com", "phone": "555-0103", "segment": "Premium", "city": "Chicago", "state": "IL"},
    {"customer_key": 4, "customer_id": "CUST004", "first_name": "Sarah", "last_name": "Davis",
     "email": "sarah.d@email.com", "phone": "555-0104", "segment": "Standard", "city": "Houston", "state": "TX"},
    {"customer_key": 5, "customer_id": "CUST005", "first_name": "James", "last_name": "Wilson",
     "email": "j.wilson@email.com", "phone": "555-0105", "segment": "VIP", "city": "Phoenix", "state": "AZ"},
    {"customer_key": 6, "customer_id": "CUST006", "first_name": "Lisa", "last_name": "Anderson",
     "email": "lisa.a@email.com", "phone": "555-0106", "segment": "Premium", "city": "Philadelphia", "state": "PA"},
    {"customer_key": 7, "customer_id": "CUST007", "first_name": "David", "last_name": "Martinez",
     "email": "d.martinez@email.com", "phone": "555-0107", "segment": "Standard", "city": "San Antonio", "state": "TX"},
    {"customer_key": 8, "customer_id": "CUST008", "first_name": "Jennifer", "last_name": "Garcia",
     "email": "j.garcia@email.com", "phone": "555-0108", "segment": "VIP", "city": "San Diego", "state": "CA"},
    {"customer_key": 9, "customer_id": "CUST009", "first_name": "Robert", "last_name": "Rodriguez",
     "email": "r.rodriguez@email.com", "phone": "555-0109", "segment": "Premium", "city": "Dallas", "state": "TX"},
    {"customer_key": 10, "customer_id": "CUST010", "first_name": "Maria", "last_name": "Hernandez",
     "email": "m.hernandez@email.com", "phone": "555-0110", "segment": "Standard", "city": "San Jose", "state": "CA"},
]

PRODUCTS = [
    {"product_key": 1, "product_id": "PROD001", "name": "Laptop Pro 15", "category": "Electronics",
     "subcategory": "Computers", "brand": "TechCorp", "unit_price": 1299.99, "cost": 850.00},
    {"product_key": 2, "product_id": "PROD002", "name": "Wireless Mouse", "category": "Electronics",
     "subcategory": "Accessories", "brand": "TechCorp", "unit_price": 29.99, "cost": 12.00},
    {"product_key": 3, "product_id": "PROD003", "name": "Office Chair Pro", "category": "Furniture",
     "subcategory": "Chairs", "brand": "ComfortPlus", "unit_price": 399.99, "cost": 200.00},
    {"product_key": 4, "product_id": "PROD004", "name": "Standing Desk", "category": "Furniture",
     "subcategory": "Desks", "brand": "ErgoWork", "unit_price": 599.99, "cost": 350.00},
    {"product_key": 5, "product_id": "PROD005", "name": "USB-C Hub", "category": "Electronics",
     "subcategory": "Accessories", "brand": "TechCorp", "unit_price": 49.99, "cost": 20.00},
    {"product_key": 6, "product_id": "PROD006", "name": "Mechanical Keyboard", "category": "Electronics",
     "subcategory": "Accessories", "brand": "TypeMaster", "unit_price": 129.99, "cost": 65.00},
    {"product_key": 7, "product_id": "PROD007", "name": "27\" Monitor", "category": "Electronics",
     "subcategory": "Displays", "brand": "ViewPro", "unit_price": 349.99, "cost": 180.00},
    {"product_key": 8, "product_id": "PROD008", "name": "Desk Lamp LED", "category": "Furniture",
     "subcategory": "Lighting", "brand": "BrightLife", "unit_price": 59.99, "cost": 25.00},
    {"product_key": 9, "product_id": "PROD009", "name": "Webcam HD", "category": "Electronics",
     "subcategory": "Accessories", "brand": "TechCorp", "unit_price": 89.99, "cost": 45.00},
    {"product_key": 10, "product_id": "PROD010", "name": "Headphones Pro", "category": "Electronics",
     "subcategory": "Audio", "brand": "SoundWave", "unit_price": 199.99, "cost": 100.00},
]

LOCATIONS = [
    {"location_key": 1, "location_id": "LOC001", "store_name": "NYC Flagship", "city": "New York",
     "state": "NY", "country": "USA", "region": "Northeast"},
    {"location_key": 2, "location_id": "LOC002", "store_name": "LA Downtown", "city": "Los Angeles",
     "state": "CA", "country": "USA", "region": "West"},
    {"location_key": 3, "location_id": "LOC003", "store_name": "Chicago Central", "city": "Chicago",
     "state": "IL", "country": "USA", "region": "Midwest"},
    {"location_key": 4, "location_id": "LOC004", "store_name": "Houston Hub", "city": "Houston",
     "state": "TX", "country": "USA", "region": "South"},
    {"location_key": 5, "location_id": "LOC005", "store_name": "Phoenix Plaza", "city": "Phoenix",
     "state": "AZ", "country": "USA", "region": "Southwest"},
]


async def load_date_dimension(session: AsyncSession, start_date: datetime, days: int = 365):
    """Load date dimension with calendar attributes."""
    print(f"Loading {days} days into date dimension...")

    dates = []
    for i in range(days):
        date = start_date + timedelta(days=i)
        dim_date = DimDate(
            date_key=int(date.strftime("%Y%m%d")),
            date=date.date(),
            day=date.day,
            month=date.month,
            year=date.year,
            quarter=(date.month - 1) // 3 + 1,
            day_of_week=date.strftime("%A"),
            week_of_year=date.isocalendar()[1],
            is_weekend=(date.weekday() >= 5),
            is_holiday=False  # Simplified
        )
        dates.append(dim_date)

    session.add_all(dates)
    await session.commit()
    print(f"✓ Loaded {len(dates)} date records")


async def load_customers(session: AsyncSession):
    """Load customer dimension."""
    print("Loading customers...")

    customers = []
    for cust_data in CUSTOMERS:
        customer = DimCustomer(
            customer_key=cust_data["customer_key"],
            customer_id=cust_data["customer_id"],
            first_name=cust_data["first_name"],
            last_name=cust_data["last_name"],
            email=cust_data["email"],
            phone=cust_data["phone"],
            segment=cust_data["segment"],
            city=cust_data["city"],
            state=cust_data["state"],
            country="USA",
            effective_date=datetime.utcnow().date(),
            is_current=True
        )
        customers.append(customer)

    session.add_all(customers)
    await session.commit()
    print(f"✓ Loaded {len(customers)} customer records")


async def load_products(session: AsyncSession):
    """Load product dimension."""
    print("Loading products...")

    products = []
    for prod_data in PRODUCTS:
        product = DimProduct(
            product_key=prod_data["product_key"],
            product_id=prod_data["product_id"],
            name=prod_data["name"],
            category=prod_data["category"],
            subcategory=prod_data["subcategory"],
            brand=prod_data["brand"],
            unit_price=prod_data["unit_price"],
            cost=prod_data["cost"]
        )
        products.append(product)

    session.add_all(products)
    await session.commit()
    print(f"✓ Loaded {len(products)} product records")


async def load_locations(session: AsyncSession):
    """Load location dimension."""
    print("Loading locations...")

    locations = []
    for loc_data in LOCATIONS:
        location = DimLocation(
            location_key=loc_data["location_key"],
            location_id=loc_data["location_id"],
            store_name=loc_data["store_name"],
            city=loc_data["city"],
            state=loc_data["state"],
            country=loc_data["country"],
            region=loc_data["region"]
        )
        locations.append(location)

    session.add_all(locations)
    await session.commit()
    print(f"✓ Loaded {len(locations)} location records")


async def load_sales_facts(session: AsyncSession, start_date: datetime, days: int = 90):
    """Load sales fact table with transactions."""
    print(f"Generating sales transactions for {days} days...")

    sales = []
    transaction_id = 1

    # Generate 5-15 transactions per day
    for i in range(days):
        date = start_date + timedelta(days=i)
        date_key = int(date.strftime("%Y%m%d"))
        num_transactions = random.randint(5, 15)

        for _ in range(num_transactions):
            customer_key = random.randint(1, len(CUSTOMERS))
            product_key = random.randint(1, len(PRODUCTS))
            location_key = random.randint(1, len(LOCATIONS))

            product = PRODUCTS[product_key - 1]
            quantity = random.randint(1, 5)
            unit_price = product["unit_price"]

            # Add some price variation
            if random.random() < 0.1:  # 10% chance of discount
                unit_price *= random.uniform(0.8, 0.95)

            sales_amount = round(quantity * unit_price, 2)
            cost_amount = round(quantity * product["cost"], 2)
            profit_amount = round(sales_amount - cost_amount, 2)

            sale = FactSales(
                transaction_id=f"TXN{transaction_id:06d}",
                date_key=date_key,
                customer_key=customer_key,
                product_key=product_key,
                location_key=location_key,
                quantity=quantity,
                unit_price=unit_price,
                sales_amount=sales_amount,
                cost_amount=cost_amount,
                profit_amount=profit_amount
            )
            sales.append(sale)
            transaction_id += 1

    session.add_all(sales)
    await session.commit()
    print(f"✓ Loaded {len(sales)} sales transactions")


async def main():
    """Load all sample data."""
    print("=" * 60)
    print("Sample Data Loader")
    print("=" * 60)
    print("\nThis will populate the database with sample data for:")
    print("- Date dimension (1 year)")
    print("- 10 Customers")
    print("- 10 Products")
    print("- 5 Store locations")
    print("- ~900 Sales transactions (90 days)")
    print()

    try:
        async with async_session_maker() as session:
            # Load dimensions first (required for fact table foreign keys)
            start_date = datetime.utcnow() - timedelta(days=365)
            await load_date_dimension(session, start_date, days=365)
            await load_customers(session)
            await load_products(session)
            await load_locations(session)

            # Load facts
            sales_start = datetime.utcnow() - timedelta(days=90)
            await load_sales_facts(session, sales_start, days=90)

        print("\n" + "=" * 60)
        print("✓ Sample data loaded successfully!")
        print("\nNext steps:")
        print("1. Query the API: GET /api/v1/analytics/metrics/sales")
        print("2. View top products: GET /api/v1/analytics/products/top")
        print("3. Check customer segments: GET /api/v1/analytics/customers/segments")
        print("4. Open Swagger UI: http://localhost:8000/docs")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error loading sample data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
