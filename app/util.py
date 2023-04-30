import os
import numpy as np
from tensorflow.keras.preprocessing.sequence import pad_sequences
import random


class DataObject:
    def __init__(self, dictionary):
        self.__dict__.update(dictionary)

def float_or_none(value):
    try:
        return float(value)
    except:
        return None
def load_data_from_file(file_name):
    data = []
    with open(file_name, 'r', encoding='utf-8') as f:
        for line in f:
            split_line = line.strip().split('\t')
            if len(split_line) < 2:
                continue
            q, a = split_line[:2]
            data.append((q, a))

    return data

def byte_level_tokenization(text):
    return [float(ord(c)) for c in text]

def byte_level_detokenization(tokens):
    return "".join([chr(int(c)) for c in tokens])

def tokenize_data(data):
    return [(byte_level_tokenization(qa[0]), byte_level_tokenization(qa[1])) for qa in data]

def pad_data(data, max_length):
    return [(pad_sequences([q], maxlen=max_length, padding='post', value=0)[0], pad_sequences([a], maxlen=max_length, padding='post', value=0)[0]) for q, a in data]

def load_and_preprocess_multiple_data_files(data_files, max_length, slice_records=0, randomize=False):
    all_data = []

    # Load and combine data from all data files
    for data_file in data_files:
        data = load_data_from_file(data_file)
        all_data.extend(data)

    # Clip and randomize
    if randomize:
        random.shuffle(all_data)

    # Clip and randomize
    if slice_records > 0:
        all_data = all_data[:slice_records]

    # Tokenize and pad data
    tokenized = tokenize_data(all_data)
    padded = pad_data(tokenized, max_length)

    x = np.array([q for q, a in padded]).astype(np.int32)
    y = np.array([a.reshape(-1, 1) for q, a in padded]).astype(np.int32)

    return x, y
