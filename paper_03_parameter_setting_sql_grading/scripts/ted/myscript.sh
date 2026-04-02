#!/bin/bash

for i in {0..16}; do
    for j in {0..15}; do
        echo "IPC033-289 v1" | ./socoles 2024/289/discography.sql 2024/289/original_results.csv 2024/289/correct.csv 3 3 3 3 1 $i $j
	mv "quiz_graded.csv" "quiz_graded_${i}_${j}.csv"
    done
done

