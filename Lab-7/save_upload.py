"""Модуль сохранения и загрузки лабиринтов.

Импорты:
    from PIL import ... - для взаимодействия с изображениями
    from numpy import ... - для преобразования данных
    from PyQt5.QtWidgets import ... - для открытия и сохранения файлов

Функции:
    _save_txt - сохранить лабиринт в текстовом виде
    _save_image - сохранить лабиринт в виде изображения
    save_image - сохранить лабиринт
    _upload_txt - загрузить лабиринт из текстового формата
    _upload_image - загрузить лабиринт из изображения
    upload_maze - загрузить лабиринт

"""
from PIL import Image
from numpy import asarray, reshape
from PyQt5.QtWidgets import QApplication, QFileDialog


def _save_txt(opened_file, maze: list[list[int]]):
    """Сохранить лабиринт в текстовом виде.

    Аргументы:
        opened_file - открытый файл для записи
        maze: list[list[int]] - лабиринт

    """
    for row in maze:
        for cell in row:
            opened_file.write(str(cell))
        opened_file.write("\n")


def _save_image(path: str, maze: list[list[int]]):
    """Сохранить лабиринт в виде изображения.

    Аргументы:
        path: str - путь сохранения
        maze: list[list[int]] - лабиринт

    """
    array = asarray(maze)
    array[array == 1] = 255
    Image.fromarray(array).convert("RGB").save(
        path, subsampling=0, quality=100
    )


def save_maze(maze: list[list[int]], available: bool):
    """Сохранить лабиринт.

    Аргументы:
        maze: list[list[int]] - лабиринт
        available: bool - флаг доступности сохранения

    """
    if not available:
        return
    _ = QApplication([])
    fname, extension = QFileDialog.getSaveFileName(
        None, "Save maze", "D:/",
        "Images (*.jpg);;Images (*.png);;Text files (*.txt)"
    )
    if extension:
        if extension[0] == "T":
            with open(fname, "w", encoding="utf-8") as opened_file:
                _save_txt(opened_file, maze)
        else:
            _save_image(fname, maze)


def _upload_txt(opened_file, maze: list[list[int]]):
    """Загрузить лабиринт из текстового формата.

    Аргументы:
        opened_file - открытый файл для чтения
        maze: list[list[int]] - лабиринт

    """
    width, new_maze = -1, []
    while (line := opened_file.readline()):
        line = list(line) if line[-1] != "\n" else list(line[:-1])
        current_width = len(line)
        if not current_width:
            break
        if width == -1:
            width = current_width
        elif current_width != width:
            return
        if any(value not in ("0", "1") for value in line):
            return
        new_maze += [list(map(int, line))]
    maze.clear()
    for row in new_maze:
        maze.append(row)


def _upload_image(image: Image, maze: list[list[int]]):
    """Загрузить лабиринт из изображения.

    Аргументы:
        image: Image - считываемое изображение
        maze: list[list[int]] - лабиринт

    """
    components = len(image.getbands())
    array = asarray(image.getdata())
    array = [color.sum() // components for color in array]
    array = reshape(array, (-1, image.width))
    if array[(array >= 50) & (array <= 205)].size:
        return
    array[array < 50], array[array > 205] = 0, 1
    maze.clear()
    for row in array:
        maze.append(list(row))


def upload_maze(maze: list[list[int]]):
    """Загрузить лабиринт maze."""
    _ = QApplication([])
    fname, extension = QFileDialog.getOpenFileName(
        None, "Upload maze", "D:/",
        "Images (*.jpg *.png);;Text files (*.txt)"
    )
    if extension:
        if extension[0] == "T":
            with open(fname, "r", encoding="utf-8") as opened_file:
                _upload_txt(opened_file, maze)
        else:
            with Image.open(fname) as image:
                _upload_image(image, maze)
