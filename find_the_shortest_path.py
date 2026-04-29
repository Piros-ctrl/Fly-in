import heapq
from math import sqrt


def calculate_estimate_distance(current_node, goal_node):
    current_x, current_y = current_node
    goal_x, goal_y = goal_node
    return sqrt((current_x - goal_x)**2+(current_y - goal_y)**2)

def calculate_g_cost(zone, neighbor, parsed_config, g_costs):
    if "zone" in parsed_config[neighbor]["metadata"]:
        if parsed_config[neighbor]["metadata"]["zone"] == "restricted":
            truns_number = 2
        if parsed_config[neighbor]["metadata"]["zone"] == "priority":
            truns_number = 1
        if parsed_config[neighbor]["metadata"]["zone"] == "blocked":
            truns_number = float('inf')
    else:
        truns_number = 1

    tentative_g = g_costs[zone] + truns_number

    updated = False
    if tentative_g < g_costs[neighbor]:
        g_costs[neighbor] = tentative_g
        updated = True

    return tentative_g, updated


def initialize_g_costs(nodes_dict):
    g_costs = {node: float('inf') for node in nodes_dict}
    g_costs["start"] = 0
    return g_costs


def translate_path(come_from):
    path = ["goal"]
    current = come_from["goal"]
    while current != "start":
        current = come_from[current]
        path.append(current)
    path.reverse()
    return path


def calculate_shortest_path(parsed_config):
    connections = parsed_config["connections"]
    nodes_dict  = {}
    open_list = []
    come_from = {}

    for key, value in parsed_config.items():
        if isinstance(value, dict) and "coords" in value:
            nodes_dict[key] = value

    g_costs = initialize_g_costs(nodes_dict)
    goal_coords = parsed_config["goal"]["coords"]
    start_coords = parsed_config["start"]["coords"]
    start_h = calculate_estimate_distance(start_coords, goal_coords)
    heapq.heappush(open_list, (start_h, "start"))
    
    visited = set()
    
    while open_list:
        content_f, zone = heapq.heappop(open_list)

        if zone == "goal":
            return translate_path(come_from)

        if zone in visited:
            continue
        visited.add(zone)

        neighbors = []
        for connection in connections:
            if zone in connection["pair"]:
                possible_neighb1, possible_neighb2 = connection["pair"]
                neighbors.append(
                    possible_neighb2 if possible_neighb1 == zone else possible_neighb1
                    )

        for neighbor in neighbors:
            if neighbor in visited:
                pass
        tentative_g, updated = calculate_g_cost(
            zone, neighbor, parsed_config, g_costs
            )
        if updated:
            come_from[neighbor] = zone
            neighbor_coords = parsed_config[neighbor]["coords"]
            h = calculate_estimate_distance(neighbor_coords, goal_coords)
            f = tentative_g + h
            heapq.heappush(open_list, (f, neighbor))
    return []
