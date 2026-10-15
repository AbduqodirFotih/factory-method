import threading
import time
from concurrent.futures import ThreadPoolExecutor
from enum import Enum


class TimeUnit(Enum):
    MILLISECONDS = 0.001
    SECONDS = 1
    MINUTES = 60


class TaskScheduler:
    MAX_TASKS = 5

    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=self.MAX_TASKS)
        self.timers = []
        self.lock = threading.Lock()
        self.is_shutdown = False

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def schedule(self, task, delay, unit=TimeUnit.SECONDS):
        with self.lock:
            if self.is_shutdown:
                raise RuntimeError("Scheduler is shut down")
            seconds = delay * unit.value
            timer = threading.Timer(seconds, self.run_task, args=(task,))
            timer.daemon = True
            self.timers.append(timer)
            timer.start()

    def run_task(self, task):
        with self.lock:
            if not self.is_shutdown:
                self.executor.submit(task)

    def shutdown(self):
        with self.lock:
            self.is_shutdown = True
            for timer in self.timers:
                timer.cancel()
            self.timers.clear()
        self.executor.shutdown(wait=True)


running = 0
max_running = 0
finished = []
counter_lock = threading.Lock()


def make_task(name):
    def task():
        global running, max_running
        with counter_lock:
            running += 1
            max_running = max(max_running, running)
        time.sleep(0.3)
        with counter_lock:
            running -= 1
            finished.append(name)
    return task


scheduler_ids = set()


def client(number):
    scheduler = TaskScheduler.get_instance()
    scheduler_ids.add(id(scheduler))
    for i in range(2):
        scheduler.schedule(make_task(f"client{number}-task{i}"), 100, TimeUnit.MILLISECONDS)


threads = [threading.Thread(target=client, args=(n,)) for n in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print("scheduler objects:", len(scheduler_ids))
time.sleep(2)
print("finished tasks:", len(finished))
print("max running at the same time:", max_running)

scheduler = TaskScheduler.get_instance()
scheduler.schedule(make_task("late"), 10, TimeUnit.SECONDS)
scheduler.shutdown()
print("late task finished:", "late" in finished)
try:
    scheduler.schedule(make_task("new"), 1)
except RuntimeError as e:
    print("Error:", e)
