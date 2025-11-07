import sqlite3

from .. import MINIM_DIR

__all__ = ["apple", "spotify", "tidal"]

AUTH_DB_FILE = MINIM_DIR / "auth.db"
db_connection = sqlite3.connect(AUTH_DB_FILE)
db_cursor = db_connection.cursor()
db_cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS tokens (
        added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        client TEXT,
        flow TEXT,
        client_id TEXT,
        client_secret TEXT,
        user_identifier TEXT,
        redirect_uri TEXT,
        scopes TEXT,
        token_type TEXT,
        access_token TEXT,
        expiry TIMESTAMP,
        refresh_token TEXT,
        PRIMARY KEY (client, flow, client_id, user_identifier)
    )
    """
)
db_connection.commit()
