import os
import re
import random
import requests
import zipfile
import io
import tempfile
from sklearn.model_selection import train_test_split

DATASET_URL = "http://www.cs.cornell.edu/~cristian/data/cornell_movie_dialogs_corpus.zip"
CORPUS_DIR = "cmc"
TEMP_DIR = tempfile.gettempdir()
TRAIN_FILE = "train_data.txt"
TEST_FILE = "test_data.txt"
DATASETS_DIR = "../../datasets"
def load_movie_lines(file_path):
    try:
        with open(file_path, 'r', encoding='iso-8859-1') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error opening movie lines file: {e}")
        return {}

    movie_lines = {}
    for line in lines:
        split_line = line.split(" +++$+++ ")
        if len(split_line) < 2:
            continue

        line_id = split_line[0]
        text = split_line[-1].strip()
        movie_lines[line_id] = text

    return movie_lines

def load_conversations(file_path, movie_lines):
    try:
        with open(file_path, 'r', encoding='iso-8859-1') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error opening movie conversations file: {e}")
        return []

    conversations = []
    for line in lines:
        split_line = line.split(" +++$+++ ")
        if len(split_line) < 2:
            continue

        try:
            line_ids = eval(split_line[-1])
        except Exception as e:
            print(f"Error parsing line IDs: {e}")
            continue

        for i in range(len(line_ids) - 1):
            question = movie_lines.get(line_ids[i], "")
            answer = movie_lines.get(line_ids[i + 1], "")
            if question and answer:
                conversations.append((question, answer))

    return conversations

def preprocess_text(text):
    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"[-()\"#/@;:<>{}`+=~|.!?,]", "", text)
    return text


def save_data_to_file(data, file_name):
    try:
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        with open(file_name, 'w', encoding='utf-8') as f:
            for q, a in data:
                try:
                    f.write(f"{q}\t{a}\n")
                except Exception as e:
                    print(f"Error writing question-answer pair to file: {e}")
    except Exception as e:
        print(f"Error opening output file: {e}")


def download_and_unzip(url, extract_to='.'):
    print(f'Downloading the dataset from {url}...')
    response = requests.get(url)
    if response.status_code == 200:
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            zip_ref.extractall(extract_to)
        print('Download and extraction successful.')
    else:
        print(f"Error downloading dataset: {response.status_code}")
        exit(1)

# The rest of your Python script goes here...

def main():

    # Download and extract data
    download_and_unzip(DATASET_URL, TEMP_DIR)

    # Rename directory
    movie_lines_file = os.path.join(TEMP_DIR, "cornell movie-dialogs corpus", "movie_lines.txt")
    movie_conversations_file = os.path.join(TEMP_DIR, "cornell movie-dialogs corpus", "movie_conversations.txt")

    movie_lines = load_movie_lines(movie_lines_file)
    conversations = load_conversations(movie_conversations_file, movie_lines)
    preprocessed_conversations = [(preprocess_text(q), preprocess_text(a)) for q, a in conversations]

    train_data, test_data = train_test_split(preprocessed_conversations, test_size=0.2, random_state=42)
    train_output_file = TRAIN_FILE
    test_output_file = TEST_FILE

    train_output_path = os.path.join(DATASETS_DIR, CORPUS_DIR, train_output_file)
    test_output_path = os.path.join(DATASETS_DIR, CORPUS_DIR, test_output_file)

    save_data_to_file(train_data, train_output_path)
    save_data_to_file(test_data, test_output_path)


if __name__ == "__main__":
    main()

