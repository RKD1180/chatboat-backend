import os
import psycopg2
from config import settings


def get_connection():
    return psycopg2.connect(settings.DATABASE_URL)


def run_migrations():
    """Run SQL migrations on startup - creates tables if missing, fixes issues."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        print("Checking database...")
        
        # Step 1: Drop problematic tables/triggers from old setup
        try:
            cur.execute("DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users")
            cur.execute("DROP FUNCTION IF EXISTS public.handle_new_user()")
            cur.execute("DROP TABLE IF EXISTS user_profiles CASCADE")
            cur.execute("DROP TABLE IF EXISTS profiles CASCADE")
            conn.commit()
        except Exception:
            conn.rollback()
        
        # Step 2: Check if users table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'users'
            )
        """)
        users_exists = cur.fetchone()[0]
        
        if not users_exists:
            # Tables don't exist - create all from scratch
            print("Creating database tables...")
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            sql_file = os.path.join(base_dir, "sql", "000_init.sql")
            with open(sql_file, "r") as f:
                sql = f.read()
            cur.execute(sql)
            conn.commit()
            print("All tables created successfully!")
        else:
            print("Database tables already exist, checking for updates...")
            
            # Fix users table UUID default if missing
            cur.execute("""
                SELECT column_default FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'id'
            """)
            row = cur.fetchone()
            if row and not row[0]:
                print("Fixing users table UUID default...")
                cur.execute("ALTER TABLE users ALTER COLUMN id SET DEFAULT uuid_generate_v4()")
                conn.commit()
            
            # Check and add embeddings column if missing
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'training_data' 
                    AND column_name = 'embeddings'
                )
            """)
            has_embeddings = cur.fetchone()[0]
            
            if not has_embeddings:
                print("Adding embeddings column...")
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
                cur.execute("ALTER TABLE training_data ADD COLUMN embeddings vector(768)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_training_data_embeddings ON training_data USING hnsw (embeddings vector_cosine_ops)")
                conn.commit()
                print("Embeddings column added!")
            
            print("Database is up to date.")
        
        cur.close()
    except Exception as e:
        print(f"Migration error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
