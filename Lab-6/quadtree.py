"""Модуль квадродерева.

Содержит необходимые элементы для реализации квадродерева.

Импорты:
    from math import ... - для вычислений
    from pygame import ... - для отрисовки кадров
    from particle import ... - для взаимодействия с частицами

Константы:
    MAX_DEPTH - максимальная глубина рекурсии

Классы:
    Rectangle - класс прямоугольника
    QuadTree - класс квадродерева

"""
from math import sqrt

from pygame import Surface, draw

from particle import Particle, check_collision, handle_collision


MAX_DEPTH = 10


class Rectangle:
    """Класс прямоугольника.

    Методы:
        resize - изменить размер
        move - переместить
        contains - проверить, содержит ли частицу
        intersection - проверить пересечение с другим прямоугольником
        draw - отрисовать

    """

    def __init__(self, x: float, y: float, width: float,
                 height: float, color: tuple[int]=(0, 255, 0),
                 thickness: int=1):
        """Инициализировать.

        Аргументы:
            x: float - положение левой стороны по x
            y: float - положение верхней стороны по y
            width: float - ширина
            height: float - высота
            color: tuple[int] - цвет контура в RGB, по умолчанию (0, 255, 0)
            thickness: int - толщина линии контура, по умолчанию 1

        """
        self.x = x
        self.y = y
        self.resize(width, height)
        self.color = color
        self.thickness = thickness

    def resize(self, width: float, height: float):
        """Изменить размер на width x height."""
        self.width = 0 if width < 0 else width
        self.height = 0 if height < 0 else height
        self.max_x = self.x + width
        self.max_y = self.y + height

    def move(self, x: float, y: float):
        """Переместить на x и y."""
        self.x = x - self.width / 2
        self.y = y - self.height / 2
        self.max_x = x + self.width / 2
        self.max_y = y + self.height / 2

    def contains(self, particle: Particle) -> bool:
        """Проверить, содержит ли частицу."""
        x = max(self.x, min(particle.pos.x, self.max_x))
        y = max(self.y, min(particle.pos.y, self.max_y))
        dist = sqrt((x - particle.pos.x) ** 2 + (y - particle.pos.y) ** 2)
        return dist < particle.radius

    def intersection(self, other) -> bool:
        """Проверить пересечение с другим прямоугольником."""
        return not (self.y > other.max_y or self.max_y < other.y
                    or self.x > other.max_x or self.max_x < other.x)

    def draw(self, screen: Surface):
        """Отрисовать на экране (screen)."""
        draw.rect(screen, self.color,
                  (self.x, self.y, self.width, self.height), self.thickness)


class QuadTree:
    """Класс квадродерева.

    Методы:
        subdivide - поделить на квадранты
        insert - вставить частицу
        remove - удалить частицу
        get_particles - получить все частицы, попадающие в квадрант
        query - получить частицы, попадающие в область
        handle_collisions - разрешить столкновения частиц

    """

    def __init__(self, parent, screen: Surface, border: Rectangle,
                 capacity: int, visible: bool, depth: int=0):
        """Инициализировать.

        Аргументы:
            parent - родительский квадрант
            screen: Surface - экран, на котором будет отрисовано дерево
            border: Rectangle - граница квадранта
            capacity: int - объем квадранта
            visible: bool - видимость дерева
            depth: int - текущая глубина рекурсии, по умолчанию 0

        """
        self.parent = parent
        self.screen = screen
        self.border = border
        self.capacity = capacity
        self.visible = visible
        self.depth = depth
        self.particles = set()
        self.north_west = None
        self.north_east = None
        self.south_west = None
        self.south_east = None

    def subdivide(self):
        """Поделить на квадранты."""
        width = self.border.width // 2
        height = self.border.height // 2

        nw = Rectangle(self.border.x, self.border.y, width, height)
        ne = Rectangle(self.border.x + width, self.border.y, width, height)
        sw = Rectangle(self.border.x, self.border.y + height, width, height)
        se = Rectangle(self.border.x + width,
                       self.border.y + height, width, height)

        self.north_west = QuadTree(self, self.screen, nw, self.capacity,
                                   self.visible, self.depth + 1)
        self.north_east = QuadTree(self, self.screen, ne, self.capacity,
                                   self.visible, self.depth + 1)
        self.south_west = QuadTree(self, self.screen, sw, self.capacity,
                                   self.visible, self.depth + 1)
        self.south_east = QuadTree(self, self.screen, se, self.capacity,
                                   self.visible, self.depth + 1)

    def insert(self, particle: Particle):
        """Вставить частицу."""
        if not self.border.contains(particle):
            return
        if (self.north_west is None and len(self.particles) < self.capacity
                or self.depth == MAX_DEPTH):
            self.particles.add(particle)
        else:
            particles = {particle}
            if self.north_west is None:
                self.subdivide()
                particles |= self.particles
                self.particles = set()
            for particle in particles:
                self.north_west.insert(particle)
                self.north_east.insert(particle)
                self.south_west.insert(particle)
                self.south_east.insert(particle)

    def remove(self, particle: Particle):
        """Удалить частицу."""
        if not self.border.contains(particle):
            return
        if self.north_west is not None:
            self.north_west.remove(particle)
            self.north_east.remove(particle)
            self.south_west.remove(particle)
            self.south_east.remove(particle)
        else:
            self.particles.remove(particle)
            if self.parent is not None:
                particles = self.parent.get_particles()
                if len(particles) <= self.parent.capacity:
                    self.parent.particles = particles
                    self.parent.north_west = None

    def get_particles(self) -> set[Particle]:
        """Получить все частицы попадающие в квадрант."""
        particles = self.particles
        if self.north_west is not None:
            particles |= self.north_west.get_particles()
            particles |= self.north_east.get_particles()
            particles |= self.south_west.get_particles()
            particles |= self.south_east.get_particles()
        return particles

    def query(self, area) -> set[Particle]:
        """Получить частицы, попадающие в область."""
        particles = set()
        if not area.intersection(self.border):
            return particles
        if self.north_west is not None:
            particles |= self.north_west.query(area)
            particles |= self.north_east.query(area)
            particles |= self.south_west.query(area)
            particles |= self.south_east.query(area)
        else:
            for particle in self.particles:
                if area.contains(particle):
                    particles.add(particle)
        return particles

    def handle_collisions(self):
        """Разрешить столкновения частиц."""
        num = len(self.particles)
        particles = tuple(self.particles)
        for i in range(num - 1):
            for j in range(i + 1, num):
                if check_collision(particles[i], particles[j]):
                    handle_collision(particles[i], particles[j])
        if self.north_west is not None:
            self.north_west.handle_collisions()
            self.north_east.handle_collisions()
            self.south_west.handle_collisions()
            self.south_east.handle_collisions()
        if self.visible:
            self.border.draw(self.screen)
