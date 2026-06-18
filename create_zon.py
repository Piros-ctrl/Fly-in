from typing import Any


class Zone:
    def __init__(
            self, name: str,
            coords: tuple[int, int],
            metadata: dict[str, Any]
            ) -> None:
        self.name = name
        self.coords = coords
        self.metadata = metadata

    def get_zone_type(self) -> str:
        return str(self.metadata.get("zone", "normal"))

    def get_cost(self) -> int | float:
        zone_type = self.get_zone_type()

        if zone_type == "restricted":
            return 2

        if zone_type == "blocked":
            return float("inf")

        return 1

    def get_priority(self) -> float:
        zone_type = self.get_zone_type()
        if zone_type == "priority":
            return -0.5
        return 0

    def get_capacity(self) -> int:
        return int(self.metadata.get("max_drones", 1))
