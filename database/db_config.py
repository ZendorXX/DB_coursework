import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = "postgresql://postgres:1234@localhost:5432/postgres"

def get_connection():
    """
    Создает подключение к базе данных.
    """
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        raise Exception(f"Ошибка подключения к базе данных: {e}")