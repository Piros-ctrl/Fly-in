from graph_generation import Graph
from a_star_algorithme import AStar
from creat_drone import Drone
import sys


class DroneSimulation:
    def __init__(self, config: dict) -> None:
        self.config = config

        self.graph = Graph(config)
        self.pathfinder = AStar(self.graph)

        self.start: str = config["start_end"][0]
        self.goal: str = config["start_end"][1]

        self.nb_drones: int = config["nb_drones"]
        self.been_there = {}

        self.drones: list[Drone] = []
        self.turns: int = 0
        self.finished: int = 0

        self.occupancy: dict[str, int] = {}
        self.capacity: dict[str, int] = {}

        self.initialize_capacities()
        self.initialize_occupancy()
        self.initialize_drones()

    def initialize_capacities(self) -> None:
        for zone_name, zone in self.graph.zones.items():
            self.capacity[zone_name] = zone.get_capacity()

        self.capacity[self.goal] = self.nb_drones

    def initialize_occupancy(self) -> None:
        for zone_name in self.graph.zones:
            self.occupancy[zone_name] = 0
        self.occupancy[self.start] = self.nb_drones

    def initialize_drones(self) -> None:
        start_path = self.pathfinder.search(self.start, self.goal)

        if not start_path:
            print("No path found recheck you map")
            sys.exit()

        for drone_id in range(1, self.nb_drones + 1):
            drone = Drone(
                drone_id,
                self.start,
                start_path
            )
            self.drones.append(drone)

    def get_is_(self, drone):
        if self.been_there:
            for id, position in self.been_there.items():
                if drone.id == id and drone.position == position:
                    return 1

        self.been_there[drone.id] = drone.position
        return 2

    def move_drone(
        self,
        drone: Drone,
        next_node: str,
        edge_usage: dict[tuple[str, str], int]
            ) -> bool:
        edge = (drone.position, next_node)
        edge_capacity = self.graph.get_edge_capacity(edge)
        used = edge_usage.get(edge, 0)

        if self.occupancy[next_node] < self.capacity[next_node] and used < edge_capacity:

            if self.graph.get_zone(next_node).get_zone_type() == "restricted":
                cost = self.get_is_(drone)
            else:
                cost = 1

            edge_usage[edge] = used + 1

            if cost > 1:
                drone.turns_remaining = int(cost) - 1
                drone.res_zones.append(drone.position)
                self.occupancy[drone.position] -= 1
            else:
                if drone.position not in drone.res_zones:
                    self.occupancy[drone.position] -= 1
                drone.move_to(next_node)
                self.occupancy[drone.position] += 1
                drone.advance_path()

            return True

        return False

    def reroute_drone(
        self,
        drone: Drone,
        edge_usage: dict[tuple[str, str], int]
            ) -> bool | None:
        neighbors = self.graph.get_neighbors(drone.position)
        still_remaning = len(drone.path) - drone.path_index

        available_neighbors: list[str] = []

        for neighbor in neighbors:
            edge = (drone.position, neighbor)
            edge_capacity = self.graph.get_edge_capacity(edge)
            used = edge_usage.get(edge, 0)
            if (
                self.occupancy[neighbor] < self.capacity[neighbor]
                and neighbor != drone.next_node()
                and used < edge_capacity
            ):
                new_path = self.pathfinder.search(neighbor, self.goal)
                if new_path and len(new_path) <= still_remaning:
                    available_neighbors.append(neighbor)

        if not available_neighbors:
            return None

        best_neighbor = min(
            available_neighbors,
            key=lambda node: self.occupancy[node]
        )

        new_path = self.pathfinder.search(best_neighbor, self.goal)
        drone.set_new_path(new_path, drone.position)
        moved = self.move_drone(drone, best_neighbor, edge_usage)
        if moved:
            return True
        else:
            return False

    def update_drone(
        self,
        drone: Drone,
        edge_usage: dict[tuple[str, str], int]
            ) -> None:
        if drone.finished:
            return

        next_node = drone.next_node()

        moved = False
        if drone.is_in_transit():
            drone.turns_remaining -= 1
            if drone.turns_remaining == 0:
                moved = self.move_drone(drone, next_node, edge_usage)
                if not moved:
                    moved = self.reroute_drone(drone, edge_usage)
                if moved:
                    if drone.position != self.goal:
                        if self.graph.get_zone(drone.next_node()).get_zone_type() == "restricted":
                            print(f" D{drone.id}:{drone.position}-{drone.next_node()}", end="")
                        else:
                            print(f" D{drone.id}:{drone.next_node()}", end="")

                if drone.position == self.goal:
                    drone.finished = True
                    self.finished += 1
            return

        moved = self.move_drone(drone, next_node, edge_usage)
        if not moved:
            moved = self.reroute_drone(drone, edge_usage)

        if moved:
            if drone.position != self.goal:
                if self.graph.get_zone(drone.next_node()).get_zone_type() == "restricted":
                    print(f" D{drone.id}:{drone.position}-{drone.next_node()}", end="")
                else:
                    print(f" D{drone.id}:{drone.next_node()}", end="")
        if drone.position == self.goal:
            drone.finished = True
            self.finished += 1

    def run_one_turn(self) -> None:
        edge_usage: dict[tuple[str, str], int] = {}

        for drone in self.drones:
            self.update_drone(drone, edge_usage)
        print()

        self.turns += 1

    def run(self) -> None:
        while self.finished < self.nb_drones:
            self.run_one_turn()

        print(f"number of turns : {self.turns}")
