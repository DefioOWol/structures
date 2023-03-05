"""Тесты для модулей maze и jump_point_search."""
from unittest import TestCase
from unittest.mock import patch

from maze import generate
from jump_point_search import jump_point_search


MAZE = [
    [
     1, 1, 0,

     [[0, 0, 0],
      [0, 1, 0],
      [0, 0, 0]],

     [[0, 0, 0],
      [0, 1, 0],
      [0, 0, 0]]
    ],
    [
     2, 2, 0,

     [[0, 0, 0, 0, 0],
      [0, 1, 1, 1, 0],
      [0, 1, 0, 1, 0],
      [0, 1, 1, 1, 0],
      [0, 0, 0, 0, 0]],

     [[0, 0, 0, 0, 0],
      [0, 1, 1, 1, 0],
      [0, 1, 0, 1, 0],
      [0, 1, 0, 1, 0],
      [0, 0, 0, 0, 0]],
    ],
    [
     2, 2, 1,

     [[0, 0, 0, 0, 0],
      [0, 1, 1, 1, 0],
      [0, 0, 0, 0, 0],
      [0, 1, 0, 1, 0],
      [0, 0, 0, 0, 0]],

     [[0, 0, 0, 0, 0],
      [0, 1, 0, 1, 0],
      [0, 1, 0, 1, 0],
      [0, 1, 1, 1, 0],
      [0, 0, 0, 0, 0]],
    ],
    [
     2, 2, 0,

     [[0, 0, 0, 0, 0],
      [0, 1, 1, 1, 0],
      [0, 0, 0, 0, 0],
      [0, 1, 1, 1, 0],
      [0, 0, 0, 0, 0]],

     [[0, 0, 0, 0, 0],
      [0, 1, 1, 1, 0],
      [0, 1, 0, 0, 0],
      [0, 1, 1, 1, 0],
      [0, 0, 0, 0, 0]],
    ],
    [
     3, 3, 1,

     [[0, 0, 0, 0, 0, 0, 0],
      [0, 1, 1, 1, 1, 1, 0],
      [0, 1, 0, 1, 0, 1, 0],
      [0, 1, 1, 1, 1, 1, 0],
      [0, 1, 0, 1, 0, 1, 0],
      [0, 1, 1, 1, 1, 1, 0],
      [0, 0, 0, 0, 0, 0, 0]],

     [[0, 0, 0, 0, 0, 0, 0],
      [0, 1, 0, 1, 0, 1, 0],
      [0, 1, 0, 1, 0, 1, 0],
      [0, 1, 0, 1, 0, 1, 0],
      [0, 1, 0, 1, 0, 1, 0],
      [0, 1, 1, 1, 1, 1, 0],
      [0, 0, 0, 0, 0, 0, 0]],
    ],
    [
     3, 3, 0,

     [[0, 0, 0, 0, 0, 0, 0],
      [0, 1, 1, 1, 1, 1, 0],
      [0, 1, 0, 1, 0, 1, 0],
      [0, 1, 1, 1, 1, 1, 0],
      [0, 1, 0, 1, 0, 1, 0],
      [0, 1, 1, 1, 1, 1, 0],
      [0, 0, 0, 0, 0, 0, 0]],

     [[0, 0, 0, 0, 0, 0, 0],
      [0, 1, 1, 1, 1, 1, 0],
      [0, 1, 0, 1, 0, 1, 0],
      [0, 1, 0, 1, 0, 1, 0],
      [0, 1, 0, 1, 0, 1, 0],
      [0, 1, 0, 1, 0, 1, 0],
      [0, 0, 0, 0, 0, 0, 0]],
    ],
    [
     3, 3, 1,

     [[0, 0, 0, 0, 0, 0, 0],
      [0, 1, 0, 1, 0, 1, 0],
      [0, 0, 0, 0, 0, 0, 0],
      [0, 1, 0, 1, 0, 1, 0],
      [0, 0, 0, 0, 0, 0, 0],
      [0, 1, 0, 1, 0, 1, 0],
      [0, 0, 0, 0, 0, 0, 0]],

     [[0, 0, 0, 0, 0, 0, 0],
      [0, 1, 0, 1, 0, 1, 0],
      [0, 1, 0, 1, 0, 1, 0],
      [0, 1, 0, 1, 0, 1, 0],
      [0, 1, 0, 1, 0, 1, 0],
      [0, 1, 1, 1, 1, 1, 0],
      [0, 0, 0, 0, 0, 0, 0]],
    ],
    [
     3, 3, 0,

     [[0, 0, 0, 0, 0, 0, 0],
      [0, 1, 1, 1, 1, 1, 0],
      [0, 0, 0, 0, 0, 0, 0],
      [0, 1, 1, 1, 1, 1, 0],
      [0, 0, 0, 0, 0, 0, 0],
      [0, 1, 1, 1, 1, 1, 0],
      [0, 0, 0, 0, 0, 0, 0]],

     [[0, 0, 0, 0, 0, 0, 0],
      [0, 1, 1, 1, 1, 1, 0],
      [0, 1, 0, 0, 0, 0, 0],
      [0, 1, 1, 1, 1, 1, 0],
      [0, 1, 0, 0, 0, 0, 0],
      [0, 1, 1, 1, 1, 1, 0],
      [0, 0, 0, 0, 0, 0, 0]],
    ]
]


