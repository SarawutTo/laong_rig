import math


def calculate_hypotenuse(a, b):
    return math.sqrt(a**2 + b**2)


def get_linear_base_distance(amount):
    dis = 1.00 / (amount - 1)
    return dis


def get_closest_section(value, section):
    for iy in range(len(section)):
        if section[iy] <= value < (iy + 1) * section[1]:
            return iy
