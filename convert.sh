#!/bin/bash

for f in $1/*.pdf; do
    filename=$(basename "$f")
    filename="${filename%.*}"
    java -jar tabula-1.0.1-jar-with-dependencies.jar $f --pages all --lattice > "$2/$filename.csv"
done
