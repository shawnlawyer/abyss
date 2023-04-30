import os
import re
import random
from sklearn.model_selection import train_test_split

def load_conversations_from_file(file_path):
    conversations = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error opening conversation file: {e}")
        return conversations

    current_conversation = []
    for line in lines:
        line_parts = line.strip().split(' ')
        if len(line_parts) < 2:
            continue

        line_number = line_parts[0]
        text = ' '.join(line_parts[1:])

        # Remove unnecessary spaces
        text = re.sub(' +', ' ', text)

        if line_number == '1':
            if current_conversation:
                for i in range(len(current_conversation) - 1):
                    conversations.append((current_conversation[i], current_conversation[i + 1]))
            current_conversation = [text]
        else:
            current_conversation.append(text)

    # Add the last conversation
    if current_conversation:
        for i in range(len(current_conversation) - 1):
            conversations.append((current_conversation[i], current_conversation[i + 1]))

    return conversations

def preprocess_text(text):
    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"[-()\"#/@;:<>{}`+=~|.!?,]", "", text)
    return text

def save_data_to_file(data, file_name):
    try:
        with open(file_name, 'w', encoding='utf-8') as f:
            for q, a in data:
                try:
                    f.write(f"{q}\t{a}\n")
                except Exception as e:
                    print(f"Error writing question-answer pair to file: {e}")
    except Exception as e:
        print(f"Error opening output file: {e}")

def main():
    corpus_dir = "corpus"

    train_files = [
        "train_both_original.txt",
        "train_both_revised.txt",
        "train_none_original.txt",
        "train_other_original.txt",
        "train_other_revised.txt",
        "train_self_original.txt",
        "train_self_revised.txt"
    ]

    conversations = []
    for file_name in train_files:
        file_path = os.path.join(corpus_dir, file_name)
        loaded_conversations = load_conversations_from_file(file_path)
        print(f"Loaded {len(loaded_conversations)} conversations from {file_name}")
        conversations.extend(loaded_conversations)
    preprocessed_conversations = [(preprocess_text(q), preprocess_text(a)) for q, a in conversations]

    train_data, test_data = train_test_split(preprocessed_conversations, test_size=0.2, random_state=42)
    train_output_file = "train_data.txt"
    test_output_file = "test_data.txt"

    train_output_path = os.path.join("datasets", "persona_chat", train_output_file)
    test_output_path = os.path.join("datasets", "persona_chat", test_output_file)

    save_data_to_file(train_data, train_output_path)
    save_data_to_file(test_data, test_output_path)

if __name__ == "__main__":
    main()
