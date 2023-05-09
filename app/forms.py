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

FORMS_X = 30
FORMS_Y = 4
FORMS_WIDTH = 60
class Forms():
    def forms_controller(self):

        if self.state.active_screen == 'create_project':
            self.create_project_config_form()
        elif self.state.active_screen == 'tune_project':
            self.tuning_settings_form()
        elif self.state.active_screen == 'application_settings':
            self.application_settings_form()
        else:
            pass

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
        self.state.configs = self.form(fields, FORMS_X, FORMS_Y, FORMS_WIDTH, SCREENS['create_project']['label'])
        self.state.config_file = self.state.configs['name'] + '.json'
        config_filepath = join(settings.configs_dir, self.state.config_file)
        self.state.configs.pop('name')
        save_config(self.state.configs, config_filepath)
        self.state.active_screen = 'main_menu'

    def tuning_settings_form(self):
        fields = self.form_fields(TUNING_SETTINGS_FORM_FIELDS, TUNING_SETTINGS_LABELS, TUNING_SETTINGS_VALIDATORS)
        self.state.configs_tuning = self.form(fields, FORMS_X, FORMS_Y, FORMS_WIDTH, SCREENS['tune_project']['label'])
        self.state.active_screen = 'tuning_settings_detail'

    def application_settings_form(self):
        fields = self.form_fields(SETTINGS, SETTINGS_LABELS, SETTINGS_VALIDATORS)
        self.state.settings = self.form(fields, FORMS_X, FORMS_Y, FORMS_WIDTH, SCREENS['application_settings']['label'])
        config_filepath = join('~/', '.abyss')
        save_config(self.state.settings, config_filepath)
        self.state.active_screen = 'main_menu'
