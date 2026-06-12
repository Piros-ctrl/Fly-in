import tkinter as tk


class SimulationWindow(tk.Tk):
    def __init__(self, simulation):
        super().__init__()

        self.simulation = simulation

        self.title("Drone Simulation")
        self.geometry("1920x1080")
        self.configure(bg="gray")

        tk.Label(
            self,
            text="Drone Routing Simulation",
            bg="#0f172a",
            fg="white",
            font=("Arial", 14, "bold"),
            pady=10
        ).pack(fill=tk.X)

        self.turn_label = tk.Label(
            self,
            text="Turn Number: 0",
            bg="#0f172a",
            fg="white",
            font=("Arial", 12, "bold")
        )
        self.turn_label.pack(fill=tk.X)

        self.canvas = tk.Canvas(self, bg="#111827", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.nodes = {}
        self.edges = []
        self.zone_color = {}

        self.load_data()
        self.compute_bounds()

        self.run()

    def load_data(self):
        for name, zone in self.simulation.graph.zones.items():
            x, y = zone.coords
            self.nodes[name] = (x * 120 + 100, y * 120 + 100)
            self.zone_color[name] = zone.metadata.get("color")

        for conn in self.simulation.graph.connections:
            self.edges.append(tuple(conn["pair"]))

    def compute_bounds(self):
        xs = [x for x, y in self.nodes.values()]
        ys = [y for x, y in self.nodes.values()]

        self.min_x, self.max_x = min(xs), max(xs)
        self.min_y, self.max_y = min(ys), max(ys)

    def to_screen(self, x, y):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        scale = min(
            w / (self.max_x - self.min_x + 1),
            h / (self.max_y - self.min_y + 1)
        ) * 0.90

        cx = (self.min_x + self.max_x) / 2
        cy = (self.min_y + self.max_y) / 2

        return (
            (x - cx) * scale + w / 2,
            (y - cy) * scale + h / 2
        )

    def run(self):
        if self.simulation.finished < self.simulation.nb_drones:
            self.simulation.run_one_turn()
            self.turn_label.config(
                text=f"Turn Number: {self.simulation.turns}"
            )

        self.draw()
        self.after(900, self.run)

    # ---------------- DRAW ----------------

    def draw(self):
        self.canvas.delete("all")

        # edges
        for a, b in self.edges:
            x1, y1 = self.to_screen(*self.nodes[a])
            x2, y2 = self.to_screen(*self.nodes[b])

            color = "#334155"
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=2)

        # nodes
        for name, (bx, by) in self.nodes.items():
            x, y = self.to_screen(bx, by)
            color = self.zone_color[name]
            if color.lower() == "rainbow":
                color = "aqua"

            r = 14
            self.canvas.create_oval(x-r, y-r, x+r, y+r,
                                    fill=color, outline="white")

            self.canvas.create_text(x, y + 20,
                                    text=name,
                                    fill="white",
                                    font=("Arial", 8))

        # drones
        for d in self.simulation.drones:
            x, y = self.to_screen(*self.nodes[d.position])

            self.canvas.create_oval(x-6, y-6, x+6, y+6,
                                    fill="cyan", outline="white")
            self.canvas.create_text(x, y,
                                    text=str(d.id),
                                    fill="black",
                                    font=("Arial", 7, "bold"))
