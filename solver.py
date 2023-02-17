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

import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import List, Literal, Optional, Tuple

__author__ = "Vincent Lin"

AttrsList = List[Tuple[str, Optional[str]]]


class GanttChartParser(HTMLParser):
    OUTERMOST_DIV_CLASSNAME = "sc-a3b21388-0 evwFKR"

    def __init__(self) -> None:
        super().__init__()
        self.in_gantt_chart = False
        self.in_combined_row = False
        self.in_pids_row = False
        self.in_times_row = False
        self.in_pid_cell = False
        self.in_time_cell = False
        # PIDs <div> comes before times <div>.
        self.next_row_type: Literal["pids", "times"] = "pids"
        self.pids: List[str] = []
        self.times: List[int] = []

    def handle_starttag(self, tag: str, attrs: AttrsList) -> None:
        if tag != "div":
            return

        class_attr = dict(attrs).get("class")

        # Check inner -> outer to see if we entered a child
        if self.in_pids_row:
            self.in_pid_cell = True
        elif self.in_times_row:
            self.in_time_cell = True
        elif self.in_combined_row:
            if self.next_row_type == "pids":
                self.in_pids_row = True
                self.next_row_type = "times"
            else:
                self.in_times_row = True
                self.next_row_type = "pids"
        elif self.in_gantt_chart:
            self.in_combined_row = True
        elif class_attr == self.OUTERMOST_DIV_CLASSNAME:
            self.in_gantt_chart = True

    def handle_endtag(self, tag: str) -> None:
        if tag != "div":
            return

        # Check inner -> outer to see which endtag we just encountered
        if self.in_pid_cell:
            self.in_pid_cell = False
        elif self.in_time_cell:
            self.in_time_cell = False
        elif self.in_pids_row:
            self.in_pids_row = False
        elif self.in_times_row:
            self.in_times_row = False
        elif self.in_combined_row:
            self.in_combined_row = False
        elif self.in_gantt_chart:
            self.in_gantt_chart = False

    def handle_data(self, data: str) -> None:
        if self.in_pid_cell:
            self.pids.append(data)
        elif self.in_time_cell:
            time = int(data)
            # If the chart wraps, the end time of one row and start time
            # of the next is the same, and we don't want duplicates.
            if not self.times or self.times[-1] != time:
                self.times.append(int(data))

    def get_pids(self) -> List[str]:
        return self.pids

    def get_times(self) -> List[int]:
        return self.times


@dataclass(init=False)
class ProcessTimes:
    """Convenience struct for bundling a process' relevant times."""
    arrival_time: int
    first_exec_time: int
    waiting_time: int


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
        raw_html = fp.read()

    chart_parser = GanttChartParser()
    chart_parser.feed(raw_html)
    pids = chart_parser.get_pids()
    times = chart_parser.get_times()

    print(pids)
    print(times)

    return  # TODO.
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
