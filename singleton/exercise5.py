import copy
import importlib.util
import pickle
from enum import Enum


class WeakSecurityManager:
    _instance = None

    def __init__(self):
        self.login_attempts = 0

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def login(self, username, password):
        self.login_attempts += 1
        return username == "admin" and password == "1234"

    def get_login_attempts(self):
        return self.login_attempts


def get_security_manager():
    return SecurityManager.get_instance()


class SecurityManager:
    _instance = None

    def __init__(self):
        if SecurityManager._instance is not None:
            raise RuntimeError("Already instantiated")
        self.login_attempts = 0

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __reduce__(self):
        return (get_security_manager, ())

    def __copy__(self):
        raise TypeError("Cannot copy singleton")

    def __deepcopy__(self, memo):
        raise TypeError("Cannot copy singleton")

    def login(self, username, password):
        self.login_attempts += 1
        return username == "admin" and password == "1234"

    def get_login_attempts(self):
        return self.login_attempts


class SecurityManagerEnum(Enum):
    INSTANCE = 1

    def __init__(self, value):
        self.login_attempts = 0

    def login(self, username, password):
        self.login_attempts += 1
        return username == "admin" and password == "1234"

    def get_login_attempts(self):
        return self.login_attempts


def reflection_attack(cls):
    obj = object.__new__(cls)
    cls.__init__(obj)
    return obj


def serialization_attack(obj):
    return pickle.loads(pickle.dumps(obj))


def clone_attack(obj):
    return copy.copy(obj)


def test(cls):
    original = cls.get_instance()
    attacks = [
        ("Reflection", lambda: reflection_attack(cls)),
        ("Serialization", lambda: serialization_attack(original)),
        ("Cloning", lambda: clone_attack(original)),
    ]
    for name, attack in attacks:
        try:
            result = attack()
            if result is original:
                print(f"  {name}: safe (same object)")
            else:
                print(f"  {name}: BROKEN (new object)")
        except Exception as e:
            print(f"  {name}: safe ({e})")


def load_module_again():
    spec = importlib.util.spec_from_file_location("security_copy", __file__)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


if __name__ == "__main__":
    print("WeakSecurityManager:")
    test(WeakSecurityManager)

    print("\nSecurityManager:")
    test(SecurityManager)

    print("\nSecurityManagerEnum:")
    e = SecurityManagerEnum.INSTANCE
    print("  Serialization:", serialization_attack(e) is e)
    print("  Cloning:", clone_attack(e) is e, copy.deepcopy(e) is e)
    try:
        SecurityManagerEnum(2)
    except ValueError as err:
        print("  New object:", err)

    print("\nWhy it matters:")
    weak = WeakSecurityManager.get_instance()
    for i in range(3):
        weak.login("admin", "wrong")
    fake = serialization_attack(weak)
    fake.login_attempts = 0
    print("  real attempts:", weak.get_login_attempts(), "| fake attempts:", fake.get_login_attempts())

    safe = SecurityManager.get_instance()
    for i in range(3):
        safe.login("admin", "wrong")
    print("  protected after pickle:", serialization_attack(safe).get_login_attempts())

    print("\nTwo class loaders:")
    m1 = load_module_again()
    m2 = load_module_again()
    print("  SecurityManager same:", m1.SecurityManager.get_instance() is m2.SecurityManager.get_instance())
    print("  Enum same:", m1.SecurityManagerEnum.INSTANCE is m2.SecurityManagerEnum.INSTANCE)
