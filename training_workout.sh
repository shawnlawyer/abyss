#!/bin/bash

config_file=
epochs=5
iterations=1
batch_size=16
sample_size=400000

while getopts "c:e:i:b:s:" opt; do
  case ${opt} in
    c )
      config_file=${OPTARG}
      ;;
    i )
      iterations=${OPTARG}
      ;;
    e )
      epochs=${OPTARG}
      ;;
    b )
      batch_size=${OPTARG}
      ;;
    s )
      sample_size=${OPTARG}
      ;;
    \? )
      echo "Invalid option: -$OPTARG" 1>&2
      echo "Usage: $0 -c <config_file> [-i <iterations>] [-e <epochs>] [-b <batch_size>] [-s <sample_size>]" >&2
      echo "Example: $0 -c lstm.json -i 3 -e 10 -b 32 -s 200000" >&2
      exit 1
      ;;
    : )
      echo "Option -$OPTARG requires an argument." 1>&2
      echo "Usage: $0 -c <config_file> [-i <iterations>] [-e <epochs>] [-b <batch_size>] [-s <sample_size>]" >&2
      echo "Example: $0 -c lstm.json -i 3 -e 10 -b 32 -s 200000" >&2
      exit 1
      ;;
  esac
done

if [ -z "$config_file" ]; then
    echo "Error: config file is a required option" >&2
    echo "Usage: $0 -c <config_file> [-i <iterations>] [-e <epochs>] [-b <batch_size>] [-s <sample_size>]" >&2
    echo "Example: $0 -c lstm.json -i 3 -e 10 -b 32 -s 200000" >&2
    exit 1
fi

for (( iteration=1; iteration<=$iterations; iteration++ ))
do
    echo "Iteration number $iteration"
    modified_sample_size=$sample_size
    modified_batch_size=$batch_size
    for (( i=1; i<=4; i++ ))
    do
        echo "  Sample size: $modified_sample_size, Batch size: $modified_batch_size"
        python app --config=$config_file --train --batch-size=$modified_batch_size --epochs=$epochs --sample-size=$modified_sample_size
        modified_sample_size=$(($modified_sample_size / 2))
        modified_batch_size=$(($modified_batch_size * 2))
    done
done
