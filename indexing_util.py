import redis
import os
import dotenv
dotenv.load_dotenv()

hotkey_daily_indexing = redis.Redis(host = os.getenv("REDIS_HOST"), port = os.getenv("REDIS_PORT"), password=os.getenv("REDIS_PASSWORD"), db = 2)
hotkey_indexing = redis.Redis(host = os.getenv("REDIS_HOST"), port = os.getenv("REDIS_PORT"), password=os.getenv("REDIS_PASSWORD"), db = 3)
daily_indexing = redis.Redis(host = os.getenv("REDIS_HOST"), port = os.getenv("REDIS_PORT"), password=os.getenv("REDIS_PASSWORD"), db = 4)

def get_all(redis_db):
    keys = redis_db.keys()
    # print(keys)
    result = []
    for key in keys:
        value = redis_db.get(key)
        result.append((key, value))
    return result
if __name__ == "__main__":
    print(get_all(hotkey_daily_indexing))
    print(get_all(hotkey_indexing))
    print(get_all(daily_indexing))