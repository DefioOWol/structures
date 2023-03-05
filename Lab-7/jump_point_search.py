"""Модуль решения лабиринта с помощью Jump Point Search.

Импорты:
    from typing import ... - для аннотации типов
    from math import ... - для определения направления перемещения

Функции:
    _passable - проверить на возможность перемещения
    _direction - определить направление перемещения
    _forced - найти принужденных соседей
    _prune - обрезать соседей
    _jump - произвести прыжок
    _identify_successors - определить приемников
    jump_point_search - решить лабиринт
    _restore_path - восстановить путь

"""
from typing import Optional
from math import copysign


def _passable(cx: int, cy: int, dx: int,
              dy: int, maze: list[list[int]]) -> bool:
    """Проверить на возможность перемещения.

    Аргументы:
        cx: int - текущая позиция по x
        cy: int - текущая позиция по y
        dx: int - направление перемещения по x
        dy: int - направление перемещения по y
        maze: list[list[int]] - лабиринт

    Возвращает результат проверки

    """
    nx, ny = cx + dx, cy + dy
    if nx < 0 or nx >= len(maze[0]) or ny < 0 or ny >= len(maze) \
            or not (maze[ny][nx] and (maze[cy][nx] or maze[ny][cx])):
        return False
    return True


def _direction(cx: int, cy: int, px: int, py: int) -> tuple[int]:
    """Определить направление перемещения.

    Аргументы:
        cx: int - текущая позиция по x
        cy: int - текущая позиция по y
        px: int - предыдущая позиция по x
        py: int - предыдущая позиция по y

    Возвращает направление перемещения в виде кортежа

    """
    return (int(copysign(1, cx - px)) if cx - px else 0,
            int(copysign(1, cy - py)) if cy - py else 0)


def _forced(cx: int, cy: int, dx: int, dy: int,
            maze: list[list[int]]) -> tuple[tuple[int]]:
    """Найти принужденных соседей.

    Аргументы:
        cx: int - текущая позиция по x
        cy: int - текущая позиция по y
        dx: int - направление перемещения по x
        dy: int - направление перемещения по y
        maze: list[list[int]] - лабиринт

    Возвращает кортеж с позициями найденных соседей

    """
    neighbours = tuple()
    if dx and dy:
        if _passable(cx, cy, -dx, dy, maze) and not maze[cy][cx - dx]:
            neighbours += ((cx - dx, cy + dy),)
        if _passable(cx, cy, dx, -dy, maze) and not maze[cy - dy][cx]:
            neighbours += ((cx + dx, cy - dy),)
    else:
        if not dx:
            if _passable(cx, cy, -1, dy, maze) and not maze[cy][cx - 1]:
                neighbours += ((cx - 1, cy + dy),)
            if _passable(cx, cy, 1, dy, maze) and not maze[cy][cx + 1]:
                neighbours += ((cx + 1, cy + dy),)
        else:
            if _passable(cx, cy, dx, -1, maze) and not maze[cy - 1][cx]:
                neighbours += ((cx + dx, cy - 1),)
            if _passable(cx, cy, dx, 1, maze) and not maze[cy + 1][cx]:
                neighbours += ((cx + dx, cy + 1),)
    return neighbours


def _prune(cx: int, cy: int, prev: Optional[tuple[int]],
           maze: list[list[int]]) -> tuple[tuple[int]]:
    """Обрезать соседей.

    Аргументы:
        cx: int - текущая позиция по x
        cy: int - текущая позиция по y
        prev: Optional[tuple[int]] - предыдущая позиция
        maze: list[list[int]] - лабиринт

    Возвращает кортеж с позициями соседей после обрезки

    """
    neighbours = tuple()

    if prev is None:
        for dx, dy in ((0, -1), (-1, 0), (-1, -1), (-1, 1),
                       (1, -1), (0, 1), (1, 0), (1, 1)):
            if _passable(cx, cy, dx, dy, maze):
                neighbours += ((cx + dx, cy + dy),)
        return neighbours

    dx, dy = _direction(cx, cy, *prev)
    neighbours += _forced(cx, cy, dx, dy, maze)

    if _passable(cx, cy, dx, dy, maze):
        neighbours += ((cx + dx, cy + dy),)
    if dx and dy:
        if _passable(cx, cy, 0, dy, maze):
            neighbours += ((cx, cy + dy),)
        if _passable(cx, cy, dx, 0, maze):
            neighbours += ((cx + dx, cy),)

    return neighbours


