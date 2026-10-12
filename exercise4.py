import threading
from datetime import datetime


class Logger:
    _instance = None
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._initialized = False
                    cls._instance = instance
        return cls._instance

    def __init__(self, log_file: str = "application.log"):
        if self._initialized:
            return
        self.log_file = log_file
        self._write_lock = threading.Lock()
        self._initialized = True

    @classmethod
    def get_instance(cls) -> "Logger":
        return cls()

    def log(self, message: str, level: str = "INFO") -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        thread_name = threading.current_thread().name
        line = f"[{timestamp}] [{level}] [{thread_name}] {message}"
        with self._write_lock:
            with open(self.log_file, "a", encoding="utf-8") as file:
                file.write(line + "\n")
            print(f"LOG: {line}")

    def clear(self) -> None:
        with self._write_lock:
            open(self.log_file, "w", encoding="utf-8").close()


class UserController:
    def handle_request(self, user: str) -> None:
        Logger.get_instance().log(f"Controller: request from {user}")


class PaymentService:
    def charge(self, amount: float) -> None:
        Logger.get_instance().log(f"Service: charged {amount} UZS")


def format_size(size: int) -> str:
    Logger.get_instance().log(f"Utility: formatting {size} bytes", level="DEBUG")
    return f"{size / 1024:.1f} KB"


def test_single_instance():
    print("\n--- Test 1: only one instance ---")
    logger1 = Logger()
    logger2 = Logger()
    logger3 = Logger.get_instance()

    print(f"id(logger1) = {id(logger1)}")
    print(f"id(logger2) = {id(logger2)}")
    print(f"id(logger3) = {id(logger3)}")
    assert logger1 is logger2 is logger3
    print("OK: all variables point to the same object")


def test_thread_safe_creation():
    print("\n--- Test 2: thread-safe creation ---")
    Logger._instance = None
    instances = []
    instances_lock = threading.Lock()

    def create_logger():
        logger = Logger()
        with instances_lock:
            instances.append(logger)

    threads = [threading.Thread(target=create_logger) for _ in range(50)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    unique_ids = {id(logger) for logger in instances}
    print(f"Threads: {len(instances)}, unique instances: {len(unique_ids)}")
    assert len(unique_ids) == 1
    print("OK: 50 threads received the same instance")


def test_synchronized_writing():
    print("\n--- Test 3: synchronized writing from components ---")
    logger = Logger.get_instance()
    logger.clear()

    def worker(number: int):
        UserController().handle_request(f"user{number}")
        PaymentService().charge(number * 1000)
        format_size(number * 2048)

    threads = [threading.Thread(target=worker, args=(i,), name=f"Worker-{i}") for i in range(1, 6)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    with open(logger.log_file, encoding="utf-8") as file:
        lines = file.read().splitlines()

    print(f"Lines in {logger.log_file}: {len(lines)}")
    assert len(lines) == 15
    assert all(line.startswith("[") for line in lines)
    print("OK: all 15 messages are in one file and none are corrupted")


if __name__ == "__main__":
    test_single_instance()
    test_thread_safe_creation()
    test_synchronized_writing()
