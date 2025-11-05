"""
SQLite database operations for MST company data
"""
import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

from models import CompanyStatus


# Database file path
DB_DIR = Path("/app/data")
DB_FILE = DB_DIR / "mst_database.db"


@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(str(DB_FILE), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Initialize the database and create tables if they don't exist"""
    # Ensure data directory exists
    DB_DIR.mkdir(parents=True, exist_ok=True)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mst TEXT UNIQUE NOT NULL,
                company_name TEXT NOT NULL,
                legal_name TEXT NOT NULL,
                registration_date TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        # Create index on MST for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_mst ON companies(mst)
        """)

        conn.commit()


def get_company_by_mst(mst: str) -> Optional[dict]:
    """
    Retrieve company information by MST

    Args:
        mst: Mã số thuế (Tax ID)

    Returns:
        Dictionary with company information or None if not found
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT mst, company_name, legal_name, registration_date, status
            FROM companies
            WHERE mst = ?
        """, (mst,))

        row = cursor.fetchone()
        if row:
            return {
                "mst": row["mst"],
                "company_name": row["company_name"],
                "legal_name": row["legal_name"],
                "registration_date": row["registration_date"],
                "status": row["status"]
            }
        return None


def save_company(
    mst: str,
    company_name: str,
    legal_name: str,
    registration_date: date,
    status: CompanyStatus
) -> bool:
    """
    Save company information to database

    Args:
        mst: Mã số thuế (Tax ID)
        company_name: Company name
        legal_name: Legal company name
        registration_date: Registration date
        status: Company status

    Returns:
        True if saved successfully, False otherwise
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO companies (mst, company_name, legal_name, registration_date, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                mst,
                company_name,
                legal_name,
                registration_date.isoformat(),
                status.value,
                datetime.now().isoformat()
            ))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        # MST already exists
        return False


def get_stats() -> dict:
    """Get database statistics"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM companies")
        total = cursor.fetchone()["total"]

        cursor.execute("SELECT status, COUNT(*) as count FROM companies GROUP BY status")
        status_counts = {row["status"]: row["count"] for row in cursor.fetchall()}

        return {
            "total_companies": total,
            "by_status": status_counts
        }
