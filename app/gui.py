from os.path import join, basename, exists
import re
import json
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
from time import sleep
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
import threading
import time

class GUI(UI):
    def __init__(self):
        super().__init__()
        self.app_title = APP_TITLE
        self.procs = {}  # A dictionary to store subprocesses
        self.proc_outputs = {}  # A dictionary to store outputs
        self.proc_progress = {}  # A dictionary to store progress
        self.timer_thread = None
        self.timer_interval = 1 # Update the screen every 1 second

    def main(self):
        with self.term.fullscreen(), self.term.cbreak(), self.term.hidden_cursor():
            active_screen = None
            self.draw_screen()

            # Start the timer thread
            self.timer_thread = threading.Thread(target=self.timer_loop)
            self.timer_thread.start()

            while True:
                if active_screen != self.state.active_screen:
                    active_screen = self.state.active_screen
                    self.draw_screen()

    def timer_loop(self):
        while True:
            time.sleep(self.timer_interval)
            self.draw_screen()

    def draw_screen(self):
        self.draw_layout()

        # Print the boxes
        if self.state.active_screen in [None, 'main_menu']:
            self.main_menu()
        elif self.state.active_screen == 'create_project':
            self.create_project_config_form()
        elif self.state.active_screen == 'project_options_menu':
            self.project_options_menu()
        elif self.state.active_screen == 'load_project':
            self.choose_project_menu()



    def do_actions(self, action):
        if action == 'summary' and 'summary' not in self.procs:
            self.run_subprocess('summary', ["python", "app", "--config", self.state.config_file, "--summary", "--no-gpu"])
        elif action == 'chat' and 'chat' not in self.procs:
            self.run_subprocess('chat', ["python", "app", "--config", self.state.config_file, "--chat", "--no-gpu"])
        elif action == 'train' and 'train' not in self.procs:
            self.run_subprocess('train', ["python", "app", "--config", self.state.config_file, "--train"])

    def run_subprocess(self, key, cmd):
        self.procs[key] = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.proc_outputs[key] = []
        threading.Thread(target=self.capture_output, args=(key,)).start()

    def capture_output(self, key):
        while True:

            sleep(1)
            output = self.procs[key].stdout.readline().decode().strip()
            if output == '' and self.procs[key].poll() is not None:
                continue
            if key == 'summary':
                self.proc_outputs[key].append(output)
                self.display_output_thread(key, 40, 20)
            elif key == 'chat':
                self.proc_outputs[key].append(output)
                self.display_output_thread(key, 40, 20)
            elif key == 'train':
                if LOG_FLAG in output:
                    self.proc_outputs[key].append(output.replace(LOG_FLAG,''))
                    self.display_output_thread(key, 40, 20)

    def display_output(self, key, width, height):
        box_height = self.term.height
        text = join(self.proc_outputs[key][-1])

        width = 40
        height = 1
        x = (self.term.width // 2) - (width // 2)
        y = self.term.height - height - 5

        if key == 'train':
            training_info_data = self.proc_outputs[key][-1]
            width = 40
            height = 8
            x = (self.term.width // 5) * 3 - 2
            y = 4
            training_info_report = self.json_to_report(training_info_data)
            print(self.term.home)
            self.draw_box(key, '\n'.join(training_info_report), width, height, x, y)

    def display_output_thread(self, key, box_width=40, box_height=20):
        threading.Thread(target=self.display_output, args=(key, box_width, box_height)).start()

    def draw_layout(self):
        self.term.home()
        self.term.clear()
        with self.term.location((self.term.width // 5) + 2,2):
            print(self.app_title)

        with self.term.location(0, self.term.height - 1):
            print(self.term.center('Arrow Keys to Navigate - Enter to Select - ESC to Exit'), end='')

    def main_menu(self):
        menus = []

        config_files = glob(f"{settings.configs_dir}/*.json")
        #if len(config_files) == 0:
        options_map = ['create_project']
        #else:
            #options_map = ['create_project', 'load_project']

        header = SCREENS['main_menu']['label']
        options = [SCREENS[value]['label'] for value in options_map]
        position_x = (self.term.width // 5)
        position_y = 4
        menus.append({'menu':'main', 'options_map':options_map, 'options':options, 'header':header, 'x':position_x, 'y':position_y})

        choose_project_menu = None
        if len(config_files) != 0:
            config_files = glob(f"{settings.configs_dir}/*.json")
            header = SCREENS['choose_project_menu']['label']
            options = [basename(config_file) for config_file in config_files]
            position_x = (self.term.width // 5)
            position_y = 10
            choose_project_menu =  len(menus)
            menus.append({'menu':'projects', 'options': options, 'header': header, 'x': position_x, 'y': position_y})

        actions_menu = None
        if self.state.configs and self.state.config_file:
            options_map = ['train', 'chat', 'model']
            header = SCREENS['project_options_menu']['label']
            options = [SCREENS[value]['label'] for value in ['train_model', 'chat_with_model', 'model_summary']]
            position_x = (self.term.width // 5) * 2
            position_y = 4
            actions_menu =  len(menus)
            menus.append(
                {'menu':'project_options','options_map': options_map, 'options': options, 'header': header, 'x': position_x, 'y': position_y})
            actions_menu = 1

        menu_id, selection = self.menus(menus)
        if menu_id == 0:
            self.state.active_screen = menus[menu_id]['options_map'][selection]
        elif menus[menu_id]['menu'] == 'projects':
            self.state.config_file = menus[menu_id]['options'][selection]
            self.state.configs = DataObject(load_config(join(settings.configs_dir, self.state.config_file)))
            self.draw_screen()
        elif menus[menu_id]['menu'] == 'project_options':
            self.do_actions(menus[menu_id]['options_map'][selection])
            self.draw_screen()

    def choose_project_menu(self):

        menus = []
        config_files = glob(f"{settings.configs_dir}/*.json")
        header = SCREENS['choose_project_menu']['label']
        options = [basename(config_file) for config_file in config_files]
        position_x = (self.term.width // 5)
        position_y = 4
        menus = [{'options': options, 'header': header, 'x': position_x, 'y': position_y}]

        menu_id, selection = self.menus(menus)
        self.state.config_file = menus[menu_id]['options'][selection]
        self.state.configs = DataObject(load_config(join(settings.configs_dir, self.state.config_file)))
        self.state.active_screen = 'main_menu'

    def project_options_menu(self):
        header = SCREENS['project_options_menu']['label']
        options_map = ['train_model', 'chat_with_model', 'model_summary']
        options = [SCREENS[value]['label'] for value in options_map]
        position_x = (self.term.width // 5) * 2
        position_y = 4
        menus = [{'options_map': options_map, 'options': options, 'header': header, 'x': position_x, 'y': position_y}]
        menu_id, selection = self.menus(menus)
        self.do_actions(menus[menu_id]['options_map'][selection])
        self.state.active_screen = 'main_menu'

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
        self.state.configs = self.form(fields, (self.term.width // 2)-40, 2, 80, SCREENS['create_project']['label'])
        self.state.config_file = self.state.configs['name'] + '.json'
        config_filepath = join(settings.configs_dir, self.state.config_file)
        self.state.configs.pop('name')
        save_config(self.state.configs, config_filepath)
        self.state.active_screen = 'main_menu'

if __name__ == "__main__":
    app = GUI()
    app.run()
