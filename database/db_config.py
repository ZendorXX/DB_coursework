import os
import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse

# Формат DATABASE_URL: postgresql://user:password@host:port/dbname
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:1234@localhost:5432/postgres")

_url = urlparse(DATABASE_URL)
DB_NAME     = _url.path.lstrip("/")          # имя базы данных
DB_USER     = _url.username                  # пользователь
DB_PASSWORD = _url.password                  # пароль
DB_HOST     = _url.hostname                  # хост
DB_PORT     = _url.port                      # порт

def get_connection():
    """
    Создает подключение к базе данных.
    """
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        raise Exception(f"Ошибка подключения к базе данных: {e}")