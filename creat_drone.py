class Drone:
    def __init__(self, drone_id, start, path):
        self.id = drone_id
        self.position = start
        self.path = path
        self.path_index = 0
        self.finished = False

    def next_node(self):
        return self.path[self.path_index + 1]

    def move_to(self, zone_name):
        self.position = zone_name

    def advance_path(self):
        self.path_index += 1

    def set_new_path(self, path):
        self.path = path
        self.path_index = 0
