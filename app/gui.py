from os.path import join, basename, exists
from glob import glob
import threading
from tensorflow.keras.models import load_model
from util import DataObject
import seq2seq
from const import *
from lib import save_config, load_config
from os.path import join
import subprocess
import select
from ui import UI
import re

SCREENS = {
    "load_model": 0,
    "create_model": 1,
    "transfer_knowledge": 2
}

ACTIONS = {
    "train": 0,
    "chat": 1,
    "summary": 2,
    "view_train": 3,
    "view_chat": 4,
    "view_summary": 5,
    "view_progress": 6
}

SCREENS_LABELS = {key: key.replace('_', ' ').title() for key in SCREENS}
ACTIONS_LABELS = {key: key.replace('_', ' ').title() for key in ACTIONS}
ACTIONS_LABELS = {key: key.replace('_', ' ').title() for key in ACTIONS}
settings = DataObject(SETTINGS)
defaults = DataObject(DEFAULTS)
actions = DataObject(ACTIONS)
screens = DataObject(SCREENS)

APP_TITLE = "Abyss Dashboard"
MAIN_MENU_HEADER = "=== Options ==="
MAIN_MENU_OPTIONS = ["Load Model", "Create Model", "Transfer Knowledge",
                     "View Train", "View Chat", "View Summary", "View Progress"]
MAIN_MENU_OPTION_ROUTES = [w.lower().replace(' ', '_') for w in MAIN_MENU_OPTIONS]
MODEL_OPTIONS_MENU_HEADER = "=== Model Options ==="
MODEL_OPTIONS_MENU_OPTIONS = ["Train", "Chat", "Transfer Knowledge"]

class GUI(UI):
    def __init__(self):
        super().__init__()
        self.app_title = APP_TITLE

    def main(self):
        with self.term.fullscreen(), self.term.cbreak():
            while True:
                self.draw_dashboard()
                self.state.selection = self.main_menu()

                if self.state.selection == screens.transfer_knowledge:
                    self.transfer_knowledge_screen()

                elif self.state.selection == screens.create_model:
                    self.state.configs = self.model_config_form()
                    config_filepath = join(settings.configs_dir, self.state.configs['name'] + '.json')
                    self.state.configs.pop('name')
                    save_config(self.state.configs, config_filepath)

                elif self.state.selection == screens.load_model:
                    self.state.config_file = self.choose_model_menu()
                    self.state.configs = DataObject(load_config(join(settings.configs_dir, self.state.config_file)))
                    self.state.selection = self.model_options_menu()

                    if self.state.selection == actions.summary:
                        subprocess.run(["python", "app", "--config", self.state.config_file, "--summary", "--no-gpu"])
                    elif self.state.selection == actions.chat:
                        subprocess.run(["python", "app", "--config", self.state.config_file, "--chat", "--no-gpu"])
                    elif self.state.selection == actions.train:
                        subprocess.run(["python", "app", "--config", self.state.config_file, "--train"])

                self.state.selection = None
                self.draw_dashboard()

    def main_menu(self):

        header = "=== Options ==="
        options = ["Load Model", "Create Model", "Transfer Knowledge"]
        return self.menu(options, header, (self.term.width // 2) - 10, 5)

    def model_options_menu(self):

        header = "=== Model Options ==="
        options = ["Train", "Chat", "Transfer Knowledge"]
        return self.menu(options, header, (self.term.width // 2) - 10, 5)

    def choose_model_menu(self):
        config_files = glob(f"{settings.configs_dir}/*.json")
        if len(config_files) == 0:
            print("No config files found. Enter config manually.")
        else:
            header = "=== Select Config ==="
            options = [basename(config_file) for config_file in config_files]
            return options[self.menu(options, header, (self.term.width // 2) - 10, 5)]

    def model_config_form(self):
        fields = [{'key': 'name', 'prompt': 'Name: ', 'response': 'abyss', 'validator': lambda s: s.isalpha(),
                   'active': True}]
        fields.extend(self.form_fields(DEFAULTS, DEFAULTS_LABELS, VALIDATORS))
        return self.form(fields)

    def transfer_knowledge_screen(self):
        model_files = glob(f"{settings.models_dir}/*.h5")

        if len(model_files) == 0:
            print(self.term.home + self.term.clear + self.term.move_y(self.term.height // 2))
            print(self.term.center("No model files found."))
            self.term.inkey()
        else:
            while True:
                print(self.term.home + self.term.clear)
                print(self.term.center("\nAvailable models:"))
                for idx, model_file in enumerate(model_files, start=1):
                    print(self.term.center(f"{idx}. {basename(model_file)}"))
                print(self.term.center("Select a source model (enter the number): "))
                source_model_idx = self.term.inkey()
                print(self.term.center("Select a target model (enter the number): "))
                target_model_idx = self.term.inkey()

                if source_model_idx == target_model_idx:
                    print(self.term.center(
                        "Error: The same model has been chosen for both source and target. Please choose different models."))
                    self.term.inkey()
                else:
                    break

            source_model_path = model_files[int(source_model_idx) - 1]
            target_model_path = model_files[int(target_model_idx) - 1]

            if exists(source_model_path) and exists(target_model_path):
                print(self.term.center("Transferring weights from the source model to the target model..."))
                source_model = load_model(source_model_path)
                target_model = load_model(target_model_path)
                seq2seq.transfer_weights(source_model, target_model)
                target_model.save(target_model_path)
                print(self.term.center("Weights transferred successfully and the target model has been updated."))
                self.term.inkey()
            else:
                print(self.term.center("One or both model paths do not exist. Please check the paths and try again."))
                self.term.inkey()

if __name__ == "__main__":
    app = GUI()
    app.run()
