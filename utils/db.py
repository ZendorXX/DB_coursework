from psycopg2.extras import RealDictCursor

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