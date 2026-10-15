import copy
import pickle
import threading
import time
from enum import Enum


class CacheEntry:
    def __init__(self, value, ttl_seconds):
        self.value = value
        self.expires_at = time.time() + ttl_seconds

    def is_expired(self):
        return time.time() >= self.expires_at


class CacheManager(Enum):
    INSTANCE = 1

    def __init__(self, value):
        self.cache = {}
        self.lock = threading.Lock()
        self.start_cleanup_thread()

    def start_cleanup_thread(self):
        def cleanup():
            while True:
                time.sleep(0.5)
                with self.lock:
                    expired = [key for key, entry in self.cache.items() if entry.is_expired()]
                    for key in expired:
                        del self.cache[key]
                if expired:
                    print("cleanup removed:", expired)

        thread = threading.Thread(target=cleanup, daemon=True)
        thread.start()

    def put(self, key, value, ttl_seconds):
        with self.lock:
            self.cache[key] = CacheEntry(value, ttl_seconds)

    def get(self, key):
        with self.lock:
            entry = self.cache.get(key)
            if entry is None:
                return None
            if entry.is_expired():
                del self.cache[key]
                return None
            return entry.value

    def remove(self, key):
        with self.lock:
            return self.cache.pop(key, None) is not None

    def size(self):
        with self.lock:
            return len(self.cache)


cache = CacheManager.INSTANCE
other = CacheManager.INSTANCE
print("cache is other:", cache is other)

cache.put("user:1", {"name": "Ali"}, 1)
cache.put("settings", {"theme": "dark"}, 60)
print("read from other:", other.get("user:1"))

print("waiting 1.5 seconds...")
time.sleep(1.5)
print("user:1 =", cache.get("user:1"))
print("settings =", cache.get("settings"))
print("removed settings:", cache.remove("settings"), "| size:", cache.size())


def writer(number):
    for i in range(100):
        CacheManager.INSTANCE.put(f"t{number}-{i}", i, 60)


threads = [threading.Thread(target=writer, args=(n,)) for n in range(5)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print("5 threads x 100 items, size:", cache.size())

print("copy:", copy.copy(cache) is cache)
print("deepcopy:", copy.deepcopy(cache) is cache)
print("pickle:", pickle.loads(pickle.dumps(cache)) is cache)
try:
    CacheManager(2)
except ValueError as e:
    print("Error:", e)
