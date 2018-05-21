#!/bin/bash

CONCURRENCY=2

mkdir -p "$1/pretreated"

./convert-list-args.sh "$1" | xargs -0 -n 3 -P $CONCURRENCY ./convert-file.sh
