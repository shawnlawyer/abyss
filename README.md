# Sequence-to-Sequence Model Training Script

This script is designed to train a sequence-to-sequence model using TensorFlow and Keras. The model is built using Bidirectional LSTMs or GRUs and is suitable for various natural language processing tasks, such as text generation, machine translation, or summarization.

## Prerequisites

- TensorFlow 2.x
- Python 3.x

## Usage

To train the model, run the script from the command line with the desired arguments:

python train_seq2seq.py [options]


Options:

- `--data-dir`: Directory for the data files (default: "data").
- `--model-filename`: Filename for the model file (default: "model.h5").
- `--train-data`: Name of the train data file (default: "train_data.txt").
- `--test-data`: Name of the test data file (default: "test_data.txt").
- `--max-length`: Maximum sequence length (default: 256).
- `--batch-size`: Batch size (default: 128).
- `--epochs`: Number of epochs (default: 300).
- `--learning-rate`: Learning rate for the optimizer (default: 0.001).
- `--learning-rate-decay`: Learning rate decay factor (default: 0.0).
- `--embedding-size`: Embedding dimension for the input layer (default: 100).
- `--recurrent-units`: Number of units for the recurrent layer(s) (default: 1024).
- `--vocab-size`: Size of the vocabulary (default: 256).
- `--early-stopping-patience`: Patience for early stopping (default: 10).
- `--gradient-clip`: Gradient clipping threshold (default: None).
- `--logs-dir`: Directory for TensorBoard logs (default: "logs").
- `--recurrent-layers`: Number of recurrent layers (default: 1).
- `--recurrent-type`: Type of the recurrent layer (choices: "LSTM", "GRU"; default: "LSTM").
- `--dropout`: Dropout rate for the recurrent layers (default: 0.0).
- `--recurrent-dropout`: Recurrent dropout rate for the recurrent layers (default: 0.0).
- `--config`: Path to the configuration JSON file (default: None).
- `--save-config`: Path to save the current configuration JSON file (default: None).
- `--rebuild-model`: Build a new model instead of loading the last checkpoint (default: False).
- `--chat`: Activate chat mode (default: False).
- `--no-gpu`: Disable GPU usage (default: False).


## Configuration

You can load and save the configuration using JSON files. To load a configuration file, use the `--config` option:

python main.py --config config.json

To save the current configuration to a JSON file, use the `--save-config` option:

python main.py --save-config config.json

## Notes

- This script supports both LSTM and GRU recurrent layers.
- The model is built using Keras' functional API.
- The script supports early stopping, model checkpointing, TensorBoard logging, and learning rate reduction on plateau.
- The script can load and save configurations from JSON files, as well as accept command-line arguments for overriding default settings.

