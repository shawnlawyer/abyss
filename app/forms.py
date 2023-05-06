from os.path import join, basename
import threading
import subprocess
from time import sleep
from util import DataObject
from const import *
from lib import save_config, load_config
from ui import UI
from menus import Menus, MENUS
from lang.en import *

settings = DataObject(SETTINGS)
defaults = DataObject(DEFAULTS)


class Forms():
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