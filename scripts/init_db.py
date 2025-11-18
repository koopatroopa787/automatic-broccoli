"""
Database Initialization Script

Creates all database tables and seeds initial data.
"""

import asyncio
from api.database import init_db


async def main():
    """Initialize database."""
    print("Initializing database...")
    await init_db()
    print("Database initialized successfully!")


if __name__ == "__main__":
    asyncio.run(main())
