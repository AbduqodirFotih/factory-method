from abc import ABC, abstractmethod
from math import pi


class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        pass

    @abstractmethod
    def perimeter(self) -> float:
        pass

    def describe(self) -> str:
        return f"{self.__class__.__name__}: Area={self.area():.2f}, Perimeter={self.perimeter():.2f}"


class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius

    def area(self) -> float:
        return pi * self.radius ** 2

    def perimeter(self) -> float:
        return 2 * pi * self.radius


class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)


class Square(Shape):
    def __init__(self, side: float):
        self.side = side

    def area(self) -> float:
        return self.side ** 2

    def perimeter(self) -> float:
        return 4 * self.side


class ShapeFactory:
    _shapes = {
        "circle": Circle,
        "rectangle": Rectangle,
        "square": Square,
    }

    @staticmethod
    def create_shape(shape_type: str, *args) -> Shape:
        shape_class = ShapeFactory._shapes.get(shape_type.lower())
        if shape_class is None:
            raise ValueError(f"Unknown shape type: {shape_type}")
        return shape_class(*args)


def test_shape_factory():
    factory = ShapeFactory()

    circle = factory.create_shape("circle", 5)
    rectangle = factory.create_shape("rectangle", 4, 6)
    square = factory.create_shape("square", 3)

    shapes = [circle, rectangle, square]

    for shape in shapes:
        print(shape.describe())


if __name__ == "__main__":
    test_shape_factory()
