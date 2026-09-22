# ============================================================
#  db_connection.py
#  This file handles talking to the PostgreSQL database.
#  Every other file imports run_query() from here.
#
#  Install what you need first:
#      pip install psycopg2-binary
#
#  Run this file by itself first to check your connection works:
#      python db_connection.py
# ============================================================

import psycopg2
from psycopg2.extras import RealDictCursor


# --- CHANGE THESE to match your own PostgreSQL setup ---
DB_HOST = "localhost"
DB_PORT = 5432
DB_USER = "postgres"
DB_PASSWORD = "KAvi"
DB_NAME = "Project1"


def get_connection():
    """
    Opens a brand new connection to the database and returns it.
    """
    connection = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME
    )
    return connection


def run_query(query, params=None, fetch=True):
    """
    Runs one SQL query and takes care of opening/closing the connection
    so the rest of the code never has to worry about that.

    query  : the SQL text, e.g. "SELECT * FROM branches WHERE branch_id = %s"
    params : a tuple of values to safely fill in for any %s in the query,
             e.g. (5,) — always use %s + params instead of pasting values
             straight into the query string, so the database library can
             protect you from SQL injection.
    fetch  : tells this function what kind of query it is
        fetch=True   -> a SELECT query. Fetches and returns every row.
        fetch="one"  -> an INSERT ... RETURNING query. Fetches one row.
        fetch=False  -> an INSERT/UPDATE/DELETE with nothing to return.

    Returns:
        - a list of rows, when fetch=True
        - a single row (or None), when fetch="one"
        - True (or None on failure), when fetch=False
    """
    connection = None
    cursor = None

    try:
        connection = get_connection()

        # RealDictCursor lets us read each row like a dictionary,
        # e.g. row["branch_name"] instead of row[0]
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, params)

        if fetch == True:
            rows = cursor.fetchall()
            connection.commit()
            return rows

        elif fetch == "one":
            row = cursor.fetchone()
            connection.commit()
            return row

        else:
            connection.commit()
            print("Query ran successfully!")
            return True

    except Exception as error:
        print("Something went wrong:", error)
        if connection:
            connection.rollback()
        return None

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# ============================================================
#  Quick test — run this file directly to check the connection
# ============================================================
if __name__ == "__main__":
    try:
        connection = get_connection()
        print("Connected to PostgreSQL successfully!")
        connection.close()
    except Exception as error:
        print("Could not connect. Check the DB_ settings above.")
        print("Error was:", error)
