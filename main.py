from sys import argv
# from parser import parse_file
from test import parse_file
# from find_the_shortest_path import managing_drones
from manage_drones import DroneSimulation


def main():
    # try:
    config = argv[-1]
    x = parse_file(config)
    # managing_drones(x)
    dron = DroneSimulation(x)
    dron.run()
    # except BaseException as e:
    #     print(e)


main()