def _jump(cx: int, cy: int, dx: int, dy: int, end: tuple[int],
          maze: list[list[int]]) -> Optional[tuple[int]]:
    """Произвести прыжок.

    Аргументы:
        cx: int - текущая позиция по x
        cy: int - текущая позиция по y
        dx: int - направление перемещения по x
        dy: int - направление перемещения по y
        end: tuple[int] - конечная позиция
        maze: list[list[int]] - лабиринт

    Возвращает позицию для прыжка или None при ее отсутствии

    """
    if not _passable(cx, cy, dx, dy, maze):
        return None
    nx, ny = cx + dx, cy + dy
    if (nx, ny) == end or _forced(nx, ny, dx, dy, maze):
        return (nx, ny)
    if dx and dy:
        for dxi, dyi in ((dx, 0), (0, dy)):
            if _jump(nx, ny, dxi, dyi, end, maze) is not None:
                return (nx, ny)
    return _jump(nx, ny, dx, dy, end, maze)


def _identify_successors(
        cx: int, cy: int, prev: Optional[tuple[int]],
        end: tuple[int], maze: list[list[int]]
) -> tuple[tuple[int]]:
    """Определить приемников.

    Аргументы:
        cx: int - текущая позиция по x
        cy: int - текущая позиция по y
        prev: Optional[tuple[int]] - предыдущая позиция
        end: tuple[int] - конечная позиция
        maze: list[list[int]] - лабиринт

    Возвращает кортеж с позициями приемников

    """
    successors = tuple()
    neighbours = _prune(cx, cy, prev, maze)
    for nx, ny in neighbours:
        jump_point = _jump(cx, cy, nx - cx, ny - cy, end, maze)
        successors += ((jump_point,) if jump_point else tuple())
    return successors


def jump_point_search(maze: list[list[int]],
                      start: tuple[int], end: tuple[int]):
    """Решить лабиринт.

    Все точки имеют формат (x, y)

    Аргументы:
        maze: list[list[int]] - лабиринт
        start: tuple[int] - начальная точка
        end: tuple[int] - конечная точка

    Является генератором, который возвращает
    поэтапное решение лабиринта

    """
    points, queue, jumped = {start: None}, [start], tuple()

    while queue:

        current = queue.pop(0)
        jumped += (current,)
        if current == end:
            break
        yield (jumped, None)
        successors = _identify_successors(*current, points[current], end, maze)

        for successor in successors:
            if successor in jumped:
                continue
            if successor not in queue:
                points[successor] = current
                queue += [successor]

    yield from _restore_path(points, end, jumped)


def _restore_path(points: dict[Optional[tuple[int]]],
                  end: tuple[int], jumped: tuple[tuple[int]]):
    """Восстановить путь.

    Восстановление происходит с конца

    Аргументы:
        points: dict[Optional[tuple[int]]] - словарь перемещения по точкам:
            ключ - точка, значение - предыдущая точка, из которой
                переместились в ключ
        end: tuple[int] - конечная позиция
        jumped: tuple[tuple[int]] - кортеж посещенных точек

    Является генератором, который возвращает
    поэтапное восстановление пути

    """
    first, restored = end, (end,)
    yield (jumped, restored)

    while first in points:

        second = points[first]
        if second is None:
            break
        dx, dy = _direction(*second, *first)
        first = second

        while restored[-1] != second:
            restored += ((restored[-1][0] + dx, restored[-1][1] + dy),)
            yield (jumped, restored)
