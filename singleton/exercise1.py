from pathlib import Path


class ConfigurationManager:
    _instance = None
    _key = object()

    def __init__(self, key=None):
        if key is not ConfigurationManager._key:
            raise RuntimeError("Use get_instance() instead")
        self.file_path = Path(__file__).parent / "config.properties"
        self.properties = {}
        self.load_count = 0
        self.load_properties()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            print("Creating ConfigurationManager...")
            cls._instance = cls(cls._key)
        return cls._instance

    def load_properties(self):
        self.load_count += 1
        try:
            with open(self.file_path, encoding="utf-8") as f:
                result = {}
                for line in f:
                    line = line.strip()
                    if line == "" or line.startswith("#") or "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    result[key.strip()] = value.strip()
                self.properties = result
        except FileNotFoundError:
            print(f"Warning: {self.file_path.name} not found, using empty config")
            self.properties = {}

    def get_property(self, key, default=None):
        return self.properties.get(key, default)

    def reload_config(self):
        self.load_properties()


class SimpleConfig:
    def __init__(self):
        self.properties = {}
        with open(Path(__file__).parent / "config.properties", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    self.properties[key.strip()] = value.strip()


print("--- With Singleton ---")
print("instance before:", ConfigurationManager._instance)
a = ConfigurationManager.get_instance()
b = ConfigurationManager.get_instance()
print("a is b:", a is b)
print("app.name:", a.get_property("app.name"))
print("file loaded:", a.load_count, "time(s)")

a.properties["app.name"] = "Changed"
print("b sees:", b.get_property("app.name"))
b.reload_config()
print("after reload a sees:", a.get_property("app.name"))

try:
    c = ConfigurationManager()
except RuntimeError as e:
    print("Error:", e)

print("\n--- Without Singleton ---")
x = SimpleConfig()
y = SimpleConfig()
print("x is y:", x is y)
x.properties["app.name"] = "Changed"
print("x:", x.properties["app.name"], "| y:", y.properties["app.name"])

print("\n--- File not found ---")
a.file_path = Path(__file__).parent / "missing.properties"
a.reload_config()
print("db.host:", a.get_property("db.host", "default-host"))
