from os.path import join, basename, exists
from time import sleep
from glob import glob
import subprocess
from tensorflow.keras.models import load_model
from blessed import Terminal
from util import DataObject, float_or_none
import seq2seq
from const import *
from lang.en import HELP, CONFIG_FORM_LABELS
from lib import build, save_config, load_config
from bf import model_config_form


settings = DataObject(SETTINGS)
defaults = DataObject(DEFAULTS)
actions = DataObject(ACTIONS)
screens = DataObject(SCREENS)
config_form_labels = DataObject(CONFIG_FORM_LABELS)

term = Terminal()
def menu(options, header=None, x=0, y=0):
    selected = 0

    draw_dashboard()
    while True:
        if header:
            with term.location(x, y):
                print(header)
                for i, option in enumerate(options):
                    if i == selected:
                        print(term.move_x(x, i+1) + term.on_black(term.white(option)))
                    else:
                        print(term.move_x(x, i+1) + option)

        inp = term.inkey()
        if inp.code == term.KEY_UP:
            selected = max(0, selected - 1)
        elif inp.code == term.KEY_DOWN:
            selected = min(len(options) - 1, selected + 1)
        elif inp.code == term.KEY_ENTER:
            return selected
        elif inp.code == term.KEY_ESCAPE:
            quit()

def draw_dashboard():
    print(term.home + term.clear)
    # AIbyss Title
    print(term.move_y(2) + term.center(('AIbyss Dashboard')))
    print(term.move_y(term.height // 4))

    with term.location(0, term.height - 1):
        print(term.center('Use Arrow Keys to navigate and Enter to select'), end='')
def main():
    with term.fullscreen(), term.cbreak():

        while True:
            selection = ''
            draw_dashboard()
            selection = main_menu()
            if selection == screens.transfer_knowledge:
                transfer_knowledge_screen()
                continue

            if selection == screens.create_model:
                configs = model_config_form()
                config_filepath = join(settings.configs_dir, configs['name'] + '.json')
                configs.pop('name')
                save_config(configs, config_filepath)
                continue

            if selection == screens.load_model: # screens.choose_model_config
                config_file = choose_model_menu()
                configs = DataObject(load_config(join(settings.configs_dir, config_file)))


                selection = model_options_menu()

                if selection == actions.summary:
                    subprocess.run(["python", "main.py", "--config", config_file, "--summary"])


                if selection == actions.chat:
                    subprocess.run(["python", "main.py", "--config", config_file, "--chat", "--no-gpu"])


                if selection == actions.train:
                    subprocess.run(["python", "main.py", "--config", config_file, "--train"])
            sleep(10)
            selection = ''
            draw_dashboard()
            selection = main_menu()

def main_menu():
    header = "=== Options ==="
    options = ["Load Model", "Create Model", "Transfer Knowledge"]
    return menu(options, header, (term.width // 2) - 10, 5)

def model_options_menu():
    header = "=== Model Options ==="
    options = ["Train", "Chat", "Transfer Knowledge"]
    return menu(options, header, (term.width // 2) - 10, 5)

def choose_model_menu():
    config_files = glob(f"{settings.configs_dir}/*.json")
    if len(config_files) == 0:
        print("No config files found. Enter config manually.")
    else:
        header = "=== Select Config ==="
        options = [basename(config_file) for config_file in config_files]
        return options[menu(options, header, (term.width // 2) - 10, 5)]

def transfer_knowledge_screen():
    model_files = glob(f"{settings.models_dir}/*.h5")

    if len(model_files) == 0:
        print(term.home + term.clear + term.move_y(term.height // 2))
        print(term.center("No model files found."))
        term.inkey()
    else:
        while True:
            print(term.home + term.clear)
            print(term.center("\nAvailable models:"))
            for idx, model_file in enumerate(model_files, start=1):
                print(term.center(f"{idx}. {basename(model_file)}"))
            print(term.center("Select a source model (enter the number): "))
            source_model_idx = term.inkey()
            print(term.center("Select a target model (enter the number): "))
            target_model_idx = term.inkey()

            if source_model_idx == target_model_idx:
                print(term.center(
                    "Error: The same model has been chosen for both source and target. Please choose different models."))
                term.inkey()
            else:
                break

        source_model_path = model_files[int(source_model_idx) - 1]
        target_model_path = model_files[int(target_model_idx) - 1]

        if exists(source_model_path) and exists(target_model_path):
            print(term.center("Transferring weights from the source model to the target model..."))
            source_model = load_model(source_model_path)
            target_model = load_model(target_model_path)
            seq2seq.transfer_weights(source_model, target_model)
            target_model.save(target_model_path)
            print(term.center("Weights transferred successfully and the target model has been updated."))
            term.inkey()
        else:
            print(term.center("One or both model paths do not exist. Please check the paths and try again."))
            term.inkey()

def configs_form(args):
    configs = generate_input_fields(args, DEFAULTS, CONFIG_FORM_LABELS)
    config_filename = (input("Enter a name to save this config (without aibyss.json extension): ") or "aibyss") + ".json"
    config_filepath = join(settings.configs_dir, config_filename)
    save_config(configs, config_filepath)
    print(f"Config saved to: {config_filepath}")
    return configs

def generate_input_fields(args, fields, labels):
    configs = {}
    for key, field in fields.items():
        prompt = labels[key]
        default_value = getattr(args, key)
        if key == 'datasets':
            input_value = (input(prompt.format(','.join(default_value))) or ','.join(default_value)).split(',')
        elif key == 'randomize_sample':
            input_value = bool(int(input(prompt.format(int(default_value))) or default_value))
        elif key == 'gradient_clip':
            input_value = float_or_none(input(prompt.format(default_value)) or default_value)
        else:
            input_value = type(default_value)(input(prompt.format(default_value)) or default_value)
        configs[key] = input_value
    return configs




if __name__ == "__main__":
    main()
