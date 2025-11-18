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
    {"customer_id": "CUST001", "customer_name": "John Smith", "email": "john.smith@email.com",
     "phone": "555-0101", "segment": "Premium", "city": "New York", "state": "NY", "postal_code": "10001"},
    {"customer_id": "CUST002", "customer_name": "Emma Johnson", "email": "emma.j@email.com",
     "phone": "555-0102", "segment": "Standard", "city": "Los Angeles", "state": "CA", "postal_code": "90001"},
    {"customer_id": "CUST003", "customer_name": "Michael Brown", "email": "m.brown@email.com",
     "phone": "555-0103", "segment": "Premium", "city": "Chicago", "state": "IL", "postal_code": "60601"},
    {"customer_id": "CUST004", "customer_name": "Sarah Davis", "email": "sarah.d@email.com",
     "phone": "555-0104", "segment": "Standard", "city": "Houston", "state": "TX", "postal_code": "77001"},
    {"customer_id": "CUST005", "customer_name": "James Wilson", "email": "j.wilson@email.com",
     "phone": "555-0105", "segment": "VIP", "city": "Phoenix", "state": "AZ", "postal_code": "85001"},
    {"customer_id": "CUST006", "customer_name": "Lisa Anderson", "email": "lisa.a@email.com",
     "phone": "555-0106", "segment": "Premium", "city": "Philadelphia", "state": "PA", "postal_code": "19019"},
    {"customer_id": "CUST007", "customer_name": "David Martinez", "email": "d.martinez@email.com",
     "phone": "555-0107", "segment": "Standard", "city": "San Antonio", "state": "TX", "postal_code": "78201"},
    {"customer_id": "CUST008", "customer_name": "Jennifer Garcia", "email": "j.garcia@email.com",
     "phone": "555-0108", "segment": "VIP", "city": "San Diego", "state": "CA", "postal_code": "92101"},
    {"customer_id": "CUST009", "customer_name": "Robert Rodriguez", "email": "r.rodriguez@email.com",
     "phone": "555-0109", "segment": "Premium", "city": "Dallas", "state": "TX", "postal_code": "75201"},
    {"customer_id": "CUST010", "customer_name": "Maria Hernandez", "email": "m.hernandez@email.com",
     "phone": "555-0110", "segment": "Standard", "city": "San Jose", "state": "CA", "postal_code": "95101"},
]

PRODUCTS = [
    {"product_id": "PROD001", "name": "Laptop Pro 15", "sku": "LT-PRO-15", "category": "Electronics",
     "subcategory": "Computers", "brand": "TechCorp", "unit_price": 1299.99, "unit_cost": 850.00},
    {"product_id": "PROD002", "name": "Wireless Mouse", "sku": "MS-WRL-01", "category": "Electronics",
     "subcategory": "Accessories", "brand": "TechCorp", "unit_price": 29.99, "unit_cost": 12.00},
    {"product_id": "PROD003", "name": "Office Chair Pro", "sku": "CH-OFC-PR", "category": "Furniture",
     "subcategory": "Chairs", "brand": "ComfortPlus", "unit_price": 399.99, "unit_cost": 200.00},
    {"product_id": "PROD004", "name": "Standing Desk", "sku": "DK-STD-01", "category": "Furniture",
     "subcategory": "Desks", "brand": "ErgoWork", "unit_price": 599.99, "unit_cost": 350.00},
    {"product_id": "PROD005", "name": "USB-C Hub", "sku": "HB-USC-08", "category": "Electronics",
     "subcategory": "Accessories", "brand": "TechCorp", "unit_price": 49.99, "unit_cost": 20.00},
    {"product_id": "PROD006", "name": "Mechanical Keyboard", "sku": "KB-MCH-RGB", "category": "Electronics",
     "subcategory": "Accessories", "brand": "TypeMaster", "unit_price": 129.99, "unit_cost": 65.00},
    {"product_id": "PROD007", "name": "27\" Monitor", "sku": "MN-27-4K", "category": "Electronics",
     "subcategory": "Displays", "brand": "ViewPro", "unit_price": 349.99, "unit_cost": 180.00},
    {"product_id": "PROD008", "name": "Desk Lamp LED", "sku": "LP-LED-DSK", "category": "Furniture",
     "subcategory": "Lighting", "brand": "BrightLife", "unit_price": 59.99, "unit_cost": 25.00},
    {"product_id": "PROD009", "name": "Webcam HD", "sku": "WC-HD-PRO", "category": "Electronics",
     "subcategory": "Accessories", "brand": "TechCorp", "unit_price": 89.99, "unit_cost": 45.00},
    {"product_id": "PROD010", "name": "Headphones Pro", "sku": "HP-PRO-NC", "category": "Electronics",
     "subcategory": "Audio", "brand": "SoundWave", "unit_price": 199.99, "unit_cost": 100.00},
]

