
import pymysql
import sys
from config import DB_CONFIG
from contextlib import contextmanager


@contextmanager
def get_db_connection():
    """Provides a database connection using a context manager."""
    connection = None
    try:
        connection = pymysql.connect(**DB_CONFIG)
        yield connection
    except pymysql.Error as e:
        print(f"Database connection error: {e}", file=sys.stderr)
        # Consider more specific error handling or logging
        yield None  
    finally:
        if connection:
            connection.close()


def execute_query(query, params=None, fetch_one=False, fetch_all=False, commit=False):
    """Executes a given SQL query."""
    result = None
    with get_db_connection() as connection:
        if connection is None:
            print("Failed to establish database connection.", file=sys.stderr)
            return None  # Indicate failure

        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                if commit:
                    connection.commit()
                    result = cursor.lastrowid  # Return ID for INSERTs
                elif fetch_one:
                    result = cursor.fetchone()
                elif fetch_all:
                    result = cursor.fetchall()
                # If not commit, fetch_one, or fetch_all, it's likely a DDL or similar query
        except pymysql.Error as e:
            print(f"Database query error: {e}", file=sys.stderr)
            if commit:  # Rollback if commit fails
                try:
                    connection.rollback()
                except pymysql.Error as rb_e:
                    print(f"Rollback failed: {rb_e}", file=sys.stderr)
            return None
    return result


def test_connection():
    """Tests the database connection."""
    print("Testing database connection...")
    with get_db_connection() as connection:
        if connection:
            print("Database connection successful.")
            return True
        else:
            print("Database connection failed.")
            return False


if __name__ == "__main__":
    
    if test_connection():
        pass
