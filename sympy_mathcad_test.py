#!/bin/env python3

from sympy_mathcad import parse_all

lines = """
pu = 3*newton + 20 * kilogram*meter/second^2
pu2 = 3*newton + 20 * kilogram*meter/second^2
gpt_size = 1*mile
gpt_k = 1*kilometer
gpt_size = ? kilometer
gpt_k = ? mile
pu = ? kilogram*meter/second^2
pu2 = ? newton
""";

parse_all(lines);
