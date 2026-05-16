class Zone:
    def __init__(self, name, coords, metadata):
        self.name = name
        self.coords = coords
        self.metadata = metadata

    def get_cost(self):
        zone_type = self.metadata.get("zone")

        if zone_type == "restricted":
            return 2

        if zone_type == "blocked":
            return float("inf")

        return 1

    def get_capacity(self):
        return self.metadata.get("max_drones", 1)
