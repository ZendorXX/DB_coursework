from psycopg2.extras import RealDictCursor
from database.redis_client import CACHE_TTL
import json

def execute_query(conn, query, params=None):
    """
    Выполняет запрос, который не возвращает результат (например, INSERT, UPDATE, DELETE, CALL).
    """
    with conn.cursor() as cur:
        cur.execute(query, params)
        conn.commit()

def fetch_query(conn, query, params=None):
    """
    Выполняет запрос, который возвращает результат (например, SELECT).
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query, params)
        return cur.fetchall()
    
def fetch_with_cache(conn, redis_client, key, query, params=None, ttl=CACHE_TTL):
    """
    Возвращает данные из Redis-кеша по ключу `key`, если есть;
    иначе выполняет SQL-запрос, сохраняет результат в Redis с TTL и возвращает его.
    """
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    rows = fetch_query(conn, query, params)
    redis_client.setex(key, ttl, json.dumps(rows))
    return rows