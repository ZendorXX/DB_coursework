import threading
import json
import queue
from database.redis_client import get_redis

# Глобальная очередь для хранения входящих сообщений
notifications_queue: "queue.Queue[dict]" = queue.Queue()


def _listen(channels):
    """
    Фоновая функция: подписывается на каналы и кладёт сообщения в очередь.
    """
    r = get_redis()
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    # Подписываемся на список каналов
    pubsub.subscribe(*channels)
    for msg in pubsub.listen():
        if msg['type'] != 'message':
            continue
        try:
            data = json.loads(msg["data"])
        except Exception:
            data = {"type": "unknown", "raw": msg["data"]}
        # Добавляем информацию о канале
        record = {"channel": msg['channel'], **data}
        notifications_queue.put(record)


def start_listener(channels):
    """
    Запустить прослушивание каналов в отдельном демоне-потоке.
    channels: список названий каналов или одиночная строка.
    """
    if isinstance(channels, str):
        channels = [channels]
    thread = threading.Thread(target=_listen, args=(channels,), daemon=True)
    thread.start()
    return thread
