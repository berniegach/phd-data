#!/bin/bash
: << 'COMMENT_BLOCK'

for i in 0 2 3; do
    for j in 0 2 3; do
        for k in 0 2 3; do
            echo "IPC033-232 v1" | ./socoles --sql=2024_april/232/journal.sql --queries=2024_april/232/Exam4April.csv --model=2024_april/232/correct.csv --syntax=$i --semantics=$j --results=$k
            mv "quiz_graded.csv" "quiz_graded_sn${i}_sm${j}_rs${k}.csv"
        done
    done
done
COMMENT_BLOCK

for i in 1 2 3 4 5 6; do
    echo "IPC033-232 v1" | ./socoles --sql=2024_april/232/journal.sql --queries=2024_april/232/Exam4April.csv --model=2024_april/232/correct.csv --prop_order=$i 
    mv "quiz_graded.csv" "quiz_graded_prop_order${i}.csv"
done


