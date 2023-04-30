#!/bin/bash
DIR=persona_chat
DATASET_URL="https://parl.ai/downloads/personachat/personachat.tgz"
DATASET_TAR="personachat.tgz"
CORPUS_DIR="corpus"
DATASETS_DIR="datasets/$DIR"

echo "Downloading the dataset..."
if curl -O $DATASET_URL -L; then
    echo "Extracting the dataset..."
    tar -xzf $DATASET_TAR

    echo "Removing the tar file..."
    rm $DATASET_TAR

    echo "Renaming extracted directory..."
    mv personachat $CORPUS_DIR

    echo "Creating $DIR directory if it doesn't exist..."
    mkdir -p $DATASETS_DIR

    echo "Running prepare_training.py script to prepare training data..."
    #python prepare_persona_chat.py

    echo "Cleaning up corpus directory..."
    #rm -Rf $CORPUS_DIR

    echo "Removing __MACOSX/ directory if it exists..."
    rm -Rf __MACOSX
else
    echo "Error downloading dataset"
fi
