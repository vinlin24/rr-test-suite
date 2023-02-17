#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""solver.py

Script for calculating the average waiting time and average response
time given the copy-pasted text from the Gantt chart of the online
process scheduling solver
https://boonsuen.com/process-scheduling-solver.  The output format is
identical to what should be outputted by a correct rr.c implementation.

USAGE: `./solver.py FILENAME`, where FILENAME is the name of the file
into which you Ctrl+A and Ctrl+C Ctrl+V the contents of the webpage
after running the solver.
"""

import re
import sys
from dataclasses import dataclass
from typing import List, Set, Tuple

__author__ = "Vincent Lin"


@dataclass(init=False)
class ProcessTimes:
    """Convenience struct for bundling a process' relevant times."""
    arrival_time: int
    first_exec_time: int
    waiting_time: int


def is_round_robin(raw_text: str) -> bool:
    """
    Return whether the text shows that "Round-Robin, RR" was selected as
    the algorithm.
    """
    match = re.search(r"^Round-Robin, RR$", raw_text, re.MULTILINE)
    return match is not None


def get_num_processes(raw_text: str) -> int:
    """Extract the number of entries from copy-pasted text."""
    # Example line:
    # Average	5587 / 30 = 186.233	5284 / 30 = 176.133
    match = re.search(r"^Average\s+\d+ / (\d+).+$", raw_text, re.MULTILINE)
    if match is None:
        raise ValueError("Could not find Average table entry in string.")
    return int(match.group(1))


def extract_gantt_and_table(raw_text: str) -> Tuple[str, str]:
    """
    Parse the raw text gotten from copy-and-pasting the result of Ctrl+A
    selecting the entire web application after computing the solution
    for a given process set.  Return the segments corresponding to the
    Gantt Chart and output table respectively.
    """
    # Discard everything before and including the "Gantt Chart" <h2>
    match = re.search(r"^Gantt Chart$", raw_text, re.MULTILINE)
    if match is None:
        raise ValueError("Could not find Gantt Chart header in string.")
    raw_text = raw_text[match.end()+1:]

    # Discard everthing after and including the "Average" <td>
    match = re.search(r"^Average.+$", raw_text, re.MULTILINE)
    if match is None:
        raise ValueError("Could not find Average table entry in string")
    raw_text = raw_text[:match.start()]

    # Find the table header within the input to serve as the divider
    match = re.search(r"^Job.+$", raw_text, re.MULTILINE)
    if match is None:
        raise ValueError("Could not find table header in string.")

    # Separate the Gantt Chart and table part of the input
    header_start, header_end = match.span()
    gantt_chart = raw_text[:header_start]
    table_string = raw_text[header_end+1:]

    return (gantt_chart, table_string)


def parse_gantt_chart(gantt_chart: str, num_entries: int
                      ) -> Tuple[List[str], List[int]]:
    gantt_tokens = gantt_chart.splitlines()

    pids: List[str] = []
    times: List[int] = []

    # The PIDs become numbers starting from 10, 11, ... after Z
    numeric_pids: Set[str] = set()
    for offset in range(num_entries - 26):
        numeric_pids.add(str(10 + offset))

    # Determine which token is a PID and which is a time
    for token in gantt_tokens:
        # Ambiguous, some tricks are needed

        if token in numeric_pids:
            # If we're already past its value in time, then this token
            # can't be a time.
            if times and times[-1] >= int(token):
                pids.append(token)

        # Obvious cases

        # The "PID" is "_" for slots where no process is executing
        elif token == "_":
            # TODO: Somehow discard the start time for _...
            pass
        elif token.isalpha():
            pids.append(token)
        elif token.isnumeric():
            time = int(token)
            # Times can repeat if the chart wraps around, but we need to
            # make sure there are no duplicates.
            if not times or times[-1] != time:
                times.append(time)
        else:
            raise ValueError(
                f"Invalid token found while parsing Gantt Chart: {token!r}.")


    return (pids, times)


def get_process_times(pids: List[str], times: List[int], table_string: str
                      ) -> Tuple[ProcessTimes]:
    """
    Given the parsed PIDs and times from the Gantt chart, parse the
    output table to extract and return a collection of (arrival time,
    first execution time, waiting time) bundles for every process.
    """
    times_mapping = {pid: ProcessTimes() for pid in pids}

    # Extract the time at which each process was first executed.  This
    # needs to be done with the Gantt Chart part because it is not
    # directly reported in the table nor can it be calculated from the
    # provided values.
    seen_pids = set()
    for pid, time in zip(pids, times):
        if pid in seen_pids:
            continue
        process_times = times_mapping[pid]
        process_times.first_exec_time = time
        seen_pids.add(pid)

    # Extract the arrival and waiting times from the table part
    table_lines = table_string.splitlines()
    for line in table_lines:
        line_tokens = line.split()
        pid, arrival_string, *_, waiting_string = line_tokens

        arrival_time = int(arrival_string)
        waiting_time = int(waiting_string)

        process_times = times_mapping[pid]
        process_times.arrival_time = arrival_time
        process_times.waiting_time = waiting_time

    # We only need the process times.  The PID mapping was just for
    # internal use, to sync up the Gantt Chart and table parts of
    # parsing the input.
    return tuple(times_mapping.values())


def main() -> None:
    """Main driver function."""
    argc = len(sys.argv)
    if argc < 2:
        sys.stderr.write(f"USAGE: {sys.argv[0]} FILENAME\n")
        sys.exit(22)

    filename = sys.argv[1]
    with open(filename, "rt", encoding="utf-8") as fp:
        raw_text = fp.read()

    if not is_round_robin(raw_text):
        sys.stderr.write(
            "It looks like you didn't select the Round-Robin algorithm!\n")
        sys.exit(1)

    gantt_chart, table_string = extract_gantt_and_table(raw_text)
    num_entries = get_num_processes(raw_text)
    pids, times = parse_gantt_chart(gantt_chart, num_entries)
    process_times = get_process_times(pids, times, table_string)
    size = len(process_times)

    # This is already provided below the table, but just for convenient
    # output that matches the format of what ./rr would output.
    total_waiting_time = sum(t.waiting_time for t in process_times)
    total_response_time = sum(t.first_exec_time - t.arrival_time
                              for t in process_times)

    avg_waiting_time = float(total_waiting_time / size)
    avg_response_time = float(total_response_time / size)

    print(f"Average waiting time: {avg_waiting_time:.2f}")
    print(f"Average response time: {avg_response_time:.2f}")


if __name__ == "__main__":
    main()
