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
            # Check user_id column type in conversations
            res = await conn.fetch("SELECT data_type FROM information_schema.columns WHERE table_name = 'conversations' AND column_name = 'user_id'")
            print(f"user_id data_type in conversations: {res[0]['data_type'] if res else 'Not Found'}")
            
            # If it's UUID, we should ALTER it to VARCHAR
            # Actually let's just alter it for all relevant tables
            tables = [
                'conversations', 'documents', 'faq_entries', 
                'handoff_tickets', 'tickets', 'orders'
            ]
            print("Altering user_id to VARCHAR(255) for all tables...")
            for table in tables:
                try:
                    await conn.execute(f"ALTER TABLE {table} ALTER COLUMN user_id TYPE VARCHAR(255);")
                    print(f"Successfully altered {table}")
                except Exception as e:
                    print(f"Failed to alter {table}: {e}")

        except Exception as e:
            print(f"Error: {e}")
            
    await pool.close()

if __name__ == "__main__":
    asyncio.run(main())
