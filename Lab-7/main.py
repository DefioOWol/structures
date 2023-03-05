"""Основной модуль программы.

Импорты:
    from typing import ... - для аннотации типов
    import pygame - для реализации анимации
    import pygame_menu - для реализации графического интерфейса
    from maze import ... - для генерации лабиринтов
    from jump_point_search import ... - для решения лабиринтов
    from save_upload import ... - для сохранения и загрузки лабиринтов

Константы:
    MIN_WIDTH - минимальная ширина окна
    MIN_HEIGHT - минимальная высота окна
    FPS - частота кадров

Функции:
    check_pos - проверить позицию клика
    create_range_slider - создать слайдер диапазона
    create_selector - создать селектор
    resize - изменить размер окна
    maze_generate - создать генератор лабиринта
    maze_solve - создать генератор решения
    click_upload - загрузить лабиринт
    draw_point - отрисовать точку
    draw_maze - отрисовать лабиринт
    draw_solve - отрисовать решение
    get_generator_data - получить данные из генератора
    main - точка входа

"""
from typing import Optional, Union

import pygame
import pygame_menu

from maze import generate
from jump_point_search import jump_point_search
from save_upload import save_maze, upload_maze


MIN_WIDTH = 150
MIN_HEIGHT = 220
FPS = 120


def check_pos(pos: tuple[int]) -> bool:
    """Проверить позицию клика pos."""
    return (0 <= pos[0] <= MIN_WIDTH) and (0 <= pos[1] <= MIN_HEIGHT)


def create_range_slider(menu: pygame_menu.Menu, text: str,
                        default: int, range_value: tuple[int]):
    """Создать слайдер диапазона.

    Аргументы:
        menu: pygame_menu.Menu - меню, в котором будет создан слайдер
        text: str - текст
        default: int - значение по умолчанию
        range_value: tuple[int] - диапазон

    Возвращает созданный слайдер

    """
    menu.add.label(text, font_size=8, margin=(0, 1))
    return menu.add.range_slider(
        "", default, range_value, 1, font_size=12, margin=(0, 8),
        slider_thickness=5, width=100, range_margin=(0, 0),
        value_format=lambda value: str(int(value))
    )


def create_selector(menu: pygame_menu.Menu, text: str,
                    values: list[tuple[str, int]]):
    """Создать селектор.

    Аргументы:
        menu: pygame_menu.Menu - меню, в котором будет создан селектор
        text: str - текст
        values: list[tuple[str, int]] - список значений

    Возвращает созданный селектор

    """
    menu.add.label(text, font_size=8, margin=(0, 1))
    return menu.add.selector("", values, font_size=7, margin=(0, 9))


def resize(menu: pygame_menu.Menu, size: tuple[float]):
    """Изменить размер окна с menu на size."""
    width = size[0] if size[0] > MIN_WIDTH else MIN_WIDTH
    height = size[1] if size[1] > MIN_HEIGHT else MIN_HEIGHT
    pygame.display.set_mode((width, height), pygame.RESIZABLE)
    menu._position = (0, 0)


def maze_generate(setup: list[Union[list[Optional[bool]], int, float]],
                  width: int, height: int):
    """Создать генератор лабиринта.

    Аргументы:
        setup: list[Union[list[Optional[bool]], int, float]] - настройки,
            отвечающие за генераторы и отрисовку
        width: int - ширина лабиринта
        height: int - высота лабиринта

    """
    setup[0] = [generate(round(width), round(height)), False]
    setup[1] = [None, None]
    setup[3] = setup[4] = 0


def maze_solve(setup: list[Union[list[Optional[bool]], int, float]],
               maze: list[list[int]]):
    """Создать генератор решения.

    Аргументы:
        setup: list[Union[list[Optional[bool]], int, float]] - настройки,
            отвечающие за генераторы и отрисовку
        maze: list[list[int]] - лабиринт

    """
    if setup[0][1]:
        setup[1] = [
            jump_point_search(maze, (1, 1), (len(maze[0]) - 2, len(maze) - 2)),
            False
        ]


def click_upload(setup: list[Union[list[Optional[bool]], int, float]],
                 maze: list[list[int]]):
    """Загрузить лабиринт.

    Аргументы:
        setup: list[Union[list[Optional[bool]], int, float]] - настройки,
            отвечающие за генераторы и отрисовку
        maze: list[list[int]] - список, куда будет загружен лабиринт

    """
    upload_maze(maze)
    setup[0] = [None, True]
    setup[1] = [None, None]
    setup[3] = setup[4] = 0


def draw_point(screen: pygame.Surface, x: int, y: int, offset: tuple[float],
               scale: int, color: tuple[int], radius: int=-1):
    """Отрисовать точку.

    Аргументы:
        screen: pygame.Surface - экран, на котором будет отрисована точка
        x: int - позиция по x
        y: int - позиция по y
        offset: tuple[float] - смещение отрисовки (dx, dy)
        scale: int - масштаб отрисовки
        color: tuple[int] - цвет
        radius: int - радиус скругления углов, по умочанию -1 (отсутствует)

    """
    pygame.draw.rect(
            screen, color,
            (offset[0] + x * scale, offset[1] + y * scale, scale, scale),
            border_radius=radius
        )


