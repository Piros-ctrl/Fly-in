from typing import Any
import heapq
from math import sqrt


class AStar:

    def __init__(self, graph: Any) -> None:
        self.graph = graph

    def heuristic(self, current_zone: str, goal_zone: str) -> float:
        current_x, current_y = self.graph.get_zone(current_zone).coords
        goal_x, goal_y = self.graph.get_zone(goal_zone).coords
        return sqrt(
            (current_x - goal_x) ** 2
            +
            (current_y - goal_y) ** 2
        )

    def initialize_costs(self) -> dict[str, float]:
        g_costs: dict[str, float] = {}
        for zone_name in self.graph.zones:
            g_costs[zone_name] = float("inf")
        return g_costs

    def reconstruct_path(
        self, came_from: dict[str, str], start: str, goal: str
            ) -> list[str]:
        current = goal
        path: list[str] = []
        while current != start:
            path.append(current)
            current = came_from[current]
        path.append(start)
        path.reverse()
        return path

    def search(self, start: str, goal: str) -> list[str]:
        open_list: list[tuple[float, int, str]] = []
        visited: set[str] = set()
        came_from: dict[str, str] = {}
        g_costs = self.initialize_costs()
        g_costs[start] = 0
        ref: int = 0
        start_h = self.heuristic(start, goal)
        heapq.heappush(open_list, (start_h, ref, start))

        while open_list:
            _, _, current_zone = heapq.heappop(open_list)

            if current_zone == goal:
                return self.reconstruct_path(came_from, start, goal)

            if current_zone in visited:
                continue
            visited.add(current_zone)

            neighbors = self.graph.get_neighbors(current_zone)
            for neighbor in neighbors:
                if neighbor in visited:
                    continue
                zone_cost = self.graph.get_zone(neighbor).get_cost()
                zone_extra_check = self.graph.get_zone(neighbor).get_priority()
                tentative_g = g_costs[current_zone] + zone_cost

                if tentative_g < g_costs[neighbor]:
                    g_costs[neighbor] = tentative_g
                    came_from[neighbor] = current_zone
                    h = self.heuristic(neighbor, goal)
                    f = tentative_g + h + zone_extra_check
                    ref += 1
                    heapq.heappush(open_list, (f, ref, neighbor))

        return []
