

SETTINGS = {
    "configs_dir": "configs",
    "logs_dir": "logs",
    "datasets_dir": "datasets",
    "models_dir": "models",
    "train_data_filename": "train_data.txt",
    "test_data_filename": "test_data.txt",
    "recurrent_types": ["LSTM", "GRU"],
    "datasets": ['cmc', 'persona_chat']
}

DEFAULTS = {
    "model_filename": "abyss.h5",
    "datasets": ['cmc', 'persona_chat'],
    "max_length": 256,
    "vocab_size": 256,
    "embedding_size": 100,
    "recurrent_units": 1024,
    "recurrent_layers": 1,
    "sample_size": 100000,
    "randomize_sample": True,
    "batch_size": 128,
    "epochs": 300,
    "learning_rate": 0.001,
    "recurrent_type": "LSTM",
    "dropout": 0.0,
    "recurrent_dropout": 0.0,
    "learning_rate_decay": 0.0,
    "gradient_clip": 0.0,
    "early_stopping_patience": 10,
    "checkpoint_save_weights_only": False,
    "checkpoint_save_freq": 'epoch',
    "checkpoint_verbose": True,
    "early_stopping_monitor": 'loss',
    "early_stopping_restore_best_weights": True,
    "tensorboard_write_graph": True,
    "tensorboard_update_freq": 'epoch',
    "reduce_lr_monitor": 'val_loss',
    "reduce_lr_factor": 0.1,
    "reduce_lr_patience": 10,
    "reduce_lr_min_lr": 1e-5,
    "reduce_lr_verbose": True
}
SETTINGS_LABELS = {key: key.replace('_', ' ').title() for key in SETTINGS}
DEFAULTS_LABELS = {key: key.replace('_', ' ').title() for key in DEFAULTS}
def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
VALIDATORS = {
    "model_filename": lambda s: s.endswith('.h5'),
    "datasets": lambda s: set(s.replace(" ", "").split(',')) <= set(['cmc', 'persona_chat']),
    "max_length": lambda s: s.isdigit(),
    "vocab_size": lambda s: s.isdigit(),
    "embedding_size": lambda s: s.isdigit(),
    "recurrent_units": lambda s: s.isdigit(),
    "recurrent_layers": lambda s: s.isdigit(),
    "sample_size": lambda s: s.isdigit(),
    "randomize_sample": lambda s: s.lower() in ['true', 'false'],
    "batch_size": lambda s: s.isdigit(),
    "epochs": lambda s: s.isdigit(),
    "learning_rate": lambda s: (s.replace('.', '', 1).isdigit() and float(s) >= 0),
    "recurrent_type": lambda s: s in ['LSTM', 'GRU'],
    "dropout": lambda s: (s.replace('.', '', 1).isdigit() and float(s) >= 0),
    "recurrent_dropout": lambda s: (s.replace('.', '', 1).isdigit() and float(s) >= 0),
    "learning_rate_decay": lambda s: (s.replace('.', '', 1).isdigit() and float(s) >= 0),
    "gradient_clip": lambda s: (s.replace('.', '', 1).isdigit() and float(s) >= 0) or s.lower() == 'none',
    "early_stopping_patience": lambda s: s.isdigit(),
    "checkpoint_save_weights_only": lambda s: s.lower() in ['true', 'false'],
    "checkpoint_save_freq": lambda s: s.lower() == 'epoch',
    "checkpoint_verbose": lambda s: s.lower() in ['true', 'false'],
    "early_stopping_monitor": lambda s: s.lower() == 'loss',
    "early_stopping_restore_best_weights": lambda s: s.lower() in ['true', 'false'],
    "tensorboard_write_graph": lambda s: s.lower() in ['true', 'false'],
    "tensorboard_update_freq": lambda s: s.lower() == 'epoch',
    "reduce_lr_monitor": lambda s: s.lower() == 'val_loss',
    "reduce_lr_factor": lambda s: (s.replace('.', '', 1).isdigit() and float(s) >= 0),
    "reduce_lr_patience": lambda s: s.isdigit(),
    "reduce_lr_min_lr": lambda s: is_float(s) and float(s) >= 0,
    "reduce_lr_verbose": lambda s: s.lower() in ['true', 'false'],
}
CONVERTERS = {
    "model_filename": str,  # Keep as string
    "datasets": lambda s: s.replace(" ", "").split(','),
    "max_length": int,
    "vocab_size": int,
    "embedding_size": int,
    "recurrent_units": int,
    "recurrent_layers": int,
    "sample_size": int,
    "randomize_sample": lambda s: s.lower() == 'true',
    "batch_size": int,
    "epochs": int,
    "learning_rate": float,
    "recurrent_type": str,  # Keep as string
    "dropout": float,
    "recurrent_dropout": float,
    "learning_rate_decay": float,
    "gradient_clip": lambda s: None if s.lower() == 'none' else float(s),
    "early_stopping_patience": int,
    "checkpoint_save_weights_only": lambda s: s.lower() == 'true',
    "checkpoint_save_freq": str,  # Keep as string
    "checkpoint_verbose": lambda s: True if s.lower() == 'true' else False,
    "early_stopping_monitor": str,  # Keep as string
    "early_stopping_restore_best_weights": lambda s: s.lower() == 'true',
    "tensorboard_write_graph": lambda s: s.lower() == 'true',
    "tensorboard_update_freq": str,  # Keep as string
    "reduce_lr_monitor": str,  # Keep as string
    "reduce_lr_factor": float,
    "reduce_lr_patience": int,
    "reduce_lr_min_lr": float,
    "reduce_lr_verbose": lambda s: s.lower() == 'true',
}

SETTINGS_VALIDATORS = {
    "configs_dir": lambda s: s.isalpha(),
    "logs_dir": lambda s: s.isalpha(),
    "datasets_dir": lambda s: s.isalpha(),
    "models_dir": lambda s: s.isalpha(),
    "train_data_filename": lambda s: s.endswith('.txt'),
    "test_data_filename": lambda s: s.endswith('.txt'),
    "recurrent_types": lambda s: set(s.replace(" ", "").split(',')) <= set(['LSTM', 'GRU']),
    "datasets": lambda s: set(s.replace(" ", "").split(',')) <= set(['cmc', 'persona_chat']),
}
LOG_FLAG = "Abyss_Log:"

BOX_1 = '╔╗╚╝═║'
