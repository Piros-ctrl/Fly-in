from sys import argv
# from parser import parse_file
from test import parse_file


def main():
    try:    
        config = argv[-1]
        x = parse_file(config)
        print(x)
    except BaseException as e:
        print(e)

main()