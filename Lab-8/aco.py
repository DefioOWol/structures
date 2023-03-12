"""Summary."""
from typing import Optional
from random import random

import numpy as np


def aco(dist: np.ndarray, start: int, end: int, salesman: bool=True,
        *, ants: int=1, ages: int=1, rho: float=0.1, a: float=1,
        b: float=1, q: float=1, ph_min: float=0.01, ph_max: float=1,
        elite: int=0) -> tuple[tuple[int], Optional[float]]:
    """Summary."""
    if salesman:
        run = lambda visited, available: len(visited) < available
    else:
        run = lambda visited, _: visited[-1] != end

    dist = np.where(np.isnan(dist), np.inf, dist)
    num = dist.shape[0]
    ph = np.ones((num, num)) * ph_max

    best_route, best_dist = tuple(), np.inf

    vertexes = set(range(num)) - {end if salesman else np.nan} | {start}
    available = len(vertexes)
    for _ in range(ages):

        ant_routes = ant_dists = tuple()
        for _ in range(ants):

            visited = (start,)
            while run(visited, available):

                unvisited = tuple(vertexes - set(visited))
                attract = (ph[visited[-1], unvisited] ** a
                           * (1 / dist[visited[-1], unvisited]) ** b)
                general = np.sum(attract)
                attract /= general if general else 1

                rand = random()
                for i in range(attract.size):
                    attract[i] = np.sum(attract[:i + 1])
                    if rand < attract[i]:
                        next_vertex = unvisited[i]
                        break
                else:
                    break

                visited += (next_vertex,)

            else:
                num = len(visited)
                visited += (end,)
                route_dist = sum([dist[visited[i], visited[i + 1]]
                                  for i in range(num)])
                ant_routes += (visited,)
                ant_dists += (route_dist,)

                if route_dist < best_dist:
                    best_route, best_dist = visited, route_dist

        ph *= (1 - rho)

        for i, route in enumerate(ant_routes):
            rel_q = (q / ant_dists[i]) if ant_dists[i] else np.inf
            for j in range(len(route) - 1):
                ph[route[j], route[j + 1]] += rel_q

        rel_q = (q / best_dist * elite) if best_dist else np.inf
        for i in range(len(best_route) - 1):
            ph[best_route[i], best_route[i + 1]] += rel_q

        ph = np.clip(ph, ph_min, ph_max)

    return (best_route if salesman else best_route[:-1],
            np.nan if np.isinf(best_dist) else best_dist)
