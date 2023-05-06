from os.path import join, basename
from glob import glob
from util import DataObject
from const import *
from lib import save_config, load_config
from ui import UI

settings = DataObject(SETTINGS)
defaults = DataObject(DEFAULTS)

class Menus():
    # Your GUI class code...
    state = []
    def generate_main_menu(self):
        if self.state.active_screen != 'main_menu':
            options_map = ['main_menu']
            handler = lambda selection: {'active_screen': options_map[selection]}
            return {
                'menu': 'main_menu',
                'options_map': ['main_menu'],
                'options': [SCREENS['main_menu']['label']],
                'header': APP_TITLE,
                'width': 25,
                'x': self.term.width // 2 - 25 // 2,
                'y': 4
            }, handler

        options_map = ['create_project']
        handler = lambda selection: {'active_screen': options_map[selection]}
        return {
            'menu': 'main_menu',
            'options_map': ['create_project'],
            'options': [SCREENS['create_project']['label']],
            'header': APP_TITLE,
            'width' : 25,
            'x':  self.term.width // 2 - 25 // 2,
            'y': 4
        }, handler

    # Your GUI class code...

    def generate_choose_project_menu(self):

        if self.state.active_screen != 'main_menu':
            return None, None

        config_files = glob(f"{settings.configs_dir}/*.json")
        if config_files:
            project_names = [basename(config_file) for config_file in config_files]
            handler = lambda selection: {
                'config_file': project_names[selection],
                'configs': DataObject(load_config(join(settings.configs_dir, project_names[selection]))),
                'active_screen': 'project_details'
            }
            return {
                'menu': 'choose_project_menu',
                'options': project_names,
                'header': MENUS['choose_project_menu']['label'],
                'width' : 25,
                'x': self.term.width // 2 - 25 // 2,
                'y': 8
            }, handler

    def generate_project_options_menu(self):
        if self.state.configs and self.state.config_file:
            options_map = ['train', 'chat', 'model']
            handler = lambda selection: self.options_selection_hander(options_map[selection])
            return {
                'menu': 'project_actions_menu',
                'options_map': options_map,
                'options': [ACTIONS[value]['label'] for value in ACTIONS],
                'header': MENUS['project_options_menu']['label'],
                'width' : 25,
                'x': self.term.width // 2 - 25 // 2,
                'y': 8
            }, handler

        return None, None
