#!/usr/bin/env bash

# Script to run to set up the test suite.  Namely, add the executable permission
# bits to all files meant to be executable such that you can invoke them
# directly without specifying the interpreter.

# Thanks ChatGPT <3! This loop runs chmod +x on all files in the current
# directory that either end in .py or do not have a file extension.
for file in *; do
    if [[ -f $file && (${file: -3} == ".py" || ${file#*.} == $file) ]]; then
        chmod +x "$file"
    fi
done
