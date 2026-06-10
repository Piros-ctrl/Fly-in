from create_zon import Zone


class Graph:
    def __init__(self, config):
        self.config = config
        self.zones = {}
        self.connections = config["connections"]
        self._load_zones()

    def _load_zones(self):
        for key, value in self.config.items():
            if isinstance(value, dict):
                self.zones[key] = Zone(
                    key,
                    value["coords"],
                    value.get("metadata", {})
                )

    def get_zone(self, name):
        return self.zones[name]

    def get_neighbors(self, zone_name):
        neighbors = []

        for connection in self.connections:
            zone1, zone2 = connection["pair"]

            if zone1 == zone_name:
                neighbors.append(zone2)
            elif zone2 == zone_name:
                neighbors.append(zone1)

        return neighbors

    def get_edge_capacity(self, edge):
        current_zone, next_zone = edge

        for connection in self.connections:
            zone1, zone2 = connection["pair"]

            if (
                (zone1 == current_zone and zone2 == next_zone)
                or
                (zone1 == next_zone and zone2 == current_zone)
            ):
                return connection.get(
                    "metadata",
                    {}
                ).get("max_link_capacity", 1)

        return 0
