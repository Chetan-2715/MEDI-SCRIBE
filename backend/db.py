import os
import psycopg2
import psycopg2.extras
from psycopg2 import pool
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

# Initialize a connection pool
try:
    db_pool = pool.SimpleConnectionPool(1, 20, DATABASE_URL)
except Exception as e:
    print(f"Error creating connection pool: {e}")
    db_pool = None

def get_db_connection():
    """Get a database connection from the pool."""
    if db_pool:
        conn = db_pool.getconn()
        conn.autocommit = False
        return conn
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    return conn

def release_db_connection(conn, rollback=False):
    """Return the connection to the pool or close it."""
    if rollback:
        try:
            conn.rollback()
        except:
            pass
    if db_pool:
        db_pool.putconn(conn)
    else:
        conn.close()

def query(sql, params=None, fetch_one=False):
    """Execute a SELECT query and return results as list of dicts."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            if fetch_one:
                row = cur.fetchone()
                return dict(row) if row else None
            return [dict(r) for r in cur.fetchall()]
    except Exception:
        release_db_connection(conn, rollback=True)
        raise
    finally:
        # Avoid closing if it was already released due to exception
        if not conn.closed:
            release_db_connection(conn)

def execute(sql, params=None, returning=False):
    """Execute an INSERT/UPDATE/DELETE query."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            result = None
            if returning:
                result = cur.fetchone()
                if result:
                    result = dict(result)
            conn.commit()
            return result
    except Exception:
        release_db_connection(conn, rollback=True)
        raise
    finally:
        if not conn.closed:
            release_db_connection(conn)

def execute_many(sql, params_list):
    """Execute a batch INSERT."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            results = []
            for params in params_list:
                cur.execute(sql, params)
                row = cur.fetchone()
                if row:
                    results.append(dict(row))
            conn.commit()
            return results
    except Exception:
        release_db_connection(conn, rollback=True)
        raise
    finally:
        # Avoid closing if it was already released due to exception
        if not conn.closed:
            release_db_connection(conn)

# Test connection on import
try:
    conn = get_db_connection()
    conn.close()
    print("[DB] Connected to Neon PostgreSQL successfully ✅")
except Exception as e:
    print(f"[DB] WARNING: Could not connect to database: {e}")
