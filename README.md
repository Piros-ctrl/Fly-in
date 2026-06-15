*This project has been created as part of the 42 curriculum by *oabderra*.*

# Fly-in

## Description

Fly-in is a drone routing and traffic management simulator developed as part of the 42 curriculum. The project models an airspace as a graph where zones represent locations and connections represent valid drone routes.

The goal is to route multiple drones from a common start zone to a destination zone while respecting capacity constraints, avoiding congestion, and handling restricted areas that may require multiple turns to traverse.

The simulator combines pathfinding, conflict resolution, and capacity management to coordinate drone movement efficiently. A graphical visualization is also provided to allow users to observe the simulation turn by turn.

## Features

* Graph-based route network
* Multiple drones moving simultaneously
* A* pathfinding algorithm
* Zone occupancy management
* Connection capacity management
* Dynamic rerouting when paths become congested
* Support for restricted zones with traversal costs
* Turn-based simulation
* Interactive graphical visualization using Tkinter
* Capacity information display mode

## Instructions

### Requirements

* Python 3
* Tkinter

### Run the simulation

```bash
make run
```

This command runs the simulator using the default map defined in the Makefile.

### Run a specific map

```bash
make run MAP=<map_file>
```

Example:

```bash
make run MAP=maps/easy/02_simple_fork.txt
```

### Debug Mode

```bash
make debug
```

Runs the project with Python's debugger.

### Linting

Standard linting:

```bash
make lint
```

Strict linting:

```bash
make lint-strict
```

### Clean Cache Files

```bash
make clean
```

### Graphical Visualization

The simulation can be launched with the visualization window enabled.

Controls:

* **Right Arrow** → Execute the next simulation turn
* **Enter** → Close the visualization window

## Algorithm and Implementation Strategy

### Graph Construction

The simulator parses a map file and constructs a graph composed of:

* Zones (nodes)
* Connections (edges)

Each zone stores:

* Coordinates
* Capacity
* Traversal cost
* Optional metadata such as display color

Each connection stores:

* Connected zones
* Maximum edge capacity

### Pathfinding

Fly-in uses the A* search algorithm to compute routes from the start zone to the destination zone.

The heuristic is based on Euclidean distance between zone coordinates, allowing efficient route computation while reducing the search space compared to uninformed algorithms.

### Capacity Management

The simulator tracks:

* Current occupancy of each zone
* Maximum capacity of each zone
* Current usage of each connection
* Maximum capacity of each connection

Before a drone enters a zone, the simulator verifies that the destination capacity is not exceeded.

The destination zone is treated as a special case and can accommodate all drones.

### Conflict Resolution

When multiple drones attempt to access the same limited resource:

1. Zone capacity is verified.
2. Edge capacity is verified.
3. Drones unable to move through their preferred route evaluate alternative neighbors.
4. A new path to the destination is computed when a valid alternative exists.

This mechanism prevents collisions and congestion while maintaining efficient drone flow.

### Restricted Zones

Some zones require multiple turns to traverse.

When entering a restricted zone:

* The drone enters a transit state.
* The traversal consumes several turns.
* Occupancy updates are delayed until traversal is completed.

This accurately models traversal delays while preserving capacity constraints.

## Visual Representation

The project includes an interactive Tkinter-based visualization designed to improve understanding of the simulation.

### Displayed Elements

* Zones displayed as nodes
* Connections displayed as edges
* Drones displayed as numbered markers
* Zone colors representing different zone types
* Turn counter showing simulation progress

### User Experience Benefits

The visualization helps users:

* Follow drone movement in real time
* Understand route selection decisions
* Observe congestion and rerouting behavior
* Verify capacity constraints visually
* Debug and validate simulation logic more easily

### Controls

| Key         | Action                      |
| ----------- | --------------------------- |
| Right Arrow | Advance one simulation turn |
| Enter       | Exit the visualization      |

## Resources

### Documentation

* meduim
* youtube videos
* peers

### AI Usage

Artificial intelligence tools were used during development for:

* Algorithm discussions
* Documentation drafting

All implementation, testing, validation, and final design decisions were performed by the project authors.
