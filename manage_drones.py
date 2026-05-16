from graph_generation import Graph
from a_star_algorithme import AStar
from creat_drone import Drone


class DroneSimulation:
    def __init__(self, config):
        self.config = config

        self.graph = Graph(config)
        self.pathfinder = AStar(self.graph)

        self.start = "start"
        self.goal = "goal"

        self.nb_drones = config["nb_drones"]

        self.drones = []
        self.turns = 0
        self.finished = 0

        self.occupancy = {}
        self.capacity = {}

        self.initialize_capacities()
        self.initialize_occupancy()
        self.initialize_drones()

    def initialize_capacities(self):
        for zone_name, zone in self.graph.zones.items():
            self.capacity[zone_name] = zone.get_capacity()

        self.capacity[self.goal] = self.nb_drones

    def initialize_occupancy(self):
        for zone_name in self.graph.zones:
            self.occupancy[zone_name] = 0

    def initialize_drones(self):
        start_path = self.pathfinder.search(self.start)

        for drone_id in range(self.nb_drones):
            drone = Drone(
                drone_id,
                self.start,
                start_path
            )

            self.drones.append(drone)

        self.occupancy[self.start] = self.nb_drones

    def move_drone(self, drone, next_node, edge_usage):
        edge = (drone.position, next_node)

        edge_capacity = self.graph.get_edge_capacity(edge)
        used = edge_usage.get(edge, 0)

        if (
            self.occupancy[next_node] < self.capacity[next_node]
            and
            used < edge_capacity
        ):
            self.occupancy[drone.position] -= 1
            self.occupancy[next_node] += 1

            edge_usage[edge] = used + 1

            drone.move_to(next_node)
            drone.advance_path()

            return True

        return False

    def reroute_drone(self, drone):
        neighbors = self.graph.get_neighbors(drone.position)

        available_neighbors = []

        for neighbor in neighbors:
            if (
                self.occupancy[neighbor] < self.capacity[neighbor]
                and
                neighbor != drone.next_node()
            ):
                available_neighbors.append(neighbor)

        if not available_neighbors:
            return

        best_neighbor = min(
            available_neighbors,
            key=lambda node: self.occupancy[node]
        )

        self.occupancy[drone.position] -= 1
        self.occupancy[best_neighbor] += 1

        drone.move_to(best_neighbor)

        new_path = self.pathfinder.search(best_neighbor)

        if new_path:
            drone.set_new_path(new_path)

    def update_drone(self, drone, edge_usage):
        if drone.finished:
            return

        next_node = drone.next_node()

        moved = self.move_drone(
            drone,
            next_node,
            edge_usage
        )

        if not moved:
            self.reroute_drone(drone)

        if drone.position == self.goal:
            drone.finished = True
            self.finished += 1

    def run(self):
        while self.finished < self.nb_drones:
            self.turns += 1

            edge_usage = {}

            for drone in self.drones:
                self.update_drone(drone, edge_usage)

        print(f"number of turns : {self.turns}")
