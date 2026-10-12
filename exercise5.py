from abc import ABC, abstractmethod
from typing import Dict, Type


class Payment(ABC):
    def __init__(self, amount: float):
        self.amount = amount

    @abstractmethod
    def validate(self) -> bool:
        pass

    @abstractmethod
    def process(self) -> str:
        pass


class CreditCardPayment(Payment):
    def __init__(self, amount: float, card_number: str = "8600123456789012"):
        super().__init__(amount)
        self.card_number = card_number

    def validate(self) -> bool:
        print(f"  Checking card number ****{self.card_number[-4:]}")
        return len(self.card_number) == 16 and self.card_number.isdigit()

    def process(self) -> str:
        return f"Credit card payment of {self.amount} UZS completed"


class PaymePayment(Payment):
    def __init__(self, amount: float, phone: str = "+998901234567"):
        super().__init__(amount)
        self.phone = phone

    def authenticate(self) -> bool:
        print(f"  Authenticating Payme account {self.phone}")
        return self.phone.startswith("+998")

    def validate(self) -> bool:
        return self.authenticate()

    def process(self) -> str:
        return f"Payme payment of {self.amount} UZS completed"


class ClickPayment(Payment):
    def __init__(self, amount: float, address: str = "Tashkent"):
        super().__init__(amount)
        self.address = address

    def validate_address(self) -> bool:
        print(f"  Validating address: {self.address}")
        return bool(self.address)

    def validate(self) -> bool:
        return self.validate_address()

    def process(self) -> str:
        return f"Click payment of {self.amount} UZS completed"


class PaymentFactory:
    _payments: Dict[str, Type[Payment]] = {
        "creditcard": CreditCardPayment,
        "payme": PaymePayment,
        "click": ClickPayment,
    }

    @classmethod
    def register_payment(cls, name: str, payment_class: Type[Payment]) -> None:
        if not isinstance(payment_class, type) or not issubclass(payment_class, Payment):
            raise TypeError(f"{payment_class} must be a subclass of Payment")
        cls._payments[name.lower()] = payment_class

    @classmethod
    def create_payment(cls, payment_type: str, amount: float, **kwargs) -> Payment:
        payment_class = cls._payments.get(payment_type.lower())
        if payment_class is None:
            raise ValueError(f"Unknown payment type: {payment_type}")
        return payment_class(amount, **kwargs)

    @classmethod
    def list_available_types(cls) -> list:
        return list(cls._payments.keys())


class PaymentProcessor:
    def process_payment(self, payment_type: str, amount: float, **kwargs) -> None:
        payment = PaymentFactory.create_payment(payment_type, amount, **kwargs)
        print(f"\nProcessing {payment.__class__.__name__}")
        if payment.validate():
            print(f"  {payment.process()}")
        else:
            print("  Validation failed, payment rejected")


class UzumPayment(Payment):
    def __init__(self, amount: float, account_id: str = "UZUM-001"):
        super().__init__(amount)
        self.account_id = account_id

    def validate(self) -> bool:
        print(f"  Checking Uzum account {self.account_id}")
        return self.account_id.startswith("UZUM-")

    def process(self) -> str:
        return f"Uzum payment of {self.amount} UZS completed"


def test_payment_factory():
    processor = PaymentProcessor()

    print("Available payment types:", PaymentFactory.list_available_types())

    processor.process_payment("creditcard", 150000)
    processor.process_payment("payme", 75000, phone="+998935554433")
    processor.process_payment("click", 50000, address="Samarkand")
    processor.process_payment("creditcard", 1000, card_number="1234")

    print("\n--- Adding a new payment method ---")
    PaymentFactory.register_payment("uzum", UzumPayment)
    print("Available payment types:", PaymentFactory.list_available_types())
    processor.process_payment("uzum", 200000, account_id="UZUM-777")

    try:
        processor.process_payment("bitcoin", 10)
    except ValueError as error:
        print(f"\nError: {error}")


if __name__ == "__main__":
    test_payment_factory()
