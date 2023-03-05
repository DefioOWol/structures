"""Модуль частицы.

Содержит необходимые элементы для реализации частицы.

Импорты:
    from math import ... - для вычислений
    from pygame import ... - для отрисовки кадров

Константы:
    FPS - частота кадров
    DT - промежуток времени за кадр

Классы:
    Vector - класс вектора
    Particle - класс частицы

Функции:
    check_collision - проверить, произошло ли столкновение частиц
    handle_collision - разрешить столкновение чатиц

"""
from math import sqrt, pi

from pygame import Surface, draw


FPS = 120
DT = 1 / FPS


class Vector:
    """Класс вектора.

    Методы:
        length - получить длину вектора

    """

    def __init__(self, x: float=0, y: float=0):
        """Инициализировать вектор (x, y)."""
        self.x = x
        self.y = y

    def length(self) -> float:
        """Получить длину."""
        return sqrt(self.x ** 2 + self.y ** 2)

    def __add__(self, other):
        """Сложить с другим вектором."""
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        """Найти разность с другим вектором."""
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        """Найти скалярное произведение с другим вектором или умножить на число."""
        if isinstance(other, Vector):
            return self.x * other.x + self.y * other.y
        return Vector(self.x * other, self.y * other)

    def __truediv__(self, other: float):
        """Поделить на число."""
        try:
            return Vector(self.x / other, self.y / other)
        except ZeroDivisionError:
            return Vector()

    def __eq__(self, other):
        """Проверить равенство с другим вектором."""
        return self.x == other.x and self.y == other.y


class Particle:
    """Класс частицы.

    Методы:
        shift - сместить
        dynamic - выполнить динамику
        handle_border_collision - разрешить столкновение с границей экрана
        draw - отрисовать

    """

    def __init__(self, screen: Surface, radius: float, pos: Vector,
                 speed: Vector, acceleration: Vector=Vector()):
        """Инициализировать.

        Аргументы:
            screen: Surface - экран, на котором будет отрисована частица
            radius: float - радиус
            pos: Vector - позиция
            speed: Vector - скорость
            acceleration: Vector - ускорение, по умолчанию Vector()

        """
        self.screen = screen
        self.radius = radius
        self.weight = pi * radius ** 2
        self.pos = pos
        self.speed = speed
        self.acceleration = acceleration

    def shift(self, shift: Vector):
        """Сместить на shift."""
        self.pos = self.pos + shift

    def dynamic(self):
        """Выполнить динамику."""
        self.speed = self.speed + self.acceleration * DT
        self.shift(self.speed * DT)
        self.handle_border_collision()
        self.draw((0, 255, 0))

    def handle_border_collision(self):
        """Разрешить столкновение с границей экрана."""
        if self.pos.x - self.radius <= 0:
            if self.speed.x < 0:
                self.speed.x = -self.speed.x
        elif self.pos.x + self.radius >= self.screen.get_width():
            if self.speed.x > 0:
                self.speed.x = -self.speed.x
        if self.pos.y - self.radius <= 0:
            if self.speed.y < 0:
                self.speed.y = -self.speed.y
        elif self.pos.y + self.radius >= self.screen.get_height():
            if self.speed.y > 0:
                self.speed.y = -self.speed.y

    def draw(self, color):
        """Отрисовать с цветом (color)."""
        draw.circle(self.screen, color, (self.pos.x, self.pos.y), self.radius)


def check_collision(first: Particle, second: Particle) -> bool:
    """Проверить столкновение двух частиц."""
    return (second.pos - first.pos).length() <= first.radius + second.radius


def handle_collision(first: Particle, second: Particle):
    """Разрешить столкновение двух частиц."""
    n = Vector(second.pos.x - first.pos.x, second.pos.y - first.pos.y)
    un = n / n.length()
    ut = Vector(-un.y, un.x)

    v1n, nv1t = un * first.speed, ut * (ut * first.speed)
    v2n, nv2t = un * second.speed, ut * (ut * second.speed)

    nv1n = un * ((v1n * (first.weight - second.weight)
                 + 2 * second.weight * v2n) / (first.weight + second.weight))
    nv2n = un * ((v2n * (second.weight - first.weight)
                 + 2 * first.weight * v1n) / (first.weight + second.weight))

    prev_first, prev_second = first.speed, second.speed
    first.speed, second.speed = nv1n + nv1t, nv2n + nv2t
    first.shift((first.speed - prev_first) * DT)
    second.shift((second.speed - prev_second) * DT)
