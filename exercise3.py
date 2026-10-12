from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Type, Optional


@dataclass
class NotificationConfig:
    priority: str = "normal"
    retry_count: int = 3
    timeout: int = 30


class Notification(ABC):
    def __init__(self, recipient: str, message: str, config: NotificationConfig = None):
        self.recipient = recipient
        self.message = message
        self.config = config or NotificationConfig()
        self.status = "pending"

    @abstractmethod
    def send(self) -> bool:
        pass

    @abstractmethod
    def format_message(self) -> str:
        pass

    def get_status(self) -> dict:
        return {
            "type": self.__class__.__name__,
            "recipient": self.recipient,
            "status": self.status,
            "priority": self.config.priority
        }


class EmailNotification(Notification):
    def __init__(self, recipient: str, message: str, subject: str, config: NotificationConfig = None):
        super().__init__(recipient, message, config)
        self.subject = subject

    def send(self) -> bool:
        print(f" Sending email to {self.recipient}")
        self.status = "sent"
        return True

    def format_message(self) -> str:
        return f"Dear {self.recipient},\n\n{self.message}"


class SMSNotification(Notification):
    def send(self) -> bool:
        print(f"📱 Sending SMS to {self.recipient}")
        self.status = "sent"
        return True

    def format_message(self) -> str:
        return f"Alert: {self.message}"


class PushNotification(Notification):
    def __init__(self, recipient: str, message: str,
                 device_token: str, badge_count: int = 0, config: NotificationConfig = None):
        super().__init__(recipient, message, config)
        self.device_token = device_token
        self.badge_count = badge_count

    def send(self) -> bool:
        print(f" Sending push to device {self.device_token[:10]}...")
        self.status = "sent"
        return True

    def format_message(self) -> str:
        return self.message


class NotificationFactory:
    _registry: Dict[str, Type[Notification]] = {}
    _priorities = ("low", "normal", "high")

    @classmethod
    def register_notification(cls, name: str, notification_class: Type[Notification]) -> None:
        if not isinstance(notification_class, type) or not issubclass(notification_class, Notification):
            raise TypeError(f"{notification_class} must be a subclass of Notification")
        cls._registry[name.lower()] = notification_class

    @classmethod
    def _validate_config(cls, config) -> bool:
        if config is None:
            return True
        if not isinstance(config, NotificationConfig):
            return False
        if config.priority not in cls._priorities:
            return False
        if config.retry_count < 0 or config.timeout <= 0:
            return False
        return True

    @classmethod
    def create_notification(
        cls,
        notification_type: str,
        recipient: str,
        message: str,
        **kwargs
    ) -> Optional[Notification]:
        notification_class = cls._registry.get(notification_type.lower())
        if notification_class is None:
            print(f"Unknown notification type: {notification_type}")
            return None

        if not recipient or not message:
            print("Recipient and message must not be empty")
            return None

        if not cls._validate_config(kwargs.get("config")):
            print(f"Invalid configuration for {notification_type}")
            return None

        try:
            return notification_class(recipient, message, **kwargs)
        except TypeError as error:
            print(f"Cannot create {notification_type} notification: {error}")
            return None

    @classmethod
    def list_available_types(cls) -> list:
        return list(cls._registry.keys())


def test_notification_factory():
    NotificationFactory.register_notification("email", EmailNotification)
    NotificationFactory.register_notification("sms", SMSNotification)
    NotificationFactory.register_notification("push", PushNotification)

    print("Available notification types:", NotificationFactory.list_available_types())

    email = NotificationFactory.create_notification(
        "email",
        "user@example.com",
        "Welcome to our service!",
        subject="Welcome Email"
    )

    sms = NotificationFactory.create_notification(
        "sms",
        "+1234567890",
        "Your verification code is 123456"
    )

    push = NotificationFactory.create_notification(
        "push",
        "user123",
        "You have a new message",
        device_token="abc123def456",
        badge_count=1
    )

    notifications = [email, sms, push]

    for notification in notifications:
        if notification:
            print(f"\nSending {notification.__class__.__name__}")
            notification.send()
            print(f"Status: {notification.get_status()}")


if __name__ == "__main__":
    test_notification_factory()
