"""
SQLite database connection and management utilities.
Handles database initialization, connection management, and cleanup.
"""

import sqlite3
import os
from typing import Optional
from pathlib import Path

from config.settings import get_database_config


def initialize_database() -> sqlite3.Connection:
    """
    Initialize the SQLite database connection for the customer support agent.
    
    Returns:
        sqlite3.Connection: Database connection object
        
    Raises:
        Exception: If database initialization fails
    """
    try:
        db_config = get_database_config()
        db_path = db_config.get("path", "customer_support.db")
        
        # Ensure the directory exists
        db_file = Path(db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create connection with thread safety
        connection = sqlite3.connect(
            db_path, 
            check_same_thread=False,
            timeout=30.0  # 30 second timeout
        )
        
        # Enable WAL mode for better concurrency
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=NORMAL")
        connection.execute("PRAGMA cache_size=10000")
        connection.execute("PRAGMA temp_store=memory")
        
        # Test the connection
        connection.execute("SELECT 1")
        connection.commit()
        
        print(f"Database initialized successfully at: {db_path}")
        return connection
        
    except Exception as e:
        print(f"Failed to initialize database: {e}")
        raise


def cleanup_database(connection: Optional[sqlite3.Connection]) -> None:
    """
    Clean up database resources and close connection.
    
    Args:
        connection: SQLite connection to close
    """
    if connection:
        try:
            # Commit any pending transactions
            connection.commit()
            
            # Close the connection
            connection.close()
            print("Database connection closed successfully.")
            
        except Exception as e:
            print(f"Error during database cleanup: {e}")


def get_database_info(connection: sqlite3.Connection) -> dict:
    """
    Get information about the database and its tables.
    
    Args:
        connection: SQLite database connection
        
    Returns:
        dict: Database information including tables and their row counts
    """
    try:
        cursor = connection.cursor()
        
        # Get all tables
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """)
        tables = cursor.fetchall()
        
        db_info = {
            "database_path": connection.execute("PRAGMA database_list").fetchone()[2],
            "tables": {}
        }
        
        # Get row count for each table
        for (table_name,) in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            db_info["tables"][table_name] = {
                "row_count": row_count
            }
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            db_info["tables"][table_name]["columns"] = [
                {
                    "name": col[1],
                    "type": col[2],
                    "not_null": bool(col[3]),
                    "primary_key": bool(col[5])
                }
                for col in columns
            ]
        
        return db_info
        
    except Exception as e:
        print(f"Error getting database info: {e}")
        return {"error": str(e)}


def vacuum_database(connection: sqlite3.Connection) -> bool:
    """
    Optimize the database by running VACUUM command.
    
    Args:
        connection: SQLite database connection
        
    Returns:
        bool: True if vacuum was successful, False otherwise
    """
    try:
        print("Running database vacuum (this may take a moment)...")
        connection.execute("VACUUM")
        connection.commit()
        print("Database vacuum completed successfully.")
        return True
        
    except Exception as e:
        print(f"Error during database vacuum: {e}")
        return False


def backup_database(connection: sqlite3.Connection, backup_path: str) -> bool:
    """
    Create a backup of the database.
    
    Args:
        connection: Source database connection
        backup_path: Path where backup should be saved
        
    Returns:
        bool: True if backup was successful, False otherwise
    """
    try:
        # Ensure backup directory exists
        backup_file = Path(backup_path)
        backup_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create backup connection
        backup_conn = sqlite3.connect(backup_path)
        
        # Perform backup
        connection.backup(backup_conn)
        backup_conn.close()
        
        print(f"Database backed up successfully to: {backup_path}")
        return True
        
    except Exception as e:
        print(f"Error during database backup: {e}")
        return False


def restore_database(backup_path: str, target_path: str) -> bool:
    """
    Restore database from backup.
    
    Args:
        backup_path: Path to backup file
        target_path: Path where database should be restored
        
    Returns:
        bool: True if restore was successful, False otherwise
    """
    try:
        if not os.path.exists(backup_path):
            print(f"Backup file not found: {backup_path}")
            return False
        
        # Ensure target directory exists
        target_file = Path(target_path)
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Open connections
        backup_conn = sqlite3.connect(backup_path)
        target_conn = sqlite3.connect(target_path)
        
        # Perform restore
        backup_conn.backup(target_conn)
        
        # Close connections
        backup_conn.close()
        target_conn.close()
        
        print(f"Database restored successfully to: {target_path}")
        return True
        
    except Exception as e:
        print(f"Error during database restore: {e}")
        return False


def check_database_health(connection: sqlite3.Connection) -> dict:
    """
    Check the health and integrity of the database.
    
    Args:
        connection: SQLite database connection
        
    Returns:
        dict: Health check results
    """
    health_report = {
        "connection_ok": False,
        "integrity_check": False,
        "pragma_checks": {},
        "errors": []
    }
    
    try:
        # Test basic connection
        connection.execute("SELECT 1")
        health_report["connection_ok"] = True
        
        # Run integrity check
        cursor = connection.cursor()
        cursor.execute("PRAGMA integrity_check")
        integrity_result = cursor.fetchone()[0]
        health_report["integrity_check"] = integrity_result == "ok"
        
        if integrity_result != "ok":
            health_report["errors"].append(f"Integrity check failed: {integrity_result}")
        
        # Check various PRAGMA settings
        pragma_checks = [
            "journal_mode",
            "synchronous", 
            "cache_size",
            "page_count",
            "page_size",
            "freelist_count"
        ]
        
        for pragma in pragma_checks:
            try:
                cursor.execute(f"PRAGMA {pragma}")
                result = cursor.fetchone()
                health_report["pragma_checks"][pragma] = result[0] if result else None
            except Exception as e:
                health_report["errors"].append(f"PRAGMA {pragma} failed: {e}")
        
    except Exception as e:
        health_report["errors"].append(f"Database health check failed: {e}")
    
    return health_report