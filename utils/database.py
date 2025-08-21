"""
PostgreSQL database connection and management utilities.
Handles database initialization, connection management, and cleanup.
"""

import os
from typing import Optional, Dict, Any
from psycopg import Connection
from psycopg.rows import dict_row
from typing import TYPE_CHECKING
from config.settings import get_database_config


if TYPE_CHECKING:
    from psycopg import Connection as PGConnection
else:
    PGConnection = Connection

def initialize_database() -> PGConnection:
    """
    Initialize the PostgreSQL database connection for the customer support agent.
    
    Returns:
        psycopg Connection object (compatible with LangGraph PostgresSaver)
    """
    try:
        db_config = get_database_config()
        db_uri = db_config.get("uri")
        
        # Use psycopg (v3) instead of psycopg2 for LangGraph compatibility
        connection = Connection.connect(
            db_uri,
            autocommit=True,
            prepare_threshold=0,
            row_factory=dict_row
        )
        
        # Test the connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
        print(f"PostgreSQL database initialized successfully at: {db_uri}")
        return connection
        
    except Exception as e:
        print(f"Failed to initialize PostgreSQL database: {e}")
        raise



def cleanup_database(connection: Optional[PGConnection]) -> None:
    """Close PostgreSQL connection."""
    if connection:
        try:
            connection.close()
            print("Database connection closed successfully.")
        except Exception as e:
            print(f"Error during database cleanup: {e}")


def get_database_info(connection: PGConnection) -> Dict[str, Any]:
    """
    Get info about tables and row counts in PostgreSQL database.
    """
    try:
        db_info = {"tables": {}}
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema='public'
            """)
            tables = cursor.fetchall()

            for (table_name,) in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]

                cursor.execute(f"""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = %s
                """, (table_name,))
                columns = cursor.fetchall()

                db_info["tables"][table_name] = {
                    "row_count": row_count,
                    "columns": [
                        {"name": c[0], "type": c[1], "not_null": c[2] == "NO"}
                        for c in columns
                    ]
                }

        return db_info

    except Exception as e:
        print(f"Error getting database info: {e}")
        return {"error": str(e)}


def vacuum_database(connection: PGConnection) -> bool:
    """Run VACUUM ANALYZE in PostgreSQL."""
    try:
        with connection.cursor() as cursor:
            print("Running VACUUM ANALYZE...")
            cursor.execute("VACUUM ANALYZE;")
        print("VACUUM ANALYZE completed successfully.")
        return True
    except Exception as e:
        print(f"Error during database vacuum: {e}")
        return False


def backup_database(backup_path: str) -> bool:
    """
    Backup PostgreSQL database using pg_dump command.
    """
    try:
        db_config = get_database_config()
        db_uri = db_config.get("uri")

        os.system(f'pg_dump "{db_uri}" > "{backup_path}"')
        print(f"Database backed up successfully to: {backup_path}")
        return True
    except Exception as e:
        print(f"Error during database backup: {e}")
        return False


def restore_database(backup_path: str) -> bool:
    """
    Restore PostgreSQL database using psql command.
    """
    try:
        db_config = get_database_config()
        db_uri = db_config.get("uri")

        os.system(f'psql "{db_uri}" < "{backup_path}"')
        print(f"Database restored successfully from: {backup_path}")
        return True
    except Exception as e:
        print(f"Error during database restore: {e}")
        return False


def check_database_health(connection: PGConnection) -> dict:
    """
    Check PostgreSQL health.
    """
    health_report = {
        "connection_ok": False,
        "errors": []
    }

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            health_report["connection_ok"] = True

            cursor.execute("SELECT version();")
            health_report["version"] = cursor.fetchone()[0]

    except Exception as e:
        health_report["errors"].append(str(e))

    return health_report
