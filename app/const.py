


SAVE_FILE_FORM_FIELDS = {
    "filename": ""
}

SAVE_FILE_FORM_FIELD_LABELS = {
    "filename": "Name"
}

SAVE_FILE_FORM_FIELD_CONVERTERS = {
    "filename": lambda s: isinstance(s, str),
}

SAVE_FILE_FORM_FIELD_VALIDATORS = {
    "filename": lambda s: isinstance(s, str),
}
#!# Change this to Application Settings Defaults
SETTINGS = {
    "projects_dir": "configs",
    "logs_dir": "logs",
    "datasets_dir": "datasets",
    "models_dir": "models",
    "train_data_filename": "train_data.txt",
    "test_data_filename": "test_data.txt",
    "recurrent_types": ["LSTM", "GRU"],
    "datasets": ['cmc', 'persona_chat']
}

#!# Change this to Project Settings Defaults
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
#!# Change this to Project Settings Validators
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
#!# Change this to Project Settings Converters
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
#!# change this to application settings validators
SETTINGS_VALIDATORS = {
    "projects_dir": lambda s: s.isalpha(),
    "logs_dir": lambda s: s.isalpha(),
    "datasets_dir": lambda s: s.isalpha(),
    "models_dir": lambda s: s.isalpha(),
    "train_data_filename": lambda s: s.endswith('.txt'),
    "test_data_filename": lambda s: s.endswith('.txt'),
    "recurrent_types": lambda s: set(s.replace(" ", "").split(',')) <= set(['LSTM', 'GRU']),
    "datasets": lambda s: set(s.replace(" ", "").split(',')) <= set(['cmc', 'persona_chat']),
}

TUNING_SETTINGS_FORM_FIELDS  = {
    "vocab_size": 256,
    "datasets": [
        "cmc",
        "persona_chat"
    ],
    "batch_size" : 64,
    "sample_size" : 500000,
    "max_length" : 1024,
    "randomize_sample" : True
}

TUNING_SETTINGS_DEFAULTS  = {
    'hypermodel': None,
    'train_data': None,
    'test_data': None,
    'epochs': 15,
    'callbacks': [],
    'tuner_type': 'random',
    'max_trials': 10,
    'executions_per_trial': 1,
    'tuner_directory': 'tuner',
    'project_name': 'chatbot',
    'seed': 42,
    'objective': 'val_loss',
    'overwrite': False
}
TUNING_SETTINGS_LABELS = {key: key.replace('_', ' ').title() for key in TUNING_SETTINGS_DEFAULTS}
TUNING_SETTINGS_VALIDATORS = {
    "hypermodel": lambda s: isinstance(s, str),
    "train_data": lambda s: isinstance(s, str),
    "test_data": lambda s: isinstance(s, str),
    "epochs": lambda s: s.isdigit(),
    "callbacks": lambda s: isinstance(s, list),
    "tuner_type": lambda s: s.lower() in ['random', 'bayesian', 'hyperband'],
    "max_trials": lambda s: s.isdigit(),
    "executions_per_trial": lambda s: s.isdigit(),
    "tuner_directory": lambda s: isinstance(s, str),
    "project_name": lambda s: isinstance(s, str),
    "seed": lambda s: s.isdigit(),
    "objective": lambda s: isinstance(s, str),
    "overwrite": lambda s: s.lower() in ['true', 'false']
}

TUNING_SETTING_CONVERTERS = {
    "hypermodel": str,  # Keep as string
    "train_data": str,  # Keep as string
    "test_data": str,  # Keep as string
    "epochs": int,
    "callbacks": lambda s: s,  # Keep as is (list)
    "tuner_type": str,  # Keep as string
    "max_trials": int,
    "executions_per_trial": int,
    "tuner_directory": str,  # Keep as string
    "project_name": str,  # Keep as string
    "seed": int,
    "objective": str,  # Keep as string
    "overwrite": lambda s: s.lower() == 'true',
}


TUNING_SETTINGS_FORM_FIELDS  = {
    'epochs': 15,
    'tuner_type': 'random',
    'max_trials': 10,
    'executions_per_trial': 1,
    'tuner_directory': 'tuner',
    'project_name': 'chatbot',
    'seed': 42,
    'objective': 'val_loss',
    'overwrite': False
}

LOG_FLAG = "Abyss_Log:"

BOX_1 = '╔╗╚╝═║'
BOX_2 = '┌┐└┘─│'

CURSOR = '▏'


SCREENS = {
    'home': {'label': 'Abyss Terminal'},
    'create_project': {
        'label': 'Create New Project',
        'form': 'create_project_config_form'
    },
    'tune_project': {
        'label': 'Tune New Project',
        'form': 'tuning_settings_form'
    },
    'application_settings': {
        'label': 'Application Settings',
        'form': 'application_settings_form'
     },
    'project_details': {'label': 'Project Details'},
    'tuning_settings_detail': {'label': 'Tuning Details'}
}

ACTIONS = {
    'train': {
        'label': 'Train Model',
        'sub_proc': ['python', 'app', '--config', '{config_file}', '--train'],
        'callback': 'draw_training_progress_report'
    },
}

THREADS = {
    "screen_controller":{
        "required" : True
    },
    "draw_screen_buffer":{
        "required" : True
    },
    "sidebar_menu_controller":{
        "required" : True
    },
    "draw_training_progress_report":{
        "required" : False
    },
    "train":{
        "required" : False,
        "command":['python', 'app', '--config', '{config_file}', '--train']
    },
}

MENUS = {
    'create_menu': {
        'label':'Create New Project'
    },
    'choose_project_menu': {
        'label':'Load Existing Project'
    },
    'project_options_menu': {
        'label':'Project Options'
    },
    'application_menu': {
        'label':'Other'
    }
}

APP_TITLE = "Abyss"
DEBUG_PAUSE_RATE = 0
REFRESH_RATE = 0.15
GUTTER = 1

MENUS_WIDTH=28
MENUS_X=GUTTER
MENUS_Y=GUTTER
MENUS_ALIGN='left'

FORMS_WIDTH = 60
FORMS_X = MENUS_X + MENUS_WIDTH + GUTTER
FORMS_Y = MENUS_Y
FORMS_ALIGN = 'left'

REPORTS_WIDTH = 50
REPORTS_HEIGHT = 8
REPORTS_X = MENUS_X + MENUS_WIDTH + GUTTER
REPORTS_Y = MENUS_Y
REPORTS_ALIGN = 'left'