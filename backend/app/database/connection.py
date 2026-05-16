import pg8000.dbapi
from typing import Any, Optional, Sequence
from app.config.settings import settings


# Opens a PostgreSQL connection using values from the environment settings.
def get_db_connection():
    try:
        conn = pg8000.dbapi.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            database=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise


# Converts pg8000 tuple rows into dictionaries for API-friendly responses.
def row_to_dict(row: tuple, columns: Sequence) -> dict:
    return dict(zip([col[0] for col in columns], row))


# Runs parameterized SQL queries and returns rows or affected row counts.
def execute_query(
    query: str, 
    params: Optional[tuple] = None, 
    fetch_one: bool = False, 
    fetch_all: bool = False
) -> Any:
    if fetch_one and fetch_all:
        raise ValueError("fetch_one and fetch_all cannot both be True")

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(query, params or ())
        
        columns = cursor.description or []
        rows = []
        if columns:
            rows = cursor.fetchall()
            if query.lstrip().lower().startswith(("insert", "update", "delete")):
                conn.commit()
        else:
            conn.commit()

        if fetch_one:
            if rows:
                return row_to_dict(rows[0], columns) if columns else rows[0]
            return None
        elif fetch_all:
            return [row_to_dict(row, columns) for row in rows] if columns else rows
        else:
            return cursor.rowcount
    
    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        print(f"Query error: {e}")
        raise
    
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            try:
                conn.close()
            except Exception:
                pass