SOLVE = [
    [
     [[1, 1, 1],
      [1, 1, 1],
      [1, 1, 1]],
     (0, 0), (2, 2),
     ((0, 0), (1, 1), (2, 2))
    ],
    [
     [[1, 1, 1],
      [1, 0, 1],
      [1, 1, 1]],
     (0, 0), (2, 2),
     ((0, 0), (0, 1), (1, 2), (2, 2))
    ],
    [
     [[1, 1, 1],
      [1, 0, 1],
      [1, 0, 1]],
     (0, 0), (2, 2),
     ((0, 0), (1, 0), (2, 1), (2, 2))
    ],
    [
     [[1, 1, 1],
      [1, 0, 1],
      [1, 1, 1]],
     (0, 1), (2, 1),
     ((0, 1), (1, 0), (2, 1))
    ],
    [
     [[1, 1, 1],
      [1, 1, 0],
      [1, 0, 1]],
     (0, 0), (2, 2),
     ((2, 2),)
    ],
    [
     [[1, 1, 1],
      [1, 0, 0],
      [1, 0, 1]],
     (0, 0), (-1, 0),
     ((-1, 0),)
    ],
    [
     [[0, 0, 0, 0, 0, 0, 0],
      [0, 1, 1, 1, 1, 1, 0],
      [0, 1, 0, 0, 0, 0, 0],
      [0, 1, 1, 0, 1, 1, 0],
      [0, 0, 1, 0, 1, 0, 0],
      [0, 1, 1, 1, 1, 1, 0],
      [0, 0, 0, 0, 0, 0, 0],],
     (1, 1), (5, 5),
     ((1, 1), (1, 2), (2, 3), (2, 4), (3, 5), (4, 5), (5, 5))
    ],
    [
     [[0, 0, 0, 0, 0, 0, 0],
      [0, 1, 1, 1, 1, 1, 0],
      [0, 1, 0, 1, 1, 1, 0],
      [0, 1, 0, 1, 1, 1, 0],
      [0, 1, 0, 0, 0, 1, 0],
      [0, 1, 1, 1, 1, 1, 0],
      [0, 0, 0, 0, 0, 0, 0],],
     (1, 1), (5, 5),
     ((1, 1), (2, 1), (3, 2), (4, 3), (5, 4), (5, 5))
    ]
]


class TestMazeGeneration(TestCase):
    """Тест-кейс генерации лабиринта."""

    init = []

    @staticmethod
    def mock_initialize(maze: list, *_):
        """Мок инициализации лабиринта."""
        for row in TestMazeGeneration.init:
            maze.append(row)
        yield maze

    @patch("maze._initialize", mock_initialize)
    @patch("maze.randint")
    def test_generate_without_path(self, mock_rand):
        """Тест функции generate без проверки пути."""
        for width, height, rand, init, expected in MAZE:
            with self.subTest():
                TestMazeGeneration.init = init
                mock_rand.return_value = rand
                generator = generate(width, height)
                try:
                    while (maze := next(generator)):
                        pass
                except StopIteration:
                    self.assertEqual(maze, expected)

    def test_generate_with_path(self):
        """Тест функции generate с проверкой пути."""
        has_path = True
        for width in range(7):
            for height in range(7):
                maze_generator = generate(width, height)
                try:
                    while (maze := next(maze_generator)):
                        pass
                except StopIteration:
                    pass
                for i in range(height):
                    for j in range(width):
                        if not maze[i][j]:
                            continue
                        for k in range(height):
                            for l in range(width):
                                if not maze[k][l]:
                                    continue
                                solve_generator = jump_point_search(
                                    maze, (j, i), (l, k)
                                )
                                try:
                                    while (solve := next(solve_generator)):
                                        pass
                                except StopIteration:
                                    if (j, i) not in solve[1]:
                                        has_path = False
        self.assertTrue(has_path)


class TestJPS(TestCase):
    """Тест-кейс решения лабиринта с помощью JPS."""

    def test_jps(self):
        """Тест функции jump_point_search."""
        for maze, start, end, path in SOLVE:
            with self.subTest():
                generator = jump_point_search(maze, start, end)
                try:
                    while (solve := next(generator)):
                        pass
                except StopIteration:
                    self.assertEqual(solve[1][::-1], path)
