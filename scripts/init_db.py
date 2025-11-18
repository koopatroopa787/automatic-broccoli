"""
Database Initialization Script

Creates all database tables and initial schema.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.api.database import init_db


async def main():
    """Initialize database."""
    print("=" * 60)
    print("Database Initialization")
    print("=" * 60)
    print("\nCreating database tables...")

    try:
        await init_db()
        print("✓ Database initialized successfully!")
        print("\nNext steps:")
        print("1. Create a user via API: POST /api/v1/auth/register")
        print("2. Load sample data: python scripts/load_sample_data.py")
        print("3. Explore the API at: http://localhost:8000/docs")
        print("=" * 60)
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