def draw_maze(screen: pygame.Surface, maze: list[list[int]],
              setup: list[Union[list[Optional[bool]], int, float]],
              offset: tuple[float]):
    """Отрисовать лабиринт.

    Аргументы:
        screen: pygame.Surface - экран, на котором будет отрисован лабиринт
        maze: list[list[int]] - лабиринт
        setup: list[Union[list[Optional[bool]], int, float]] - настройки,
            отвечающие за генераторы и отрисовку
        offset: tuple[float] - смещение отрисовки (dx, dy)

    """
    height = len(maze)
    for i in range(height):
        width = len(maze[i])
        for j in range(width):
            color = (0, 0, 0) if not maze[i][j] else (255, 255, 255)
            draw_point(screen, j, i, offset, setup[2], color)


def draw_solve(
        screen: pygame.Surface,
        solve: tuple[Optional[tuple[int]]],
        maze: list[list[int]],
        setup: list[Union[list[Optional[bool]], int, float]],
        offset: tuple[float]
):
    """Отрисовать решение.

    Аргументы:
        screen: pygame.Surface - экран, на котором будет отрисовано решение
        solve: tuple[Optional[tuple[int]]] - решение
        maze: list[list[int]] - лабиринт
        setup: list[Union[list[Optional[bool]], int, float]] - настройки,
            отвечающие за генераторы и отрисовку
        offset: tuple[float] - смещение отрисовки (dx, dy)

    """
    if setup[1][1] is None:
        return
    for x, y in solve[0]:
        draw_point(screen, x, y, offset, setup[2], (100, 100, 100))
    if solve[1] is not None:
        for x, y in solve[1]:
            draw_point(screen, x, y, offset, setup[2], (0, 255, 0))
    else:
        draw_point(screen, len(maze[0]) - 2, len(maze) - 2,
                   offset, setup[2], (0, 255, 0), 4)
    draw_point(screen, *solve[0][-1], offset, setup[2], (255, 0, 0), 4)


def get_generator_data(
        setup: list[Union[list[Optional[bool]], int, float]],
        generator_index: int, render_index: int
) -> Optional[list[list[int]]]:
    """Получить данные из генератора.

    Аргументы:
        setup: list[Union[list[Optional[bool]], int, float]] - настройки,
            отвечающие за генераторы и отрисовку
        generator_index: int - индекс генератора в setup
        render_index: int - индекс типа отрисовки:
            0 - мгновенно, 1 - поэтапно

    Возвращает полученные данные или None при их отсутствии

    """
    data = None
    try:
        data = next(setup[generator_index][0])
        if not render_index:
            while (data := next(setup[generator_index][0])):
                pass
    except StopIteration:
        setup[generator_index][1] = True
    return data


def main():
    """Основная функция программы: точка входа."""
    pygame.init()
    pygame.display.set_caption("Maze")

    screen = pygame.display.set_mode((MIN_WIDTH, MIN_HEIGHT), pygame.RESIZABLE)
    clock = pygame.time.Clock()

    theme = pygame_menu.Theme(background_color=(228, 100, 36),
                              title_background_color=(228, 100, 36),
                              widget_font=pygame_menu.font.FONT_8BIT,
                              title=False)
    menu = pygame_menu.Menu("", MIN_WIDTH, MIN_HEIGHT, theme=theme)

    setup = [[None, None], [None, None], 1, 0, 0]
    click_pos = solve = None
    maze = [[]]

    width = create_range_slider(menu, "Width", 10, (0, 200))
    height = create_range_slider(menu, "Height", 10, (0, 200))
    render = create_selector(menu, "Rendering",
                             [("Instant", 0), ("Stepwise", 1)])
    menu.add.button(
        "Generate",
        lambda: maze_generate(setup, width.get_value(), height.get_value()),
        font_size=8
    )
    menu.add.button("Solve", lambda: maze_solve(setup, maze),
                    font_size=8, margin=(0, 7))
    menu.add.button("Save", lambda: save_maze(maze, setup[0][1]), font_size=8)
    menu.add.button("Upload", lambda: click_upload(setup, maze), font_size=8)

    run = True
    while run:

        screen.fill((228, 100, 36))
        events = pygame.event.get()

        if setup[0][1] is False:
            result = get_generator_data(setup, 0, render.get_index())
            maze = result if result is not None else maze

        offset = (
            (screen.get_width() - len(maze[0]) * setup[2]) / 2 + setup[3],
            (screen.get_height() - len(maze) * setup[2]) / 2 + setup[4]
        )
        draw_maze(screen, maze, setup, offset)

        if setup[1][1] is False:
            result = get_generator_data(setup, 1, render.get_index())
            solve = result if result is not None else solve
        draw_solve(screen, solve, maze, setup, offset)

        if menu.is_enabled():
            menu.update(events)
            menu.draw(screen)

        for event in events:
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.VIDEORESIZE:
                resize(menu, event.size)
                setup[3] *= (event.size[0] / screen.get_width())
                setup[4] *= (event.size[1] / screen.get_height())
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_m:
                    menu._enabled = not menu._enabled
                if event.key == pygame.K_r:
                    setup[3] = setup[4] = 0
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not (check_pos(event.pos)
                                              and menu.is_enabled()):
                    click_pos = event.pos
                elif event.button == 4:
                    setup[2] += (1 if setup[2] < 20 else 0)
                elif event.button == 5:
                    setup[2] -= (1 if setup[2] > 1 else 0)
            elif click_pos and event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    click_pos = None

        if click_pos and pygame.mouse.get_pressed()[0]:
            setup[3] += (pygame.mouse.get_pos()[0] - click_pos[0])
            setup[4] += (pygame.mouse.get_pos()[1] - click_pos[1])
            click_pos = pygame.mouse.get_pos()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
