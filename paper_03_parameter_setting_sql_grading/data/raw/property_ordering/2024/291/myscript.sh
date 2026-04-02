#!/bin/bash
: << 'COMMENT_BLOCK'
for i in 0 2 3; do
    for j in 0 2 3; do
        for k in 0 2 3; do
            echo "IPC033-291 v1" | ./socoles --sql=291/discography.sql --queries=291/original_results.csv --model=291/correct.csv --syntax=$i --semantics=$j --results=$k
            mv "quiz_graded.csv" "quiz_graded_sn${i}_sm${j}_rs${k}.csv"
        done
    done
done
COMMENT_BLOCK

for i in 1 2 3 4 5 6; do
    echo "IPC033-291 v1" | ./socoles --sql=291/discography.sql --queries=291/original_results.csv --model=291/correct.csv --prop_order=$i 
    mv "quiz_graded.csv" "quiz_graded_prop_order${i}.csv"
done

