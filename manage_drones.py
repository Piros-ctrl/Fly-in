from graph_generation import Graph
from a_star_algorithme import AStar
from creat_drone import Drone
import sys


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
        self.occupancy[self.start] = self.nb_drones

    def initialize_drones(self):
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

    def move_drone(self, drone, next_node, edge_usage):
        edge = (drone.position, next_node)
        edge_capacity = self.graph.get_edge_capacity(edge)
        used = edge_usage.get(edge, 0)

        if (used < edge_capacity):
            cost = self.graph.get_zone(next_node).get_cost()

            edge_usage[edge] = used + 1

            self.occupancy[drone.position] -= 1

            drone.next_position = next_node

            if cost > 1:
                drone.turns_remaining = cost - 1
            else:
                self.occupancy[next_node] += 1
                drone.move_to(next_node)
                drone.advance_path()
                drone.next_position = None

            return True

        return False

    def reroute_drone(self, drone, edge_usage):
        neighbors = self.graph.get_neighbors(drone.position)
        still_remaning = len(drone.path) - drone.path_index

        available_neighbors = []

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
            return

        best_neighbor = min(
            available_neighbors,
            key=lambda node: self.occupancy[node]
        )

        new_path = self.pathfinder.search(best_neighbor, self.goal)

        drone.set_new_path(new_path, best_neighbor)
        moved = self.move_drone(drone, best_neighbor, edge_usage)
        if moved:
            return True

    def update_drone(self, drone, edge_usage):
        if drone.finished:
            return

        if drone.is_in_transit():
            drone.turns_remaining -= 1
            if drone.turns_remaining == 0:
                drone.move_to(drone.next_position)
                drone.advance_path()
                drone.next_position = None
                drone.in_edge = False

                if drone.position == self.goal:
                    drone.finished = True
                    self.finished += 1
            return

        next_node = drone.next_node()
        edge = (drone.position, next_node)
        edge_capacity = self.graph.get_edge_capacity(edge)
        used = edge_usage.get(edge, 0)

        can_move = (
            self.occupancy[next_node] < self.capacity[next_node]
            and used < edge_capacity
        )

        moved = False
        if can_move:
            moved = self.move_drone(drone, next_node, edge_usage)
        else:
            moved = self.reroute_drone(drone, edge_usage)

        if moved:
            print(f" D{drone.id}-{next_node}", end="")
        if drone.position == self.goal:
            drone.finished = True
            self.finished += 1

    def run_one_turn(self):
        edge_usage = {}

        for drone in self.drones:
            self.update_drone(drone, edge_usage)
        print()

        self.turns += 1

    def run(self):
        while self.finished < self.nb_drones:
            self.run_one_turn()

        print(f"number of turns : {self.turns}")
