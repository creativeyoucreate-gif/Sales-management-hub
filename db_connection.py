# ============================================================
#  db_connection.py
#  Sets up the MySQL connection.
#  Beginners: Run this file first to make sure your DB works!
# ============================================================

import mysql.connector  # pip install mysql-connector-python

# --- CHANGE THESE to match your MySQL setup ---
DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",       # your MySQL username
    "password": "KAvi",  # your MySQL password
    "database": "sales_management_system_pro1"
}

def get_connection():
    """
    Creates and returns a MySQL database connection.
    Call this function whenever you need to talk to the database.
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as e:
        print(f"❌ Connection failed: {e}")
        return None


def run_query(query, params=None, fetch=True):
    """
    A helper function to run any SQL query.

    Parameters:
        query  (str)  : The SQL query string
        params (tuple): Values to safely insert into the query (prevents SQL injection)
        fetch  (bool) : True = SELECT (returns rows), False = INSERT/UPDATE/DELETE

    Returns:
        list of rows (for SELECT) or None (for INSERT/UPDATE/DELETE)
    """
    conn = get_connection()
    if not conn:
        return None

    cursor = conn.cursor(dictionary=True)  # dictionary=True → rows as dicts

    try:
        cursor.execute(query, params)

        if fetch:
            return cursor.fetchall()   # Returns list of row dictionaries
        else:
            conn.commit()              # Save changes to DB
            return cursor.lastrowid    # Returns the new row's ID (useful after INSERT)

    except mysql.connector.Error as e:
        print(f"❌ Query failed: {e}")
        conn.rollback()
        return None

    finally:
        cursor.close()
        conn.close()


# ============================================================
#  Quick test — run this file directly to verify connection
# ============================================================
if __name__ == "__main__":
    conn = get_connection()
    if conn:
        print("✅ Connected to MySQL successfully!")
        conn.close()
    else:
        print("❌ Could not connect. Check DB_CONFIG settings above.")
