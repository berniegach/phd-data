#!/bin/bash

for i in 0 2 3; do
    for j in 0 2 3; do
        for k in 0 2 3; do
            echo "IPC033-235 v1" | ./socoles --sql=2024_april/235/journal.sql --queries=2024_april/235/Exam4April.csv --model=2024_april/235/correct.csv --syntax=$i --semantics=$j --results=$k
            mv "quiz_graded.csv" "quiz_graded_sn${i}_sm${j}_rs${k}.csv"
        done
    done
done

