#!/bin/bash

for i in 0 2 3; do
    for j in 0 2 3; do
        for k in 0 2 3; do
            echo "IPC033-294 v1" | ./socoles --sql=294/discography.sql --queries=294/original_results.csv --model=294/correct.csv --syntax=$i --semantics=$j --results=$k
            mv "quiz_graded.csv" "quiz_graded_sn${i}_sm${j}_rs${k}.csv"
        done
    done
done

