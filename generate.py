#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""generate.py

Script for generating a random but valid test case.

USAGE: ./generate.py [NUM] [-a 'L-U'] [-b 'L-U'] [-o FILENAME]
"""

import sys
from argparse import ArgumentParser
from random import randint
from typing import List, Tuple

__author__ = "Vincent Lin"

DESCRIPTION = (
    "Generate a random but valid test case. Output the arrival and burst "
    "times as a space-separate list of integers for easy copy-pasting into "
    "the input fields of the online solver: "
    "https://boonsuen.com/process-scheduling-solver."
)

parser = ArgumentParser(description=DESCRIPTION)
parser.add_argument("num",
                    help="positive number of entries in the test case",
                    metavar="NUM",
                    nargs="?",
                    type=int,
                    default=4)
parser.add_argument("-a", "--arrival-range",
                    help="non-negative integers as inclusive bounds for what "
                         "the arrival times can be",
                    metavar="'LOWER-UPPER'",
                    default="0-20")
parser.add_argument("-b", "--burst-range",
                    help="positive integers as inclusive bounds for what the "
                         "burst times can be",
                    metavar="'LOWER-UPPER'",
                    default="1-20")
parser.add_argument("-o", "--output",
                    help="save the test case as a valid input file for ./rr",
                    metavar="FILENAME")


def split_range_string(s: str) -> Tuple[int, int]:
    lower, upper = s.split("-")
    return (int(lower), int(upper))


def get_random_times(num: int, lower: int, upper: int) -> List[int]:
    return [randint(lower, upper) for _ in range(num)]


def to_txt_format(arrival_times: List[int], burst_times: List[int]) -> str:
    num_entries = len(arrival_times)
    content = str(num_entries)  # First line.

    zipped = zip(arrival_times, burst_times)
    for pid, (arrival_time, burst_time) in enumerate(zipped, start=1):
        content += f"\n{pid}, {arrival_time}, {burst_time}"

    content += "\n"
    return content


def main() -> None:
    """Main driver function."""
    namespace, _ = parser.parse_known_args()

    try:
        arrival_bounds = split_range_string(namespace.arrival_range)
        burst_bounds = split_range_string(namespace.burst_range)
    except Exception:
        sys.stderr.write(
            "Invalid format. "
            "Bounds string should be of the form 'LOWER-UPPER', "
            "where LOWER and UPPER are integers.\n"
        )
        sys.exit(22)

    arrival_lower, arrival_upper = arrival_bounds
    burst_lower, burst_upper = burst_bounds
    if arrival_lower > arrival_upper or burst_lower > burst_upper:
        sys.stderr.write("For bounds strings, UPPER should be >= LOWER.\n")
        sys.exit(22)

    num = namespace.num
    if num < 1:
        sys.stderr.write("Number of entries must be a positive number.\n")
        sys.exit(22)

    arrival_times = get_random_times(num, arrival_lower, arrival_upper)
    burst_times = get_random_times(num, burst_lower, burst_upper)

    print(f"Arrival times: {' '.join(str(time) for time in arrival_times)}")
    print(f"  Burst times: {' '.join(str(time) for time in burst_times)}")

    output_path = namespace.output
    if output_path is not None:
        content = to_txt_format(arrival_times, burst_times)
        with open(output_path, "wt", encoding="utf-8") as fp:
            fp.write(content)


if __name__ == "__main__":
    main()
