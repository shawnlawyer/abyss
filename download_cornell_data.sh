#!/bin/bash
DIR=cmc
DATASET_URL="http://www.cs.cornell.edu/~cristian/data/cornell_movie_dialogs_corpus.zip"
DATASET_ZIP="cornell_movie_dialogs_corpus.zip"
CORPUS_DIR="corpus"
DATASETS_DIR="datasets/$DIR"

echo "Downloading the dataset..."
if curl -O $DATASET_URL -L; then
    echo "Unzipping the dataset..."
    unzip $DATASET_ZIP

    echo "Removing the zip file..."
    rm $DATASET_ZIP

    echo "Renaming zip directory..."
    mv cornell\ movie-dialogs\ corpus/ $CORPUS_DIR

    echo "Creating $DIR directory if it doesn't exist..."
    mkdir -p $DATASETS_DIR

    echo "Running prepare_training.py script to prepare training data..."
    python prepare_cornell_data.py

    echo "Cleaning up corpus directory..."
    rm -Rf $CORPUS_DIR

    echo "Removing __MACOSX/ directory if it exists..."
    rm -Rf __MACOSX
else
    echo "Error downloading dataset"
fi
