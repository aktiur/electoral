#!/bin/sh

echo "$1" "($2)" "-->" "$3"
java -jar tabula-1.0.1-jar-with-dependencies.jar --lattice "$1" --pages "$2" > "$3"
