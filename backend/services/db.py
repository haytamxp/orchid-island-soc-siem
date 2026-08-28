"""
db.py — MySQL connection and query helpers.
"""
import mysql.connector
from mysql.connector import Error

from backend.config import Config


def get_connection():
    """Return a new MySQL connection."""
    return mysql.connector.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        database=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        charset="utf8mb4",
        collation="utf8mb4_unicode_ci"
    )


def query_all(sql: str, params: tuple = ()) -> list[dict]:
    """Execute a SELECT and return a list of dicts."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        return cursor.fetchall()
    finally:
        conn.close()


def query_one(sql: str, params: tuple = ()) -> dict | None:
    """Execute a SELECT and return a single dict."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        return cursor.fetchone()
    finally:
        conn.close()


def execute(sql: str, params: tuple = ()) -> int:
    """Execute an INSERT/UPDATE/DELETE and return lastrowid or rowcount."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.lastrowid or cursor.rowcount
    finally:
        conn.close()


def test_connection() -> bool:
    """Test the database connection."""
    try:
        conn = get_connection()
        conn.close()
        return True
    except Error as e:
        print(f"[DB] Connection error: {e}")
        return False