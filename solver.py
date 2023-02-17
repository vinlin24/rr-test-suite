#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""solver.py

Script for calculating the average waiting time and average response
time given the copy-pasted text from the Gantt chart of the online
process scheduling solver
https://boonsuen.com/process-scheduling-solver.  The output format is
identical to what should be outputted by a correct rr.c implementation.

USAGE: `./solver.py FILENAME`, where FILENAME is the name of the file
into which you paste the HTML of the solver webpage.
"""

import sys
from html.parser import HTMLParser
from typing import Dict, List, Literal, Optional, Set, Tuple

__author__ = "Vincent Lin"

AttrsList = List[Tuple[str, Optional[str]]]


class GanttChartParser(HTMLParser):
    OUTERMOST_DIV_CLASSNAME = "sc-a3b21388-0 evwFKR"
    COMBINED_ROW_DIV_CLASSNAME = "sc-a3b21388-6 dmgGsv"

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
            self.update_current_row_type()
        elif self.in_gantt_chart:
            # If the chart DOESN'T wrap, the "combined row" <div> layer
            # doesn't exist, in which case, direct children of the Gantt
            # Chart <div> would be PIDs/times rows.
            if class_attr == self.COMBINED_ROW_DIV_CLASSNAME:
                self.in_combined_row = True
            else:
                self.update_current_row_type()
        elif class_attr == self.OUTERMOST_DIV_CLASSNAME:
            self.in_gantt_chart = True

    def update_current_row_type(self) -> None:
        if self.next_row_type == "pids":
            self.in_pids_row = True
            self.next_row_type = "times"
        else:
            self.in_times_row = True
            self.next_row_type = "pids"

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


class OutputTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()

        self.in_tbody = False
        self.in_tr = False
        self.in_td = False

        self.tds_in_tr_encountered = 0
        self.average_found = False
        self.turnaround_found = False

        self.current_pid: Optional[str] = None
        self.average_waiting_time = float("inf")
        self.arrival_times: Dict[str, int] = {}

    def handle_starttag(self, tag: str, attrs: AttrsList) -> None:
        # There should be exactly one <tbody>, that of the output table.
        if tag == "tbody":
            self.in_tbody = True
        elif tag == "tr":
            self.in_tr = True
        elif tag == "td":
            self.in_td = True
            self.tds_in_tr_encountered += 1

    def handle_endtag(self, tag: str) -> None:
        # Check inner -> outer to see which endtag we just encountered.
        if tag == "td":
            self.in_td = False
        elif tag == "tr":
            self.in_tr = False
            self.tds_in_tr_encountered = 0  # Reset.
        elif tag == "tbody":
            self.in_tbody = False

    def handle_data(self, data: str) -> None:
        if not self.in_td:
            return

        # Handle the special last row (averages).
        if data == "Average":
            self.average_found = True
            return
        if self.average_found:
            # Average waiting time comes after the one for turnaround.
            if self.turnaround_found:
                self.average_waiting_time = float(data.split()[-1])
            else:
                self.turnaround_found = True
            return

        # PID is field $1.
        if self.tds_in_tr_encountered == 1:
            self.current_pid = data

        # Arrival Time is field $2.
        elif self.tds_in_tr_encountered == 2:
            if self.current_pid is None:
                raise ValueError(
                    "Unexpectedly unable to get the PID "
                    "for a process in the output table.")
            # Write and reset.
            self.arrival_times[self.current_pid] = int(data)
            self.current_pid = None

    def get_arrival_times(self) -> Dict[str, int]:
        return self.arrival_times

    def get_average_waiting_time(self) -> float:
        return self.average_waiting_time


def get_average_response_time(pids: List[str],
                             times: List[int],
                             arrival_times: Dict[str, int]
                             ) -> float:
    """
    Given the parsed PIDs and times from the Gantt Chart and arrival
    times from the output table, compute the average response time.
    """
    total_response_time = 0
    num_processes = len(arrival_times.keys())

    # We only act on the FIRST instance of a PID (since we need the time
    # at which it FIRST executes).
    seen_pids: Set[str] = set()

    # len(times) = len(pids) + 1 because it includes the final end time,
    # so that will be excluded, which is fine.
    for pid, first_exec_time in zip(pids, times):
        # "PID" is "_" in chart for slots where no process is executing.
        if pid in seen_pids or pid == "_":
            continue
        arrival_time = arrival_times[pid]
        total_response_time += (first_exec_time - arrival_time)
        seen_pids.add(pid)

    return float(total_response_time / num_processes)


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

    table_parser = OutputTableParser()
    table_parser.feed(raw_html)
    arrival_times = table_parser.get_arrival_times()
    avg_waiting_time = table_parser.get_average_waiting_time()

    avg_response_time = get_average_response_time(pids, times, arrival_times)

    print(f"Average waiting time: {avg_waiting_time:.2f}")
    print(f"Average response time: {avg_response_time:.2f}")


if __name__ == "__main__":
    main()
