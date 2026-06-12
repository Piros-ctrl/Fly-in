from graph_generation import Graph
from a_star_algorithme import AStar
from creat_drone import Drone


class DroneSimulation:
    def __init__(self, config):
        self.config = config

        self.graph = Graph(config)
        self.pathfinder = AStar(self.graph)

        self.start = config["start_end"][0]
        self.goal = config["start_end"][1]

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
        start_path = self.pathfinder.search(self.start, self.goal)

        for drone_id in range(1, self.nb_drones + 1):
            drone = Drone(
                drone_id,
                self.start,
                start_path
            )

            self.drones.append(drone)

    def move_drone(self, drone, next_node, edge_usage):
        edge = (drone.position, next_node)
        edge_capacity = self.graph.get_edge_capacity(edge)
        used = edge_usage.get(edge, 0)

        if (
            self.occupancy[next_node] < self.capacity[next_node]
            and
            used < edge_capacity
        ):
            cost = self.graph.get_zone(next_node).get_cost()

            edge_usage[edge] = used + 1

            if not drone.in_edge:
                self.occupancy[drone.position] -= 1

            if cost > 1:
                drone.next_position = next_node
                drone.turns_remaining = 1
                drone.in_edge = True
            else:
                drone.in_edge = False
                self.occupancy[next_node] += 1
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
                new_path = self.pathfinder.search(neighbor, self.goal)
                if new_path:
                    available_neighbors.append(neighbor)

        if not available_neighbors:
            return

        best_neighbor = min(
            available_neighbors,
            key=lambda node: self.occupancy[node]
        )

        new_path = self.pathfinder.search(best_neighbor)

        self.occupancy[drone.position] -= 1
        self.occupancy[best_neighbor] += 1

        drone.move_to(best_neighbor)
        drone.set_new_path(new_path)

    def update_drone(self, drone, edge_usage):
        if drone.finished:
            return

        if drone.is_in_transit():
            drone.turns_remaining -= 1
            if drone.turns_remaining == 0:
                self.occupancy[drone.next_position] += 1
                drone.move_to(drone.next_position)
                drone.advance_path()
                drone.next_position = None
                drone.in_edge = False
            return

        next_node = drone.next_node()
        moved = self.move_drone(drone, next_node, edge_usage)

        if not moved:
            self.reroute_drone(drone)

        if drone.position == self.goal:
            drone.finished = True
            self.finished += 1

    def run_one_turn(self):
        edge_usage = {}

        for drone in self.drones:
            print(f" D{drone.id}-", end="")

            if drone.path[drone.path_index] == self.goal:
                print(self.goal, end="")
                continue
            else:
                print(f"{drone.path[drone.path_index + 1]}", end="")

            self.update_drone(drone, edge_usage)

        print()

        self.turns += 1

    def run(self):
        while self.finished < self.nb_drones:
            self.run_one_turn()

        print(f"number of turns : {self.turns}")
