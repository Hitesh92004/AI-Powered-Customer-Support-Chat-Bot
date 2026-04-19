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
            # Get table names
            tables = await conn.fetch("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
            print("Tables:")
            for row in tables:
                print(f" - {row['table_name']}")
                
            # Check foreign keys pointing to users
            fks = await conn.fetch("""
                SELECT
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM
                    information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                      ON tc.constraint_name = kcu.constraint_name
                      AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name
                      AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY' AND ccu.table_name = 'users';
            """)
            print("\nForeign Keys to users:")
            for row in fks:
                print(f" - {row['table_name']}.{row['column_name']} -> {row['foreign_table_name']}.{row['foreign_column_name']}")
                
        except Exception as e:
            print(f"Error: {e}")
            
    await pool.close()

if __name__ == "__main__":
    asyncio.run(main())
