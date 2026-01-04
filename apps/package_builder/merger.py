# main.py
from data_loader import *
from packages_builder import *
from score_algorithms import *
def main():
    packet = get_full_packet()
    package = build_package(packet)
    #print(package)
    for site in package:
        print(f"{site["type"]}: {site["id"]}")



if __name__ == "__main__":
    main()
