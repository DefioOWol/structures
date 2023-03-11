"""Summary."""
from math import sqrt
from random import random

import numpy as np


ANTS = 1
AGES = 1
RHO = 0.1
ALPHA = 1
BETA = 1
PH_Q = 1
PH_MIN = 0.001
PH_MAX = 1
ELITE = 1


def _dist(first: tuple[int, int], second: tuple[int, int]):
    """Summary."""
    return sqrt((first[0] - second[0]) ** 2 + (first[1] - second[1]) ** 2)


def aco(vertexes: tuple[tuple[int, int]],
        start: int, end: int) -> tuple[tuple[int], int]:
    """Summary."""
    num = len(vertexes)
    dist = np.zeros((num, num))
    for i in range(num):
        for j in range(num):
            dist[i, j] = _dist(vertexes[i], vertexes[j])
    ph = np.ones((num, num)) * PH_MAX

    best_route = np.nan
    best_dist = np.inf

    vertexes_id = set(range(num)) - {end} | {start}
    available = len(vertexes_id)
    for _ in range(AGES):
        for _ in range(ANTS):

            visited = (start,)
            while len(visited) < available:

                unvisited = tuple(vertexes_id - set(visited))
                attract = (ph[visited[-1], unvisited] ** ALPHA
                           * dist[visited[-1], unvisited] ** -BETA)
                attract /= np.sum(attract)

                rand = random()
                for i in range(attract.size):
                    attract[i] = np.sum(attract[:i + 1])
                    if rand <= attract[i]:
                        next_vertex = unvisited[i]
                        break

                visited += (next_vertex,)

            visited += (end,)
            route_dist = sum([dist[visited[i], visited[i + 1]]
                              for i in range(available)])

            if route_dist < best_dist:
                best_route = visited
                best_dist = route_dist

            for i in range(available):
                ph[visited[i], visited[i + 1]] += (PH_Q / route_dist)

        for i in range(len(best_route) - 1):
            ph[best_route[i], best_route[i + 1]] += (PH_Q / best_dist * ELITE)

        ph = np.clip(ph, PH_MIN, PH_MAX) * (1 - RHO)

    return (best_route, best_dist)
