#!/bin/env python3

lines = """
letter = Quantity("letter")`
word = Quantity("word")`
word.set_global_relative_scale_factor(5,letter)`
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
