from sys import argv
from parser_1_2 import parse_file
from manage_drones import DroneSimulation


def main():
    try:
        config = argv[-1]
        x = parse_file(config)
        dron = DroneSimulation(x)
        dron.run()
    except BaseException as e:
        print(e)


main()
