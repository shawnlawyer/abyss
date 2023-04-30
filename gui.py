from os.path import join, basename, exists
from time import sleep
from glob import glob
import subprocess
from tensorflow.keras.models import load_model
from blessed import Terminal
from util import DataObject
import seq2seq
from const import *
from lib import save_config, load_config
import time

settings = DataObject(SETTINGS)
defaults = DataObject(DEFAULTS)
actions = DataObject(ACTIONS)
screens = DataObject(SCREENS)

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
    # Abyss Title
    print(term.move_y(2) + term.center(('Abyss Dashboard')))
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

def form_fields(values, labels, validators):
    fields = []

    for key in values:
        value = values[key]
        if isinstance(value, list):  # Convert list to comma-separated string
            value = ', '.join(value)
        fields.append({'key':key, 'prompt': labels[key] + ": ", 'response': str(value), 'validator':validators[key], 'active': False})
    return fields

def draw_form(fields):
    for idx, field in enumerate(fields):
        if field['active']:
            # Toggle the display of the cursor character.
            if time.time() % 1 < 0.5:
                line = term.reverse + field['prompt'] + term.normal + field['response'] + '|'
            else:
                line = term.reverse + field['prompt'] + term.normal + field['response']
        else:
            line = field['prompt'] + field['response']

        if not field['validator'](field['response']):
            line += term.red(f'  Invalid input for field "{field["prompt"]}"!')

        print(line)

def model_config_form():
    fields=[{'key':'name', 'prompt': 'Name: ', 'response': 'abyss', 'validator': lambda s: s.isalpha(), 'active': True}]
    fields.extend(form_fields(DEFAULTS, DEFAULTS_LABELS, VALIDATORS))
    return form(fields)

def form(fields):
    current_field = 0
    with term.cbreak(), term.hidden_cursor():
        print(term.home + term.clear)
        draw_form(fields)
        while True:
            key = term.inkey(timeout=0.1)  # Lower timeout for smoother blinking.
            if not key and not key.is_sequence:
                print(term.home + term.clear)
                draw_form(fields)
                continue
            if key.is_sequence:
                if key.name == 'KEY_ENTER':
                    invalid_fields = [field['prompt'] for field in fields if not field['validator'](field['response'])]
                    if invalid_fields:
                        print(f'These fields have invalid inputs: {", ".join(invalid_fields)}')
                    else:
                        values = {}
                        for field in fields:
                            values[field['key']] = field['response']
                        converted_dict = {}
                        for key, value in values.items():
                            if key in CONVERTERS:
                                try:
                                    converted_dict[key] = CONVERTERS[key](value)
                                except Exception as e:
                                    print(f"Error converting key {key}: {e}")
                            else:
                                print(f"No converter found for key {key}. Keeping value as is.")
                                converted_dict[key] = value
                        return converted_dict

                elif key.name == 'KEY_UP':
                    if current_field > 0:
                        fields[current_field]['active'] = False
                        current_field -= 1
                        fields[current_field]['active'] = True
                elif key.name == 'KEY_DOWN':
                    if current_field < len(fields) - 1:
                        fields[current_field]['active'] = False
                        current_field += 1
                        fields[current_field]['active'] = True
                elif key.name == 'KEY_BACKSPACE':
                    fields[current_field]['response'] = fields[current_field]['response'][:-1]
            else:
                fields[current_field]['response'] += key
            print(term.home + term.clear)
            draw_form(fields)




if __name__ == "__main__":
    main()
