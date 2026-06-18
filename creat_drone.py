class Drone:
    def __init__(self, drone_id: int, start: str, path: list[str]) -> None:
        self.id = drone_id
        self.position = start
        self.path = path
        self.path_index = 0
        self.finished = False
        self.turns_remaining = 0

    def next_node(self) -> str:
        return self.path[self.path_index + 1]

    def is_in_transit(self) -> bool:
        return self.turns_remaining > 0

    def move_to(self, zone_name: str) -> None:
        self.position = zone_name

    def advance_path(self) -> None:
        self.path_index += 1

    def set_new_path(self, path: list[str], position: str) -> None:
        self.path = path
        self.path_index = 0
        self.position = position