LOCATIONS = [
    {"location_id": "LOC001", "store_name": "NYC Flagship", "store_type": "Physical", "city": "New York",
     "state": "NY", "postal_code": "10001", "country": "USA", "region": "Northeast"},
    {"location_id": "LOC002", "store_name": "LA Downtown", "store_type": "Physical", "city": "Los Angeles",
     "state": "CA", "postal_code": "90001", "country": "USA", "region": "West"},
    {"location_id": "LOC003", "store_name": "Chicago Central", "store_type": "Physical", "city": "Chicago",
     "state": "IL", "postal_code": "60601", "country": "USA", "region": "Midwest"},
    {"location_id": "LOC004", "store_name": "Houston Hub", "store_type": "Physical", "city": "Houston",
     "state": "TX", "postal_code": "77001", "country": "USA", "region": "South"},
    {"location_id": "LOC005", "store_name": "Online Store", "store_type": "Online", "city": "Seattle",
     "state": "WA", "postal_code": "98101", "country": "USA", "region": "West"},
]


async def load_date_dimension(session: AsyncSession, start_date: datetime, days: int = 365):
    """Load date dimension with calendar attributes."""
    print(f"Loading {days} days into date dimension...")

    month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    dates = []
    for i in range(days):
        date = start_date + timedelta(days=i)
        dim_date = DimDate(
            date_id=int(date.strftime("%Y%m%d")),
            full_date=date,
            day=date.day,
            month=date.month,
            year=date.year,
            quarter=(date.month - 1) // 3 + 1,
            day_of_week=date.weekday(),
            day_name=day_names[date.weekday()],
            month_name=month_names[date.month - 1],
            week_of_year=date.isocalendar()[1],
            is_weekend=(date.weekday() >= 5),
            is_holiday=False,  # Simplified
            fiscal_year=date.year if date.month >= 4 else date.year - 1,
            fiscal_quarter=((date.month - 4) % 12) // 3 + 1
        )
        dates.append(dim_date)

    session.add_all(dates)
    await session.commit()
    print(f"✓ Loaded {len(dates)} date records")


async def load_customers(session: AsyncSession):
    """Load customer dimension."""
    print("Loading customers...")

    tier_map = {"VIP": "High", "Premium": "Medium", "Standard": "Low"}

    customers = []
    for cust_data in CUSTOMERS:
        customer = DimCustomer(
            customer_id=cust_data["customer_id"],
            customer_name=cust_data["customer_name"],
            email=cust_data["email"],
            phone=cust_data["phone"],
            customer_segment=cust_data["segment"],
            lifetime_value_tier=tier_map[cust_data["segment"]],
            city=cust_data["city"],
            state=cust_data["state"],
            postal_code=cust_data["postal_code"],
            country="USA",
            effective_date=datetime.utcnow(),
            is_current=True,
            version=1
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
            product_id=prod_data["product_id"],
            product_name=prod_data["name"],
            sku=prod_data["sku"],
            category=prod_data["category"],
            subcategory=prod_data["subcategory"],
            brand=prod_data["brand"],
            supplier=f"{prod_data['brand']} Manufacturing",
            unit_price=prod_data["unit_price"],
            unit_cost=prod_data["unit_cost"],
            description=f"High-quality {prod_data['name']}",
            is_active=True
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
            location_id=loc_data["location_id"],
            store_name=loc_data["store_name"],
            store_type=loc_data["store_type"],
            city=loc_data["city"],
            state=loc_data["state"],
            postal_code=loc_data["postal_code"],
            country=loc_data["country"],
            region=loc_data["region"],
            latitude=None,  # Could add real coordinates
            longitude=None,
            opened_date=datetime.utcnow() - timedelta(days=365),
            is_active=True
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

            # Add some price variation (discounts)
            discount_pct = 0
            if random.random() < 0.15:  # 15% chance of discount
                discount_pct = random.uniform(0.05, 0.20)

            discount_amount = round(quantity * unit_price * discount_pct, 2)
            subtotal = round(quantity * unit_price - discount_amount, 2)
            tax_amount = round(subtotal * 0.08, 2)  # 8% tax
            total_amount = round(subtotal + tax_amount, 2)
            cost_amount = round(quantity * product["unit_cost"], 2)
            profit_amount = round(total_amount - cost_amount, 2)

            sale = FactSales(
                transaction_id=f"TXN{transaction_id:06d}",
                date_key=date_key,
                customer_key=customer_key,
                product_key=product_key,
                location_key=location_key,
                quantity=quantity,
                unit_price=unit_price,
                discount_amount=discount_amount,
                tax_amount=tax_amount,
                total_amount=total_amount,
                cost_amount=cost_amount,
                profit_amount=profit_amount
            )
            sales.append(sale)
            transaction_id += 1

    session.add_all(sales)
    await session.commit()
    print(f"✓ Loaded {len(sales)} sales transactions")
    print(f"   Total revenue: ${sum(s.total_amount for s in sales):,.2f}")
    print(f"   Total profit: ${sum(s.profit_amount for s in sales):,.2f}")


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
