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
            print("Dropping foreign keys...")
            # Ignore errors if constrained doesn't exist
            tables_fks = [
                ('conversations', 'conversations_user_id_fkey'),
                ('documents', 'documents_user_id_fkey'),
                ('faq_entries', 'faq_entries_user_id_fkey'),
                ('handoff_tickets', 'handoff_tickets_user_id_fkey'),
                ('tickets', 'tickets_user_id_fkey'),
                ('orders', 'orders_user_id_fkey')
            ]
            for table, fk in tables_fks:
                try:
                    await conn.execute(f"ALTER TABLE {table} DROP CONSTRAINT {fk}")
                    print(f"Dropped {fk}")
                except Exception as e:
                    print(f"Could not drop constraint {fk} (might not exist): {e}")
            
            print("Dropping users table...")
            try:
                await conn.execute("DROP TABLE users")
                print("Table 'users' dropped successfully.")
            except Exception as e:
                print(f"Could not drop users table (might not exist): {e}")

        except Exception as e:
            print(f"Critical Error: {e}")
            
    await pool.close()

if __name__ == "__main__":
    asyncio.run(main())
