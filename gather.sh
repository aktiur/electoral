#!/bin/bash

dirname=`basename $1`

filenames="$1/out/*.csv"
files=( $filenames )

( head -n 1 ${files[0]}; for i in "${files[@]}"; do tail -n +2 "$i"; done ) > $1/$dirname.csv
