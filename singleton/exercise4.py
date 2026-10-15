import threading
import time


class Connection:
    counter = 0

    def __init__(self):
        Connection.counter += 1
        self.id = Connection.counter
        time.sleep(0.01)

    def execute(self, sql):
        return f"Conn#{self.id}: {sql}"

    def __repr__(self):
        return f"Conn#{self.id}"


class DatabaseConnectionPool:
    MAX_POOL_SIZE = 10
    TIMEOUT = 30

    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.available_connections = []
        self.used_connections = []
        self.condition = threading.Condition()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def get_connection(self, timeout=TIMEOUT):
        end_time = time.time() + timeout
        with self.condition:
            while True:
                if self.available_connections:
                    conn = self.available_connections.pop()
                    break
                if self.get_pool_size() < self.MAX_POOL_SIZE:
                    conn = Connection()
                    break
                time_left = end_time - time.time()
                if time_left <= 0:
                    raise TimeoutError(f"No free connection in {timeout} seconds")
                self.condition.wait(time_left)
            self.used_connections.append(conn)
            return conn

    def release_connection(self, conn):
        with self.condition:
            if conn not in self.used_connections:
                raise ValueError(f"{conn} is not from this pool")
            self.used_connections.remove(conn)
            self.available_connections.append(conn)
            self.condition.notify()

    def get_pool_size(self):
        return len(self.available_connections) + len(self.used_connections)


pool = DatabaseConnectionPool.get_instance()
print("same pool:", pool is DatabaseConnectionPool.get_instance())

connections = []
for i in range(10):
    connections.append(pool.get_connection())
print("taken:", connections)
print("pool size:", pool.get_pool_size())

try:
    pool.get_connection(timeout=1)
except TimeoutError as e:
    print("Error:", e)


def give_back_later():
    time.sleep(0.5)
    pool.release_connection(connections[0])


threading.Thread(target=give_back_later).start()
start = time.time()
conn = pool.get_connection(timeout=5)
print(f"got {conn} after waiting {time.time() - start:.1f}s")

for c in connections[1:]:
    pool.release_connection(c)
pool.release_connection(conn)


def worker(number):
    p = DatabaseConnectionPool.get_instance()
    c = p.get_connection()
    c.execute(f"SELECT * FROM users WHERE id = {number}")
    time.sleep(0.1)
    p.release_connection(c)


threads = [threading.Thread(target=worker, args=(n,)) for n in range(30)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print("30 threads done, pool size:", pool.get_pool_size())
print("total connections created:", Connection.counter)
