import os
from os.path import join
import json
from util import DataObject, load_and_preprocess_multiple_data_files
import seq2seq
from const import *
from lang.en import CONFIG_FORM_LABELS

settings = DataObject(SETTINGS)
defaults = DataObject(DEFAULTS)

def build(args):
    model = seq2seq.build(args.vocab_size, args.embedding_size, args.recurrent_units, args.recurrent_layers,
                          args.recurrent_type, args.dropout, args.recurrent_dropout, args.learning_rate,
                          args.learning_rate_decay, args.gradient_clip)
    model.save(join(settings.models_dir, args.model_filename))
    return model
def train(model, args):
    checkpoint_callback = seq2seq.setup_checkpoint_callback(
        join(settings.models_dir, args.model_filename),
        save_weights_only=args.checkpoint_save_weights_only,
        save_freq=args.checkpoint_save_freq,
        verbose=args.checkpoint_verbose
    )

    early_stopping_callback = seq2seq.setup_early_stopping_callback(
        monitor=args.early_stopping_monitor,
        patience=args.early_stopping_patience,
        restore_best_weights=args.early_stopping_restore_best_weights
    )

    tensorboard_callback = seq2seq.setup_tensorboard_callback(
        log_dir=settings.logs_dir,
        write_graph=args.tensorboard_write_graph,
        update_freq=args.tensorboard_update_freq
    )

    reduce_lr_callback = seq2seq.setup_reduce_lr_callback(
        monitor=args.reduce_lr_monitor,
        factor=args.reduce_lr_factor,
        patience=args.reduce_lr_patience,
        min_lr=args.reduce_lr_min_lr,
        verbose=args.reduce_lr_verbose
    )

    print_progress_callback = seq2seq.setup_print_progress_callback(
        args.batch_size, args.sample_size, LOG_FLAG, True)

    callbacks = [
        checkpoint_callback,
        early_stopping_callback,
        tensorboard_callback,
        reduce_lr_callback,
        print_progress_callback
    ]

    train_data_filepaths = []
    test_data_filepaths = []
    for dataset in args.datasets:
        train_data_filepaths.append(join(settings.datasets_dir, dataset, settings.train_data_filename))
        test_data_filepaths.append(join(settings.datasets_dir, dataset, settings.test_data_filename))

    history = seq2seq.train(model,
                            args.batch_size,
                            args.epochs,
                            load_and_preprocess_multiple_data_files(train_data_filepaths, args.max_length, args.sample_size, args.randomize_sample),
                            load_and_preprocess_multiple_data_files(test_data_filepaths, args.max_length, args.sample_size, args.randomize_sample),
                            callbacks)

    seq2seq.save(model, join(settings.models_dir, args.model_filename))

def save_config(config, filename)   :
    with open(filename, "w") as outfile:
        json.dump(config, outfile, indent=4)

def load_config(filename):
    with open(filename, "r") as infile:
        config = json.load(infile)
    return config

def make_system_directories():
    for dir in ["configs_dir", "logs_dir", "datasets_dir", "models_dir"]:
        os.makedirs(SETTINGS[dir], exist_ok=True)