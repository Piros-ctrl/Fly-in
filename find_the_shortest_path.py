# from test import parse_file
# from math import sqrt


# def calculate_estimate_distance(current_node, goal_node):
#     current_x, current_y = current_node
#     goal_x, goal_y = goal_node
#     return sqrt((current_x - goal_x)**2+(current_y - goal_y)**2)


# def calculate_shortest_path(parsed_config):
#     connections = parsed_config["connections"]
#     nodes_dict = {}
#     neighbors = []

#     for key, value in parsed_config.items():
#         if isinstance(value, dict) and "coords" in value:
#             nodes_dict[key] = value

#     for zone, drone_parametre in nodes_dict.items():
#         print(zone)
#         for connection in connections:
#             if zone in connection["pair"]:
#                 possible_n1, possible_n2 = connection["pair"]
#                 if possible_n1 == zone:
#                     neighbors.append(possible_n2)
#                 elif possible_n2 == zone:       # ← fixed condition
#                     neighbors.append(possible_n1)  # ← fixed append

#         for neighbor in neighbors:
#             neighb_coords = parsed_config[neighbor]["coords"]
#             goal_coords = parsed_config["goal"]["coords"]
#             h = calculate_estimate_distance(neighb_coords, goal_coords)
#             print(h)
#         neighbors = []
























from math import sqrt

def calculate_estimate_distance(current_node, goal_node):
    current_x, current_y = current_node
    goal_x, goal_y = goal_node
    return sqrt((current_x - goal_x)**2 + (current_y - goal_y)**2)


def calculate_g_cost(zone, neighbor, parsed_config, g_costs):
    """
    Calculate the g cost (actual cost from start to neighbor)
    
    Args:
        zone          : current node name (e.g. "start", "waypoint1")
        neighbor      : neighbor node name
        parsed_config : full config dict with coords
        g_costs       : dict tracking best known g cost for each node

    Returns:
        tentative_g   : new g cost to reach neighbor via zone
        updated       : True if a better path was found
    """
    current_coords  = parsed_config[zone]["coords"]
    neighbor_coords = parsed_config[neighbor]["coords"]

    edge_cost   = calculate_estimate_distance(current_coords, neighbor_coords)
    tentative_g = g_costs[zone] + edge_cost

    # only update if we found a cheaper path
    updated = False
    if tentative_g < g_costs[neighbor]:
        g_costs[neighbor] = tentative_g
        updated = True

    return tentative_g, updated


def initialize_g_costs(nodes_dict):
    """
    Initialize g costs — 0 for start, infinity for all others

    Args:
        nodes_dict : dict of all nodes extracted from parsed_config

    Returns:
        g_costs    : dict {node_name: g_cost}
    """
    g_costs = {node: float('inf') for node in nodes_dict}
    g_costs["start"] = 0
    return g_costs


def calculate_shortest_path(parsed_config):
    connections = parsed_config["connections"]
    nodes_dict  = {}

    for key, value in parsed_config.items():
        if isinstance(value, dict) and "coords" in value:
            nodes_dict[key] = value

    # initialize g costs
    g_costs = initialize_g_costs(nodes_dict)

    for zone in nodes_dict:
        neighbors = []
        for connection in connections:
            if zone in connection["pair"]:
                n1, n2 = connection["pair"]
                if n1 == zone:
                    neighbors.append(n2)
                elif n2 == zone:
                    neighbors.append(n1)

        print(f"{zone} | g={g_costs[zone]}")
        for neighbor in neighbors:
            tentative_g, updated = calculate_g_cost(zone, neighbor, parsed_config, g_costs)

            neighbor_coords = parsed_config[neighbor]["coords"]
            goal_coords     = parsed_config["goal"]["coords"]
            h = calculate_estimate_distance(neighbor_coords, goal_coords)
            f = tentative_g + h

            status = "✅ updated" if updated else "⏭️  skipped"
            print(f"  {neighbor} -> g={tentative_g:.1f}, h={h:.1f}, f={f:.1f} {status}")
        