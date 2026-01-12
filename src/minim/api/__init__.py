import sqlite3

from .. import MINIM_DIR

__all__ = ["apple", "deezer", "qobuz", "spotify", "tidal"]

AUTH_DB_FILE = MINIM_DIR / "auth.db"
db_connection = sqlite3.connect(AUTH_DB_FILE)
db_cursor = db_connection.cursor()
db_cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS tokens (
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        client_name TEXT,
        authorization_flow TEXT,
        client_id TEXT,
        client_secret TEXT,
        user_identifier TEXT,
        redirect_uri TEXT,
        scopes TEXT,
        token_type TEXT,
        access_token TEXT,
        expires_at TIMESTAMP,
        refresh_token TEXT,
        extras TEXT,
        PRIMARY KEY (
            client_name, 
            authorization_flow, 
            client_id, 
            user_identifier
        )
    )
    """
)
db_connection.commit()
