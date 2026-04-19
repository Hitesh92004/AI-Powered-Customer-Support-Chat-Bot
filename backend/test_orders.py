import asyncio
import sys
import os

sys.path.append(os.path.dirname(__file__))
from app.config import settings
import asyncpg

async def main():
    db_url = settings.DATABASE_URL
    if not db_url:
        print("DATABASE_URL not found")
        return

    pool = await asyncpg.create_pool(dsn=db_url)
    
    async with pool.acquire() as conn:
        try:
            res = await conn.fetch("SELECT * FROM orders")
            print(f"Orders: {res}")
            
            res2 = await conn.fetch("SELECT COUNT(*) FROM faq_entries")
            print(f"FAQs: {res2[0]['count']}")
        except Exception as e:
            print(f"Error: {e}")
            
    await pool.close()

if __name__ == "__main__":
    asyncio.run(main())
