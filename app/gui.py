from os.path import join, basename
from glob import glob
from util import DataObject
from const import *
from lib import save_config, load_config
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
ACTIONS = {
    'summary': {
        'sub_proc': ['python', 'app', '--config', '{config_file}', '--summary', '--no-gpu'],
        'callback': 'display_output'
    },
    'chat': {
        'sub_proc': ['python', 'app', '--config', '{config_file}', '--chat', '--no-gpu'],
        'callback': 'display_output'
    },
    'train': {
        'sub_proc': ['python', 'app', '--config', '{config_file}', '--train'],
        'callback': 'draw_training_progress_report'
    },
}

MENUS = {
    'main_menu': 'generate_main_menu',
    'choose_project_menu': 'generate_choose_project_menu',
    'project_actions_menu': 'generate_project_actions_menu'
}
APP_TITLE = "Abyss"
import threading
import subprocess
from time import sleep

class ThreadedSubprocessMixin:
    log_flag = LOG_FLAG
    procs = {}
    proc_outputs = {}
    proc_progress = {}

    def display_output(self, key, width, height):
        if len(self.proc_outputs[key]) == 0:
            return
    def capture_output(self, key, log_flag=LOG_FLAG):
        while True:
            output = self.procs[key].stdout.readline().decode().strip()

            if output == '' and self.procs[key].poll() is not None:
                continue
            if self.log_flag in output:
                self.proc_outputs[key] = output.replace(log_flag,'')

    def display_output_thread(self, target):
        threading.Thread(target=target).start()

    def run_subprocess(self, key, cmd):
        self.procs[key] = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.proc_outputs[key] = '{}'
        threading.Thread(target=self.capture_output, args=(key,)).start()

class GUI(UI, ThreadedSubprocessMixin):
    # Your GUI class code...

    def __init__(self):
        super().__init__()
        self.app_title = APP_TITLE
        self.menus = MENUS
        self.log_flag = LOG_FLAG
        self.timer_thread = threading.Thread(target=self.timer_loop)
        self.timer_thread.start()

    def draw_screen(self):
        self.draw_layout()

        # Print the boxes
        if self.state.active_screen in [None, 'main_menu']:
            self.draw_current_state_menus()
        if self.state.active_screen == 'create_project':
            self.create_project_config_form()

    def display_output(self, key):
        if key == 'train':
            self.draw_training_progress_report()
    def draw_training_progress_report(self):
        loading = ''
        while True:
            if loading == '':
                loading = '.'
            elif loading == '.':
                loading = '..'
            elif loading == '..':
                loading = '...'
            else:
                loading = ''
            if len(self.proc_outputs['train']) == 0:
                training_info_report = f"Loading Model:{self.state.configs.model_filename}\nOne Moment{loading}"
            else:
                training_info_data = self.proc_outputs['train']
                training_info_report = '\n'.join(self.json_to_report(training_info_data))

            box_height = self.term.height
            width = 40
            height = 8
            x = (self.term.width // 5) * 3 - 3
            y = 2

            self.draw_box('Training Progress', training_info_report, width, height, x, y)
            sleep(1)

    def generate_main_menu(self):
        handler = lambda selection: {'active_screen': ['create_project'][selection]}
        return {
            'menu': 'main_menu',
            'options_map': ['create_project'],
            'options': [SCREENS['create_project']['label']],
            'header': SCREENS['main_menu']['label'],
            'width' : 25,
            'x': (self.term.width // 5),
            'y': 2
        }, handler

    def generate_choose_project_menu(self):
        config_files = glob(f"{settings.configs_dir}/*.json")
        if config_files:
            project_names = [basename(config_file) for config_file in config_files]
            handler = lambda selection: {
                'config_file': project_names[selection],
                'configs': DataObject(load_config(join(settings.configs_dir, project_names[selection])))
            }
            return {
                'menu': 'choose_project_menu',
                'options': project_names,
                'header': SCREENS['choose_project_menu']['label'],
                'width' : 25,
                'x': (self.term.width // 5),
                'y': 10
            }, handler
        return None

    def generate_project_actions_menu(self):
        if self.state.configs and self.state.config_file:
            options_map = ['train', 'chat', 'model']
            handler = lambda selection: self.do_actions(options_map[selection])
            return {
                'menu': 'project_actions_menu',
                'options_map': options_map,
                'options': [SCREENS[value]['label'] for value in ['train_model', 'chat_with_model', 'model_summary']],
                'header': SCREENS['project_options_menu']['label'],
                'width' : 25,
                'x': (self.term.width // 5) * 2,
                'y': 2
            }, handler
        return None

    def do_actions(self, key):
        if key in self.procs:
            return

        command = [arg.format(config_file=self.state.config_file) for arg in ACTIONS[key]['sub_proc']]
        self.run_subprocess(key, command)
        if 'callback' in ACTIONS[key]:
            gen_func = getattr(self, ACTIONS[key]['callback'])
            self.display_output_thread(gen_func)


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
    def draw_layout(self):
        print(self.term.home() + self.term.clear())
        with self.term.location((self.term.width // 5) + 2,2):
            print(self.app_title)

        with self.term.location(0, self.term.height - 1):
            print(self.term.center(f'Arrow Keys to Navigate - Enter to Select - ESC to Exit'), end='')
