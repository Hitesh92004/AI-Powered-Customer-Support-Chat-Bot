import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.config import settings

import asyncpg

async def main():
    db_url = settings.DATABASE_URL
    if not db_url:
        print("DATABASE_URL not found")
        return

    pool = await asyncpg.create_pool(
        dsn=db_url,
        min_size=1,
        max_size=2,
    )
    
    # We don't have a specific user_id, let's insert NULL if user_id is nullable, or we can fetch a valid user_id or insert a dummy user.
    # Check if we can fetch a user
    async with pool.acquire() as conn:
        try:
            # First, delete existing ones if any to avoid unique constraint issues
            await conn.execute("DELETE FROM orders WHERE order_id IN ('ORD-5001', 'ORD-5002', 'ORD-5003')")
            
            # Let's see if orders has a nullable user_id. We'll just try inserting a UUID that's fake or fetching an existing one
            user = await conn.fetchrow("SELECT id FROM users LIMIT 1")
            user_id = user['id'] if user else None
            
            # If user_id is not nullable and we have no users, we might get an error.
            # Assuming there's a demo user or it can be nullable
            query = """
            INSERT INTO orders (user_id, order_id, status, expected_delivery) 
            VALUES 
            ($1, 'ORD-5001', 'processing', CURRENT_DATE + INTERVAL '5 days'),
            ($1, 'ORD-5002', 'shipped', CURRENT_DATE + INTERVAL '2 days'),
            ($1, 'ORD-5003', 'delivered', CURRENT_DATE - INTERVAL '1 day')
            """
            
            await conn.execute(query, user_id)
            print("Successfully inserted demo orders ORD-5001, ORD-5002, ORD-5003.")
            
        except Exception as e:
            print(f"Error inserting orders: {e}")
            
    await pool.close()

if __name__ == "__main__":
    asyncio.run(main())
