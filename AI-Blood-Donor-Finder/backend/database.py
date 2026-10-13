"""
Database Connection and Query Management
----------------------------------------
Supports MySQL (via PyMySQL) for production/XAMPP local environments.
Includes automated database initialization and an intelligent local
SQLite fallback to guarantee zero downtime if XAMPP MySQL has not
yet been started on the developer's workstation.
"""

import os
import sqlite3
import pymysql
import pymysql.cursors
from contextlib import contextmanager
from typing import Any, List, Dict, Optional
from .config import Config

_USE_SQLITE = False
_SQLITE_PATH = Config.BASE_DIR / 'instance' / 'blood_donor_finder.db'


def is_mysql_available() -> bool:
    """Tests if MySQL server is reachable with configured credentials."""
    try:
        conn = pymysql.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            connect_timeout=3
        )
        conn.close()
        return True
    except Exception:
        return False


def get_mysql_connection(use_database: bool = True):
    """Creates a raw PyMySQL connection."""
    db_name = Config.DB_NAME if use_database else None
    return pymysql.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=db_name,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
        charset='utf8mb4'
    )


def get_sqlite_connection():
    """Creates a connection to SQLite database."""
    _SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_SQLITE_PATH), timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db():
    """
    Context manager yielding an active database connection and cursor.
    Uses MySQL when online, or seamless local SQLite fallback.
    """
    global _USE_SQLITE
    if not _USE_SQLITE:
        try:
            conn = get_mysql_connection(use_database=True)
            cursor = conn.cursor()
            try:
                yield conn, cursor
            finally:
                cursor.close()
                conn.close()
            return
        except Exception:
            # Fall back to SQLite if MySQL is offline
            _USE_SQLITE = True

    # SQLite execution mode
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    try:
        yield conn, cursor
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def normalize_query(query: str, is_sqlite: bool) -> str:
    """Normalizes SQL syntax between MySQL and SQLite."""
    if is_sqlite:
        # SQLite uses '?' parameter placeholders instead of '%s'
        q = query.replace('%s', '?')
        # Remove MySQL-specific engine/charset clauses if present
        q = q.replace('ENGINE=InnoDB', '').replace('DEFAULT CHARSET=utf8mb4', '')
        return q
    return query


def execute_query(query: str, params: Optional[Any] = None) -> int:
    """
    Executes an INSERT, UPDATE, or DELETE query.
    Returns the last inserted id or affected rows count.
    """
    global _USE_SQLITE
    with get_db() as (conn, cursor):
        normalized_q = normalize_query(query, _USE_SQLITE)
        if params is not None:
            if isinstance(params, list) and not isinstance(params, tuple):
                params = tuple(params)
            cursor.execute(normalized_q, params)
        else:
            cursor.execute(normalized_q)

        if _USE_SQLITE:
            return cursor.lastrowid
        else:
            return cursor.lastrowid or cursor.rowcount


def fetch_one(query: str, params: Optional[Any] = None) -> Optional[Dict[str, Any]]:
    """Fetches a single record as a dictionary."""
    global _USE_SQLITE
    with get_db() as (conn, cursor):
        normalized_q = normalize_query(query, _USE_SQLITE)
        if params is not None:
            if isinstance(params, list) and not isinstance(params, tuple):
                params = tuple(params)
            cursor.execute(normalized_q, params)
        else:
            cursor.execute(normalized_q)

        row = cursor.fetchone()
        if not row:
            return None
        if _USE_SQLITE:
            return dict(row)
        return dict(row)


def fetch_all(query: str, params: Optional[Any] = None) -> List[Dict[str, Any]]:
    """Fetches all matching records as a list of dictionaries."""
    global _USE_SQLITE
    with get_db() as (conn, cursor):
        normalized_q = normalize_query(query, _USE_SQLITE)
        if params is not None:
            if isinstance(params, list) and not isinstance(params, tuple):
                params = tuple(params)
            cursor.execute(normalized_q, params)
        else:
            cursor.execute(normalized_q)

        rows = cursor.fetchall()
        if not rows:
            return []
        if _USE_SQLITE:
            return [dict(r) for r in rows]
        return [dict(r) for r in rows]


def get_current_db_type() -> str:
    """Returns whether MySQL or SQLite is currently active."""
    global _USE_SQLITE
    return "SQLite (Local Dev Mode)" if _USE_SQLITE else "MySQL (Production / XAMPP)"
