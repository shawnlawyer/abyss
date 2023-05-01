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
from ui import UI

settings = DataObject(SETTINGS)
defaults = DataObject(DEFAULTS)

SCREENS = {
    'main_menu': {'label': 'Main Menu'},
    'create_project': {'label': 'Create New Project'},
    'load_project': {'label': 'Load Project'},
    'project_options_menu': {'label': 'Project Options'},
    'choose_project_menu': {'label': 'Choose Project'},
    'train_model': {'label': 'Train Model'},
    'chat_with_model': {'label': 'Chat With Model'},
    'model_summary': {'label': 'Model Summary'}
}

APP_TITLE = "Abyss"
class GUI(UI):
    def __init__(self):
        super().__init__()
        self.app_title = APP_TITLE
    def main(self):
        with self.term.fullscreen(), self.term.cbreak():
            active_screen = None
            self.draw_screen()

            while True:
                if active_screen != self.state.active_screen:
                    active_screen = self.state.active_screen
                    self.draw_screen()
    def draw_screen(self):
        self.draw_layout()
        if self.state.active_screen in [None,'main_menu']:
            self.main_menu()
        elif self.state.active_screen == 'create_project':
            self.create_project_config_form()
        elif self.state.active_screen == 'project_options_menu': # this is really opening a model project
            self.project_options_menu()
        elif self.state.active_screen == 'load_project': # this is really opening a model project
            self.choose_project_menu()
        elif self.state.active_screen == 'model_summary':
            subprocess.run(["python", "app", "--config", self.state.config_file, "--summary", "--no-gpu"])
        elif self.state.active_screen == 'chat_with_model':
            subprocess.run(["python", "app", "--config", self.state.config_file, "--chat", "--no-gpu"])
        elif self.state.active_screen == 'train_model':
            subprocess.run(["python", "app", "--config", self.state.config_file, "--train"])
    def draw_layout(self):
        print(self.term.home + self.term.clear)
        with self.term.location((self.term.width // 5) + 2,2):
            print(self.app_title)

        with self.term.location(0, self.term.height - 1):
            print(self.term.center('Arrow Keys to Navigate - Enter to Select - ESC to Exit'), end='')

    def main_menu(self):
        header = SCREENS['main_menu']['label']

        config_files = glob(f"{settings.configs_dir}/*.json")
        if len(config_files) != 0:
            options_map = ['create_project', 'load_project']
        else:
            options_map = ['create_project']
        options = [SCREENS[value]['label'] for value in options_map]
        position_x = (self.term.width // 5)
        position_y = 4
        selection = self.menu(options, header, position_x, position_y)
        self.state.active_screen = options_map[selection]

    def choose_project_menu(self):
        config_files = glob(f"{settings.configs_dir}/*.json")
        header = SCREENS['choose_project_menu']['label']
        options = [basename(config_file) for config_file in config_files]
        position_x = (self.term.width // 5)
        position_y = 4
        selection = self.menu(options, header, position_x, position_y)
        self.state.config_file = options[selection]
        self.state.configs = DataObject(load_config(join(settings.configs_dir, self.state.config_file)))
        self.state.active_screen = 'project_options_menu'

    def project_options_menu(self):
        header = SCREENS['project_options_menu']['label']
        options_map = ['train_model', 'chat_with_model', 'model_summary']
        options = [SCREENS[value]['label'] for value in options_map]
        position_x = (self.term.width // 5)
        position_y = 4
        selection = self.menu(options, header, position_x, position_y)
        self.state.active_screen = options_map[selection]

    def create_project_config_form(self):
        fields = [
            {
                'key': 'name',
                'prompt': 'Name: ',
                'response': 'abyss',
                'validator': lambda s: s.isalpha(),
                'active': True
             }
        ]

        fields.extend(self.form_fields(DEFAULTS, DEFAULTS_LABELS, VALIDATORS))
        self.state.configs = self.form(fields)
        self.state.config_file = self.state.configs['name'] + '.json'
        config_filepath = join(settings.configs_dir, self.state.config_file)
        self.state.configs.pop('name')
        save_config(self.state.configs, config_filepath)
        self.state.active_screen = 'project_options_menu'

if __name__ == "__main__":
    app = GUI()
    app.run()
