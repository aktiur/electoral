#!/bin/bash

mkdir -p $1/pretreated

ls $1/pdf/*.pdf | parallel sh -c "\"java -jar tabula-1.0.1-jar-with-dependencies.jar {} --pages all --lattice > '$1/pretreated/{/.}.csv'\""
