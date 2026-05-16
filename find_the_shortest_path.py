# import heapq
# from math import sqrt


# def calculate_estimate_distance(current_node, goal_node):
#     current_x, current_y = current_node
#     goal_x, goal_y = goal_node
#     return sqrt((current_x - goal_x)**2+(current_y - goal_y)**2)


# def zone_cost(neighbor, parsed_config):
#     zone_type = parsed_config[neighbor].get("metadata", {}).get("zone")
#     if zone_type == "restricted":
#         return 2
#     if zone_type == "blocked":
#         return float('inf')
#     return 1


# def calculate_g_cost(zone, neighbor, parsed_config, g_costs):
#     turns_number = zone_cost(neighbor, parsed_config)

#     tentative_g = g_costs[zone] + turns_number
#     updated = False
#     if tentative_g < g_costs[neighbor]:
#         g_costs[neighbor] = tentative_g
#         updated = True

#     return tentative_g, updated


# def initialize_g_costs(nodes_list):
#     g_costs = {node: float("inf") for node in nodes_list}
#     g_costs[nodes_list[0]] = 0
#     return g_costs


# def translate_path(come_from, start):
#     path = ["goal"]
#     current = come_from["goal"]
#     while current != start:
#         path.append(current)
#         current = come_from[current]
#     path.append(start)
#     path.reverse()
#     return path


# def get_neighbors(parsed_config, zone):
#     connections = parsed_config["connections"]
#     neighbors = []
#     for connection in connections:
#         if zone in connection["pair"]:
#             possible_neighb1, possible_neighb2 = connection["pair"]
#             neighbors.append(
#                 possible_neighb2 if possible_neighb1 == zone
#                 else possible_neighb1
#             )
#     return neighbors


# def a_star(parsed_config, start):
#     nodes = []
#     open_list = []
#     come_from = {}

#     for key, value in parsed_config.items():
#         if isinstance(value, dict):
#             nodes.append(key)

#     g_costs = initialize_g_costs(nodes)

#     goal_coords = parsed_config["goal"]["coords"]
#     start_coords = parsed_config[start]["coords"]
#     start_h = calculate_estimate_distance(start_coords, goal_coords)
#     ref = 0
#     heapq.heappush(open_list, (start_h, ref, start))

#     visited = set()

#     while open_list:
#         _, _, zone = heapq.heappop(open_list)

#         if zone == "goal":
#             return translate_path(come_from, start)

#         if zone in visited:
#             continue
#         visited.add(zone)

#         neighbors = get_neighbors(parsed_config, zone)

#         for neighbor in neighbors:
#             if neighbor in visited:
#                 continue
#             tentative_g, updated = calculate_g_cost(
#                 zone, neighbor, parsed_config, g_costs
#                 )
#             if updated:
#                 come_from[neighbor] = zone
#                 neighbor_coords = parsed_config[neighbor]["coords"]
#                 h = calculate_estimate_distance(neighbor_coords, goal_coords)
#                 f = tentative_g + h
#                 ref += 1
#                 heapq.heappush(open_list, (f, ref, neighbor))
#     return []


# def get_vertex_capacity(config):
#     vertex_capacity = {}
#     for name, data in config.items():
#         if isinstance(data, dict):
#             dr_num = data.get("metadata", {}).get("max_drones")
#             if "coords" in data and dr_num:
#                 vertex_capacity[name] = dr_num
#             elif "coords" in data:
#                 vertex_capacity[name] = 1
#     return vertex_capacity


# def get_edge_cap(connections, edge) -> int:
#     zone, next_zone = edge
#     for connection in connections:
#         x, y = connection["pair"]
#         if (x == zone and y == next_zone) or (x == next_zone and y == zone):
#             return connection.get('metadata', {}).get('max_link_capacity', 1)
#     return 1


# def managing_drones(parsed_config):
#     nb_drones = parsed_config["nb_drones"]

#     drones = []
#     occupancy = {node: 0 for node, value in parsed_config.items()
#                  if isinstance(value, dict)}
#     start = "start"
#     goal = "goal"

#     start_path = a_star(parsed_config, start)

#     for i in range(nb_drones):
#         drones.append({
#             "id": i,
#             "position": start,
#             "path": start_path,
#             "path_index": 0,
#             "finished": False
#         })

#     capacity = get_vertex_capacity(parsed_config)
#     occupancy[start] = nb_drones
#     capacity["goal"] = nb_drones
#     finished = 0
#     turns = 0
#     while finished < nb_drones:
#         edge_usage = {}
#         turns += 1
#         for drone in drones:
#             if drone["finished"]:
#                 continue
#             path = drone["path"]
#             idx = drone["path_index"]

#             next_node = path[idx + 1]

#             edge = (drone["position"], next_node)
#             edge_cap = get_edge_cap(parsed_config["connections"], edge)
#             used = edge_usage.get(edge, 0)

#             if (
#                 occupancy[next_node] < capacity[next_node]
#                 and used < edge_cap
#                     ):
#                 occupancy[drone["position"]] -= 1
#                 occupancy[next_node] += 1

#                 edge_usage[edge] = used + 1

#                 drone["position"] = next_node
#                 drone["path_index"] += 1
#             else:
#                 neighbors = get_neighbors(parsed_config, drone["position"])

#                 available = [n for n in neighbors
#                              if occupancy[n] < capacity[n]
#                              and n != drone["path"][drone["path_index"] + 1]]

#                 if available:
#                     best = min(available, key=lambda x: occupancy[x])
#                     occupancy[drone["position"]] -= 1
#                     occupancy[best] += 1
#                     drone["position"] = best
#                     new_path = a_star(parsed_config, best)
#                     if new_path:
#                         drone["path"] = new_path
#                         drone["path_index"] = 0

#             if drone["position"] == goal:
#                 drone["finished"] = True
#                 finished += 1
#                 continue

#     print(f"number of turns : {turns}")
