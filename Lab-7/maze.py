"""Модуль генерации лабиринта.

Импорты:
    from random import ... - для случайной генерации

Функции:
    _initialize - инициализировать лабиринт
    _third_step - третий шаг генерации
    _fourth_step - четвертый шаг генерации
    generate - сгенерировать лабиринт

"""
from random import randint


def _initialize(maze: list, width: int, height: int):
    """Инициализировать лабиринт.

    Аргументы:
        maze: list - список, в который будет сгенерирован лабиринт
        width: int - ширина лабиринта
        height: int - высота лабиринта

    Является генертором, который возвращает
    поэтапное генерироване лабиринта

    """
    for i in range(height):
        maze.append([])
        index = len(maze) - 1
        for j in range(width):
            if (i % 2 and not j % 2 and j and j != width - 1) \
                    or (j % 2 and not i % 2 and i and i != height - 1) \
                        or (i % 2 and j % 2):
                maze[index] += [1]
            else:
                maze[index] += [0]
            yield maze


def _third_step(row: int, width: int,
                maze: list[list[int]], row_set: list[int]):
    """Третий шаг генерации.

    Аргументы:
        row: int - индекс текущей генерируемой строки
        width: int - ширина лабиринта
        maze: list[list[int]] - текущий лабиринт
        row_set: list[int] - распределение текущей строки по множествам

    Является генертором, который возвращает
    поэтапное генерироване лабиринта

    """
    for j in range(width - 1):
        right_border = randint(0, 1)
        if right_border or row_set[j] == row_set[j + 1]:
            maze[row * 2 + 1][j * 2 + 2] = 0
            yield maze
        else:
            change_set = row_set[j + 1]
            for k in range(width):
                if row_set[k] == change_set:
                    row_set[k] = row_set[j]


def _fourth_step(row: int, width: int, height: int,
                 maze: list[list[int]], row_set: list[int]):
    """Четвертый шаг генерации.

    Аргументы:
        row: int - индекс текущей генерируемой строки
        width: int - ширина лабиринта
        height: int - высота лабиринта
        maze: list[list[int]] - текущий лабиринт
        row_set: list[int] - распределение текущей строки по множествам

    Является генертором, который возвращает
    поэтапное генерироване лабиринта

    """
    for j in range(width):
        bottom_border = randint(0, 1)
        current_set_count = row_set.count(row_set[j])
        if bottom_border and current_set_count != 1:
            maze[row * 2 + 2][j * 2 + 1] = 0
            yield maze
    if row != height - 1:
        for j in range(width):
            bottom_hole = 0
            for k in range(width):
                if row_set[j] == row_set[k] \
                        and maze[row * 2 + 2][k * 2 + 1] == 1:
                    bottom_hole += 1
            if not bottom_hole:
                maze[row * 2 + 2][j * 2 + 1] = 1
                yield maze


def generate(width: int, height: int):
    """Сгенерировать лабиринт.

    Аргументы:
        width: int - ширина лабиринта
        height: int - высота лабиринта

    Является генертором, который возвращает
    поэтапное генерироване лабиринта

    """
    maze = []
    total_height = height * 2 + 1
    yield from _initialize(maze, width * 2 + 1, total_height)
    row_set = [0 for _ in range(width)]
    set_count = 1
    for i in range(height):
        for j in range(width):
            if not row_set[j]:
                row_set[j] = set_count
                set_count += 1
        yield from _third_step(i, width, maze, row_set)
        yield from _fourth_step(i, width, height, maze, row_set)
        if i != height - 1:
            for j in range(width):
                if maze[i * 2 + 2][j * 2 + 1] == 0:
                    row_set[j] = 0
    for j in range(width - 1):
        if row_set[j] != row_set[j + 1]:
            maze[total_height - 2][j * 2 + 2] = 1
            yield maze
