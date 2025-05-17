import redis, os

REDIS_CONFIG = {
    "host": os.getenv("REDIS_HOST", "localhost"),
    "port": int(os.getenv("REDIS_PORT", 6379)),
    "password": os.getenv("REDIS_PASSWORD", None),
    "decode_responses": True
}

# Время жизни в секундах
TOKEN_TTL   = int(os.getenv("REDIS_TOKEN_TTL",   3600))  # токены авторизации
SESSION_TTL = int(os.getenv("REDIS_SESSION_TTL", 1800))  # данные сессии
CACHE_TTL   = int(os.getenv("REDIS_CACHE_TTL",   300))  # кэш списка/рейтинга

def get_redis():
    return redis.Redis(**REDIS_CONFIG)