import tensorflow as tf
import numpy as np
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import Input, Bidirectional, LSTM, GRU, Dense, Embedding, TimeDistributed
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.optimizers.schedules import ExponentialDecay
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, TensorBoard, ReduceLROnPlateau
from tensorflow.keras.preprocessing.sequence import pad_sequences
from util import byte_level_tokenization, byte_level_detokenization


# Model building
def build(vocab_size, embedding_size, recurrent_units, recurrent_layers=1, recurrent_type="LSTM", dropout=0.0, recurrent_dropout=0.0, learning_rate=0.001,
          learning_rate_decay=0.0, gradient_clip=None):
    input_layer = Input(shape=(None,))
    embedding_layer = Embedding(vocab_size, embedding_size, mask_zero=True)(input_layer)
    if recurrent_type == 'GRU':
        recurrent_layer = GRU(recurrent_units, return_sequences=True, dropout=dropout, recurrent_dropout=recurrent_dropout)
    else:
        recurrent_layer = LSTM(recurrent_units, return_sequences=True, dropout=dropout, recurrent_dropout=recurrent_dropout)

    recurrent_layers_output = embedding_layer
    for _ in range(recurrent_layers):
        recurrent_layers_output = Bidirectional(recurrent_layer)(recurrent_layers_output)
    output_layer = TimeDistributed(Dense(vocab_size, activation='softmax'))(recurrent_layers_output)

    model = Model(inputs=input_layer, outputs=output_layer)

    if learning_rate_decay > 0:
        learning_rate_schedule = ExponentialDecay(
            initial_learning_rate=learning_rate,
            decay_steps=1000,
            decay_rate=learning_rate_decay
        )
    else:
        learning_rate_schedule = learning_rate
    optimizer = Adam(learning_rate=learning_rate_schedule, clipnorm=gradient_clip) if gradient_clip else Adam(
        learning_rate=learning_rate_schedule)
    model.compile(optimizer=optimizer, loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    return model

# Training and callbacks
def train(model, batch_size, epochs, train_data, test_data, callbacks):
    X_train, y_train = train_data
    X_test, y_test = test_data

    return model.fit(
        X_train,
        y_train,
        batch_size=batch_size,
        epochs=epochs,
        validation_data=(X_test, y_test),
        callbacks=callbacks,
    )

def setup_checkpoint_callback(filepath, save_weights_only=False, save_freq='epoch', verbose=1):
    return ModelCheckpoint(
        filepath=filepath,
        save_weights_only=save_weights_only,
        save_freq=save_freq,
        verbose=verbose
    )

def setup_early_stopping_callback(monitor='val_loss', patience=10, restore_best_weights=True):
    return EarlyStopping(
        monitor=monitor,
        patience=patience,
        restore_best_weights=restore_best_weights
    )

def setup_tensorboard_callback(log_dir, write_graph=True, update_freq='epoch'):
    return TensorBoard(
        log_dir=log_dir,
        write_graph=write_graph,
        update_freq=update_freq
    )

def setup_reduce_lr_callback(monitor='val_loss', factor=0.1, patience=10, min_lr=1e-5, verbose=1):
    return ReduceLROnPlateau(
        monitor=monitor,
        factor=factor,
        patience=patience,
        min_lr=min_lr,
        verbose=verbose
    )

def setup_print_progress_callback(batch_size, sample_size, logs_flag='', as_json=False):
    return PrintProgressCallback(batch_size, sample_size, logs_flag, as_json)


import time

import time
import json


class PrintProgressCallback(tf.keras.callbacks.Callback):
    def __init__(self, batch_size, sample_size, logs_flag='', as_json=False):
        self.batch_size = batch_size
        self.sample_size = sample_size
        self.epoch_losses = []
        self.total_start_time = time.time()
        self.as_json = as_json
        self.logs_flag = '\n' + logs_flag

    def on_epoch_begin(self, epoch, logs=None):
        self.epoch_start_time = time.time()
        if self.as_json:
            print(self.logs_flag + json.dumps({"event": "epoch_begin", "epoch": epoch + 1}))
        else:
            print(f"{self.logs_flag}Starting epoch {epoch + 1}")
        self.epoch_losses = []

    def on_batch_end(self, batch, logs=None):
        batch_loss = logs["loss"]
        batch_acc = logs.get("accuracy")
        batch_lr = self.model.optimizer.lr.numpy().item()
        processed_samples = (batch + 1) * (self.batch_size // self.sample_size)
        if self.as_json:
            print(self.logs_flag + json.dumps(
                {"event": "batch_end", "batch": batch + 1, "batch_size": self.batch_size, "loss": batch_loss,
                 "accuracy": batch_acc, "lr": batch_lr, "processed_samples": processed_samples,
                 "sample_size": self.sample_size}))
        else:
            print(
                f"{self.logs_flag}Batch {batch + 1}/{self.batch_size} - loss: {batch_loss:.4f} - accuracy: {batch_acc:.4f} - lr: {batch_lr:.6f} - processed samples: {processed_samples}/{self.sample_size}")
        self.epoch_losses.append(batch_loss)

    def on_epoch_end(self, epoch, logs=None):
        epoch_loss = sum(self.epoch_losses) / len(self.epoch_losses)
        epoch_acc = logs.get("val_accuracy")
        epoch_val_loss = logs.get("val_loss")
        epoch_time = time.time() - self.epoch_start_time
        total_time = time.time() - self.total_start_time
        if self.as_json:
            print(self.logs_flag + json.dumps(
                {"event": "epoch_end", "epoch": epoch + 1, "loss": epoch_loss, "accuracy": logs.get('accuracy'),
                 "val_loss": epoch_val_loss, "val_accuracy": epoch_acc, "epoch_time": epoch_time,
                 "total_time": total_time, "sample_size": (epoch + 1) * self.sample_size,
                 "num_params": self.model.count_params()}))
        else:
            print(
                f"{self.logs_flag}Epoch {epoch + 1} - loss: {epoch_loss:.4f} - accuracy: {logs.get('accuracy'):.4f} - val_loss: {epoch_val_loss:.4f} - val_accuracy: {epoch_acc:.4f} - time: {epoch_time:.2f}s - total time: {total_time:.2f}s")
            print(f"{self.logs_flag}Total processed samples: {(epoch + 1) * self.sample_size}")
            print(f"{self.logs_flag}Total number of parameters: {self.model.count_params()}")

def setup_capture_progress_callback(callback, batch_size, sample_size, logs_flag='', as_json=False):
    return CaptureProgressCallback(callback, batch_size, sample_size, logs_flag, as_json)

class CaptureProgressCallback(tf.keras.callbacks.Callback):
    def __init__(self, callback, batch_size, sample_size, logs_flag='', as_json=False):
        self.callback = callback
        self.batch_size = batch_size
        self.sample_size = sample_size
        self.epoch_losses = []
        self.total_start_time = time.time()
        self.as_json = as_json
        self.logs_flag = '\n' + logs_flag if logs_flag != '' else ''

    def on_epoch_begin(self, epoch, logs=None):
        self.epoch_start_time = time.time()
        if self.as_json:
            output = self.logs_flag + json.dumps({"event": "epoch_begin", "epoch": epoch + 1})
        else:
            output = f"{self.logs_flag}Starting epoch {epoch + 1}"

        self.callback(output)

    def on_batch_end(self, batch, logs=None):
        batch_loss = logs["loss"]
        batch_acc = logs.get("accuracy")
        batch_lr = self.model.optimizer.lr.numpy().item()
        processed_samples = (batch + 1) * (self.batch_size // self.sample_size)
        if self.as_json:
            output = self.logs_flag + json.dumps(
                {"event": "batch_end", "batch": batch + 1, "batch_size": self.batch_size, "loss": batch_loss,
                 "accuracy": batch_acc, "lr": batch_lr, "processed_samples": processed_samples,
                 "sample_size": self.sample_size})
        else:
            output = f"{self.logs_flag}Batch {batch + 1}/{self.batch_size} - loss: {batch_loss:.4f} - accuracy: {batch_acc:.4f} - lr: {batch_lr:.6f} - processed samples: {processed_samples}/{self.sample_size}"
        self.callback(output)
        self.epoch_losses.append(batch_loss)

    def on_epoch_end(self, epoch, logs=None):
        epoch_loss = sum(self.epoch_losses) / len(self.epoch_losses)
        epoch_acc = logs.get("val_accuracy")
        epoch_val_loss = logs.get("val_loss")
        epoch_time = time.time() - self.epoch_start_time
        total_time = time.time() - self.total_start_time
        if self.as_json:
            output = self.logs_flag + json.dumps(
                {"event": "epoch_end", "epoch": epoch + 1, "loss": epoch_loss, "accuracy": logs.get('accuracy'),
                 "val_loss": epoch_val_loss, "val_accuracy": epoch_acc, "epoch_time": epoch_time,
                 "total_time": total_time, "sample_size": (epoch + 1) * self.sample_size,
                 "num_params": self.model.count_params()})
        else:
            output = f"{self.logs_flag}Epoch {epoch + 1} - loss: {epoch_loss:.4f} - accuracy: {logs.get('accuracy'):.4f} - val_loss: {epoch_val_loss:.4f} - val_accuracy: {epoch_acc:.4f} - time: {epoch_time:.2f}s - total time: {total_time:.2f}s"
            self.callback(output)
            output = f"{self.logs_flag}Total processed samples: {(epoch + 1) * self.sample_size}"
            self.callback(output)
            output = f"{self.logs_flag}Total number of parameters: {self.model.count_params()}"
            self.callback(output)



# Saving and loading the model
def save(model, filepath):
    model.save(filepath)

# Generating responses and chatting
def generate_response(input_text, model, num_responses=1):
    tokenized_input = byte_level_tokenization(input_text)
    padded_input = pad_sequences([tokenized_input] * num_responses, padding='post')
    prediction = model.predict(padded_input)

    responses = []
    for i in range(num_responses):
        response_tokens = np.argmax(prediction[i], axis=-1)
        response_text = byte_level_detokenization(response_tokens)
        responses.append(response_text.strip())

    return responses

def chat(model, num_responses=1):
    print("Chatbot is ready. Type 'quit' to exit.")
    responses = generate_response("hi", model, num_responses)
    for idx, response in enumerate(responses, start=1):
        print(f"Bot {idx}: {response}")
    while True:
        user_input = input("You: ")

        if user_input.lower() == '':
            continue

        responses = generate_response(user_input, model, num_responses)
        for idx, response in enumerate(responses, start=1):
            print(f"Bot {idx}: {response}")

        if user_input.lower() == 'goodbye':
            break

# Utility functions
def disable_gpu():
    tf.config.set_visible_devices([], 'GPU')

def get_weights(model):
    return model.get_weights()

def set_weights(model, weights):
    model.set_weights(weights)

def transfer_weights(src_model, dest_model):
    src_weights = get_weights(src_model)
    dest_model.set_weights(src_weights)

