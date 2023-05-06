from os.path import isfile, join
import click
from lib import load_config, make_system_directories
from util import DataObject
from gui import GUI
from cli import CLI
from const import DEFAULTS, SETTINGS
from lang.en import HELP

settings = DataObject(SETTINGS)
defaults = DataObject(DEFAULTS)
options_help = DataObject(HELP)

@click.command()
@click.option('--model-filename', help=options_help.model_filename)
@click.option('--train-data', help=options_help.train_data)
@click.option('--test-data', help=options_help.test_data)
@click.option('--max-length', type=int, help=options_help.max_length)
@click.option('--batch-size', type=int, help=options_help.batch_size)
@click.option('--sample-size', type=int, help=options_help.sample_size)
@click.option('--randomize-sample', is_flag=True, help=options_help.randomize_sample)
@click.option('--epochs', type=int, help=options_help.epochs)
@click.option('--learning-rate', type=float, help=options_help.learning_rate)
@click.option('--learning-rate-decay', type=float, help=options_help.learning_rate_decay)
@click.option('--embedding-size', type=int, help=options_help.embedding_size)
@click.option('--recurrent-units', type=int, help=options_help.recurrent_units)
@click.option('--vocab-size', type=int, help=options_help.vocab_size)
@click.option('--early-stopping-patience', type=int, help=options_help.early_stopping_patience)
@click.option('--gradient-clip', type=float, help=options_help.gradient_clip)
@click.option('--logs-dir', help=options_help.logs_dir)
@click.option('--recurrent-layers', type=int, help=options_help.recurrent_layers)
@click.option('--recurrent-type', type=click.Choice(settings.recurrent_types), help=options_help.recurrent_type)
@click.option('--dropout', type=float, help=options_help.dropout)
@click.option('--recurrent-dropout', type=float, help=options_help.recurrent_dropout)
@click.option('--config', help=options_help.config)
@click.option('--save-config', help=options_help.save_config)
@click.option('--rebuild-model', is_flag=True, help=options_help.rebuild_model)
@click.option('--train', is_flag=True, help=options_help.train)
@click.option('--chat', is_flag=True, help=options_help.chat)
@click.option('--summary', is_flag=True, help=options_help.summary)
@click.option('--num-responses', type=int, help=options_help.num_responses)
@click.option('--no-gpu', is_flag=True, help=options_help.no_gpu)
@click.option('--transfer-weights', help=options_help.transfer_weights)
def main(**kwargs):
    if kwargs["config"]:
        config_path = kwargs.config if isfile(kwargs["config"]) else join(settings.configs_dir, kwargs["config"])
        config = load_config(config_path)
        args = DataObject(config)
        for key, value in kwargs.items():
            if value:
                setattr(args, key, None if value == "None" else value)
        CLI(args)
    else:
        gui = GUI()

if __name__ == "__main__":
    make_system_directories()
    main()
