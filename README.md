# Round-Robin Lab Test Suite


A collection of useful scripts for your development and testing workflow for **UCLA W23 COM SCI 111 Lab 2: You Spin Me Round Robin**.


## Setup


Download the compressed tarball from my [dist/](dist/) folder or `curl` it directly from the command line:

```sh
curl https://raw.githubusercontent.com/vinlin24/rr-test-suite/main/dist/test_suite.tgz -o test_suite.tgz
```

You can extract the scripts directly into your lab2 directory:

```sh
tar -xzvf test_suite.tgz
```

Alternatively, if you're scared of `tar` overwriting files (you shouldn't have files with the same name as my scripts, but it's a good habit):

```sh
mkdir test_suite
tar -xzvf test_suite.tgz -C test_suite
# Then you can use mv to bring what you want to the top-level
```


## Python Skeleton Code


For those who have not started yet, I created a Python equivalent of the rr.c skeleton code: [rr.py](rr.py). I myself started from something similar to this when I kept running into problems with my C implementation. It's must easier to express and debug an algorithm in Python, and it's a relatively trivial task to then translate the code back into C.

I tried to keep the code as one-to-one as possible:

* `struct process_list` and the corresponding [tailq API](https://man7.org/linux/man-pages/man3/tailq.3.html) became `process_list_t`, a wrapper class for Python's [`collections.deque`](https://docs.python.org/3/library/collections.html#collections.deque) data structure. I exposed limited methods with similar names, like `insert_head` for `TAILQ_INSERT_HEAD`, to make your code more one-to-one with the real thing.
* `struct process` became `process_t`, a Python [dataclass](https://docs.python.org/3/library/dataclasses.html). If you're unfamiliar with dataclasses, they're basically the closest thing you get to **Plain Old Data (POD)** `struct`s: simple collections of member variables.
* Like expected, `data` is a `List[process_t]`, `list` is your "tail queue" instance, and `size`, `quantum_length`, `total_waiting_time` and `total_response_time` are all `int`s.
* `init_processes()` handles the file I/O for you, and the final `print()` statements already format the output exactly the way rr.c should.


## Scripts for the Online Solver


These scripts are designed to be used with the very useful online scheduling solver tool: https://boonsuen.com/process-scheduling-solver. Remember to set the algorithm to **Round-Robin, RR**. This tool helps visualize the order of your processes with a **Gantt Chart**.

Your workflow can look like this:


### (1) Convert Input File to Input Lists


[to_solver](to_solver) converts an input file (like processes.txt) into a space-separated list of arrival and burst times. This lets you conveniently copy-and-paste them into the input fields of the online solver:

```console
$ ./to_solver processes.txt
0 2 4 5
7 4 1 4
```


### (2) Parse Webpage for Expected Output


Capture the output of the online solver and paste it into some dummy file. My [solver.py](solver.py) script parses the raw copy-pasted text and calculates the correct average response and waiting time, in the exact format of ./rr's output:

```console
$ touch output.txt
$ # Hit Ctrl+A Ctrl+C on the solver webpage...
$ # Ctrl+V that into output.txt...
$ ./solver.py output.txt
Average waiting time: 7.00
Average response time: 2.75
```


### (3) Convert Input Lists to Input File


Alternatively, it's much easier to write test cases directly into the online solver instead of filling out a new processes.txt. I also provide a [from_solver](from_solver) script that converts the space-separated input lists into a file in a format ready to be loaded by ./rr:

```console
$ ./from_solver '0 2 4 5' '7 4 1 4'
4
1, 0, 7
2, 2, 4
3, 4, 1
4, 5, 4
$ # Save the output so you can try it with your ./rr
$ ./from_solver '0 2 4 5' '7 4 1 4' > my_test_case.txt
$ ./rr my_test_case.txt 3
```


### (4) Generate Random Test Cases!


Instead of keyboard mashing to create your own test cases, you can use my [generate.py](generate.py) script to generate random but valid lists of arrival and burst times. They are outputted in the [same format at to_solver](#1-convert-input-file-to-input-lists):

```console
$ ./generate.py
6 1 13 3
11 11 8 3
```

The script supports some options, like customizing the number of entries (default 4), the allowed range for arrival and burst times (default 0-20 and 1-20 respectively), and saving a copy as a file in a format ready to be loaded by ./rr:

```console
$ ./generate.py 6 -a 20-50 -b 1-30 -o my_test_case.txt
40 40 27 38 26 22
28 14 29 7 19 2
$ cat my_test_case.txt
6
1, 40, 28
2, 40, 14
3, 27, 29
4, 38, 7
5, 26, 19
6, 22, 2
```

You can review the options with `./generate.py --help`.
