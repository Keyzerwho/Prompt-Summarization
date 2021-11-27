#!/usr/bin/env bash

. find_files.sh

echo "Testing script"

required_files=(question.txt summary.txt expert.txt)

get_generated_human
for problem in $problems; do
    for file in "${required_files[@]}"; do
        ! [[ -f $problem/clean-$file ]] && echo "Make sure the format.sh script runs without errors. This file didn't exist $problem/clean-$file" && error=1
    done
done

[[ ! -z $error ]] && echo "Failed test" && exit 1 || echo "Passed test"
