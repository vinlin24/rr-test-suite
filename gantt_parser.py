from html.parser import HTMLParser
from typing import List, Literal, Optional, Tuple

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


with open("output.html") as f:
    parser = GanttChartParser()
    parser.feed(f.read())

pids = parser.get_pids()
times = parser.get_times()
print(pids)
print(times)
