import threading
import time
from datetime import datetime
from pathlib import Path


class Logger:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.log_file = Path(__file__).parent / "app.log"
        self.write_lock = threading.Lock()
        self.initialize_log_file()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def initialize_log_file(self):
        try:
            self.log_file.touch(exist_ok=True)
        except OSError as e:
            print("Cannot create log file:", e)

    def log(self, level, message):
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{time_now}] [{level.upper()}] {message}\n"
        with self.write_lock:
            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(line)
            except OSError as e:
                print("Cannot write log:", e)


class UnsafeLogger:
    _instance = None

    def __init__(self):
        time.sleep(0.05)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


def count_instances(get_instance):
    ids = set()

    def worker():
        ids.add(id(get_instance()))

    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return len(ids)


def log_worker(number):
    logger = Logger.get_instance()
    for i in range(3):
        logger.log("info", f"Thread-{number} message {i}")


(Path(__file__).parent / "app.log").write_text("", encoding="utf-8")

print("UnsafeLogger, 10 threads ->", count_instances(UnsafeLogger.get_instance), "objects")
print("Logger, 10 threads       ->", count_instances(Logger.get_instance), "object")

threads = [threading.Thread(target=log_worker, args=(n,)) for n in range(5)]
for t in threads:
    t.start()
for t in threads:
    t.join()
Logger.get_instance().log("error", "Something went wrong")

lines = Logger.get_instance().log_file.read_text(encoding="utf-8").splitlines()
print("Lines in app.log:", len(lines))
for line in lines[:3]:
    print(line)
