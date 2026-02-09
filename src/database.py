"""Module de connexion a la base de donnees."""
import time
from contextlib import contextmanager
import mysql.connector
from mysql.connector import Error
from src.config import Config

def get_connection():
    """Cree une connexion a la base de donnees."""
    return mysql.connector.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        database=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD
    )

def get_connection_with_retry(max_retries=5, delay=2):
    """Connexion avec tentatives multiples."""
    for attempt in range(max_retries):
        try:
            conn = get_connection()
            print(f"Connexion etablie a {Config.DB_HOST}")
            return conn
        except Error as e:
            print(f"Tentative {attempt+1}/{max_retries}: {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
    raise Exception("Impossible de se connecter a la base")

@contextmanager
def database_connection():
    """Context manager pour les connexions."""
    conn = get_connection_with_retry()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
