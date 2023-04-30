#!/bin/bash

iterations=1
epochs=5

while getopts "i:e:" opt; do
  case ${opt} in
    i )
      iterations=${OPTARG}
      ;;
    e )
      epochs=${OPTARG}
      ;;
    \? )
      echo "Invalid option: -$OPTARG" 1>&2
      exit 1
      ;;
    : )
      echo "Option -$OPTARG requires an argument." 1>&2
      exit 1
      ;;
  esac
done

for (( iteration=1; iteration<=$iterations; iteration++ ))
do
    echo "Iteration number $iteration"
    python main.py --config=lstm.json --train --batch-size=16 --epochs=$epochs --sample-size=400000
    python main.py --config=lstm.json --train --batch-size=32 --epochs=$epochs --sample-size=200000
    python main.py --config=lstm.json --train --batch-size=64 --epochs=$epochs --sample-size=100000
    python main.py --config=lstm.json --train --batch-size=128 --epochs=$epochs --sample-size=50000
done
