from sys import argv
from parser_1_2 import MapParser
from manage_drones import DroneSimulation
from visualisation import SimulationWindow


def main():
    # try:
    config = argv[-1]
    x = MapParser(config)
    dron = DroneSimulation(x.parse())
    sum = SimulationWindow(dron)
    sum.mainloop()
    dron.run()
    # except BaseException as e:
    #     print(e)


main()
