from os.path import isfile, join, exists
from tensorflow.keras.models import load_model
from lib import save_config, build, train
from util import DataObject
from seq2seq import disable_gpu, transfer_weights, chat
from const import DEFAULTS, SETTINGS
from lang.en import HELP

settings = DataObject(SETTINGS)
defaults = DataObject(DEFAULTS)
options_help = DataObject(HELP)

def CLI(args, callbacks=[]):

    if hasattr(args, 'save_config'): #save_project_config
        save_config(vars(args), args.save_config)

    if hasattr(args, 'no_gpu'):
        disable_gpu()

    if hasattr(args, 'rebuild_model') or not exists(join(settings.models_dir, args.model_filename)):
        model = build(args)
    elif exists(join(settings.models_dir, args.model_filename)):
        model = load_model(join(settings.models_dir, args.model_filename))

    if hasattr(args, 'transfer_weights'):

        if isfile(args.transfer_weights):
            transfer_src = args.transfer_weights
        else:
            transfer_src = join(settings.models_dir, args.transfer_weights)

        transfer_weights(load_model(transfer_src))

    if hasattr(args, 'summary'):
        model.summary()

    if hasattr(args, 'chat'):
        chat(model, 1 if not hasattr(args, 'num_responses') else args.num_responses)

    if hasattr(args, 'train'):
        train(model, args, callbacks)

    if hasattr(args, 'tune'):
        train(model, args, callbacks)
