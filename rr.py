#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rr.py

Python equivalent of the skeleton code for rr.c, the source file of W23
COM SCI 111 Lab 2: You Spin Me Round Robin.  I found it useful to start
from here because it's easier to debug in Python, and you don't need to
shorten your lifespan with each Segmentation fault.  It is relatively
trivial to then translate your implementation from Python to C.

Author: Vincent Lin

Usage: ./rr.py INPUT_FILE QUANTUM_LENGTH
"""

import sys
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, List, Optional

__author__ = "YOUR NAME HERE"

EXIT_SUCCESS = 0
EINVAL = 22


@dataclass
class process_t:
    """Represents one entry of the input file."""
    # Provided fields.
    pid: int
    arrival_time: int
    burst_time: int

    # Additional fields.
    pass


class process_list_t:
    """Wrapper of collections.deque to simulate the TAILQ API."""

    def __init__(self) -> None:
        """Use the composition design pattern to wrap a deque."""
        self._queue: deque[process_t] = deque()

    def __repr__(self) -> str:
        """Implement a debugging-friendly string representation.

        I didn't actually have this when I wrote mine.  You're welcome.
        """
        INDENT = " "*4
        formatted_elements = "\n".join(f"{INDENT}{element}"
                                      for element in self._queue)
        if formatted_elements == "":
            content = ""
        else:
            content = f"\n{formatted_elements}\n"

        class_name = self.__class__.__name__
        return f"{class_name}({content})"

    def __iter__(self) -> Iterator[process_t]:
        """Implement for-in iteration to simulate TAILQ_FOREACH."""
        return iter(self._queue)

    def empty(self) -> bool:
        """Return whether the queue has zero elements in it."""
        return len(self._queue) == 0

    def first(self) -> Optional[process_t]:
        """Return the first element in the queue, or None if empty."""
        if self.empty():
            return None
        return self._queue[0]

    def last(self) -> Optional[process_t]:
        """Return the last element in the queue, or None if empty."""
        if self.empty():
            return None
        return self._queue[-1]

    def prev(self, element: process_t) -> Optional[process_t]:
        """
        Return the previous element in the queue, or None if the given
        element is the first element.  Note that because deque does not
        expose the underlying pointers, this wrapper uses deque.index()
        followed by subscripting, which is redundant time overhead.
        """
        if element == self.first():
            return None
        index = self._queue.index(element)  # This can raise.
        return self._queue[index-1]

    def next(self, element: process_t) -> Optional[process_t]:
        """
        Return the next element in the queue, or None if the given
        element is the last element.  Note that because deque does not
        expose the underlying pointers, this wrapper uses deque.index()
        followed by subscripting, which is redundant time overhead.
        """
        if element == self.last():
            return None
        index = self._queue.index(element)  # This can raise.
        return self._queue[index+1]

    def remove(self, element: process_t) -> None:
        """Remove the element from the queue."""
        self._queue.remove(element)

    def insert_head(self, element: process_t) -> None:
        """Insert a new element at the head of the queue."""
        self._queue.appendleft(element)

    def insert_tail(self, element: process_t) -> None:
        """Insert a new element at the tail of the queue."""
        self._queue.append(element)

    def insert_before(self, existing: process_t, element: process_t) -> None:
        """
        Insert an element before an existing one in the queue.  Note
        that because deque does not expose the underlying pointers, this
        wrapper uses deque.index() followed by deque.insert(), which is
        redundant time overhead.
        """
        index = self._queue.index(existing)
        self._queue.insert(index, element)

    def insert_after(self, existing: process_t, element: process_t) -> None:
        """
        Insert an element after an existing one in the queue.  Note
        that because deque does not expose the underlying pointers, this
        wrapper uses deque.index() followed by deque.insert(), which is
        redundant time overhead.
        """
        index = self._queue.index(existing)
        self._queue.insert(index + 1, element)


def init_processes(file_path: Path) -> List[process_t]:
    """Parse input file and return a list of represented processes."""
    data: List[process_t] = []

    with file_path.open("rt", encoding="utf-8") as fp:
        # Ignore the first line as that's not needed in Python.
        fp.readline()

        for line in fp:
            nums = [int(s.strip()) for s in line.rstrip().split(",")]
            pid, arrival_time, burst_time = nums

            # If you choose to add fields to process_t, update this:
            process = process_t(
                pid=pid,
                arrival_time=arrival_time,
                burst_time=burst_time
            )
            data.append(process)

    return data


def main(argc: int, argv: List[str]) -> int:
    """Main driver function."""
    if argc != 3:
        return EINVAL
    file_path = Path(argv[1])
    try:
        quantum_length = int(argv[2])
        if quantum_length < 0:
            raise ValueError("Quantum length must be non-negative.")
    except Exception:
        return EINVAL

    data = init_processes(file_path)
    size = len(data)

    # pylint: disable=redefined-builtin
    list = process_list_t()

    total_waiting_time = 0
    total_response_time = 0

    # Your code here.

    pass

    # End of "Your code here".

    avg_waiting_time = float(total_waiting_time / size)
    avg_response_time = float(total_response_time / size)
    print(f"Average waiting time: {avg_waiting_time:.2f}")
    print(f"Average response time: {avg_response_time:.2f}")
    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main(len(sys.argv), sys.argv))
