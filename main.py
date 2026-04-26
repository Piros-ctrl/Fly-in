from sys import argv
# from parser import parse_file
from test import parse_file
from find_the_shortest_path import calculate_shortest_path


def main():
    try:
        config = argv[-1]
        x = parse_file(config)
        calculate_shortest_path(x)
    except BaseException as e:
        print(e)


main()
