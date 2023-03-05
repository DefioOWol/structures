"""Основной модуль программы.

Содержит необходимые элементы для запуска программы.

Импорты:
    from random import ... - для генерации случайных чисел
    import pygame - для реализации анимации
    import pygame_menu - для реализации графического интерфейса
    from particle import ... - для взаимодействия с частицами
    from quadtree import ... - для взаимодействия с квадродеревом

Константы:
    MIN_WIDTH - минимальная ширина окна
    MIN_HEIGHT - минимальная высота окна

Функции:
    create_range_slider - создать слайдер диапазона
    resize - изменить размер окна
    create_particles - создать частицы
    draw_particles - отрисовать частицы
    main - точка входа

"""
from random import randint

import pygame
import pygame_menu

from particle import Particle, Vector, FPS
from quadtree import QuadTree, Rectangle


MIN_WIDTH = 300
MIN_HEIGHT = 300


def create_range_slider(menu: pygame_menu.Menu, text: str,
                        width: int, range_value: tuple[int]):
    """Создать слайдер диапазона.

    Аргументы:
        menu: pygame_menu.Menu - меню, в котором создастся слайдер
        text: str - текст
        width: int - ширина
        range_value: tuple[int] - диапазон

    Возвращает созданный слайдер.

    """
    menu.add.label(text, font_size=16)
    return menu.add.range_slider(
        "", range_value, range_value, 1, font_size=16,
        slider_thickness=5, width=width, range_margin=(0, 0),
        slider_text_value_enabled=False, range_text_value_enabled=False
    )


def resize(menu: pygame_menu.Menu, size: tuple[float]):
    """Изменить размер окна с menu на size."""
    width = size[0] if size[0] > MIN_WIDTH else MIN_WIDTH
    height = size[1] if size[1] > MIN_HEIGHT else MIN_HEIGHT
    pygame.display.set_mode((width, height), pygame.RESIZABLE)
    menu._position = (0, 0)


def create_particles(screen: pygame.Surface, num: int, size: tuple[float],
                     speed: tuple[float]) -> tuple[Particle]:
    """Создать частицы.

    Аргументы:
        screen: pygame.Surface - экран, на котором будут отрисованы частицы
        num: int - количество
        size: tuple[float] - границы длин радиусов
        speed: tuple[float] - границы скорости

    Возвращает кортеж с созданными частицами.

    """
    particles = tuple()
    x, y, = 0, 0
    for _ in range(num):
        radius = randint(round(size[0]), round(size[1]))
        if x + radius * 2 + 4 >= screen.get_width():
            x = 0
            y += size[1] * 2 + 4
        pos = Vector(x + radius + 4, y + radius + 4)
        x = x + radius * 2 + 4
        hspeed = (randint(0, 1) * 2 - 1) * randint(round(speed[0]),
                                                   round(speed[1]))
        vspeed = (randint(0, 1) * 2 - 1) * randint(round(speed[0]),
                                                   round(speed[1]))
        particles += (Particle(screen, radius, pos, Vector(hspeed, vspeed)),)
    return particles


def draw_particles(screen: pygame.Surface, particles: tuple[Particle],
                   area: Rectangle, tree_visible: bool, area_visible: bool):
    """Отрисовать частицы.

    Аргументы:
        screen: pygame.Surface - экран, на котором будут отрисованы частицы
        particles: tuple[Particle] - кортеж частиц
        area: Rectangle - область для проверки частиц на вхождение
        tree_visible: bool - флаг видимости дерева
        area_visible: bool - флаг видимости области

    """
    quadtree = QuadTree(
        None, screen, Rectangle(0, 0, *screen.get_size()), 4, tree_visible
    )

    for particle in particles:
        particle.dynamic()
        quadtree.insert(particle)

    quadtree.handle_collisions()

    if area_visible:
        area.move(*pygame.mouse.get_pos())
        query = quadtree.query(area)
        for particle in query:
            particle.draw((255, 255, 0))
        area.draw(screen)


def main():
    """Основная функция программы: точка входа."""
    pygame.init()
    pygame.display.set_caption("Particles")

    screen = pygame.display.set_mode((MIN_WIDTH, MIN_HEIGHT), pygame.RESIZABLE)
    clock = pygame.time.Clock()
    menu = pygame_menu.Menu("Меню", MIN_WIDTH, MIN_HEIGHT,
                            theme=pygame_menu.themes.THEME_DARK)

    num = menu.add.text_input(
        "Количество частиц: ", 0, font_size=16,
        input_type=pygame_menu.locals.INPUT_INT, maxchar=3
    )
    size = create_range_slider(menu, "\nГраницы размеров частиц",
                               100, (1, 50))
    speed = create_range_slider(menu, "\nГраницы скоростей частиц",
                                251, (0, 250))

    tree_visible, area_visible = False, False
    area = Rectangle(0, 0, 0, 0, (255, 255, 0), 2)
    particles = tuple()

    run = True
    while run:

        screen.fill((0, 0, 0))
        events = pygame.event.get()

        if menu.is_enabled():
            menu.update(events)
            menu.draw(screen)
        else:
            draw_particles(screen, particles, area, tree_visible, area_visible)

        for event in events:
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.VIDEORESIZE:
                resize(menu, event.size)
            elif event.type == pygame.MOUSEBUTTONDOWN and area_visible:
                if event.button == 4:
                    area.resize(area.width + 1, area.height + 1)
                elif event.button == 5:
                    area.resize(area.width - 1, area.height - 1)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RETURN:
                    particles = create_particles(
                        screen, num.get_value(),
                        size.get_value(), speed.get_value()
                    )
                    pygame.display.set_mode(screen.get_size())
                    menu.disable()
                elif event.key == pygame.K_BACKSPACE:
                    tree_visible, area_visible = False, False
                    area.resize(0, 0)
                    pygame.display.set_mode(screen.get_size(),
                                            pygame.RESIZABLE)
                    menu.enable()
                elif not menu.is_enabled():
                    if event.key == pygame.K_t:
                        tree_visible = not tree_visible
                    elif event.key == pygame.K_a:
                        area_visible = not area_visible

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
