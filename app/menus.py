from os.path import join, basename
from glob import glob
from util import DataObject
from const import *
from lib import save_config, load_config
from ui import UI

settings = DataObject(SETTINGS)
defaults = DataObject(DEFAULTS)

class Menus():

    def get_menus(self, width=25, x_offset = 4, y_offset = 4, align='left'):


        config_files = glob(f"{settings.configs_dir}/*.json")

        main_menu_home_options_map = ['create_project', 'tune_project']
        main_menu_back_options_map = ['main_menu']
        choose_project_options_map = [basename(config_file) for config_file in config_files] if config_files else []
        project_options_menu_options_map = ['train', 'chat', 'model']

        menus = {
            'main_menu_home': {
                'header': APP_TITLE,
                'options': [SCREENS['create_project']['label']],
                'handler': lambda selection: {'active_screen': main_menu_home_options_map[selection]},
                'condition': lambda: self.state.active_screen == 'main_menu'
            },
            'main_menu_back': {
                'header': APP_TITLE,
                'options': [SCREENS['main_menu']['label']],
                'handler': lambda selection: {'active_screen': main_menu_back_options_map[selection]},
                'condition': lambda: self.state.active_screen != 'main_menu'
            },
            'choose_project_menu': {
                'header': MENUS['choose_project_menu']['label'],
                'options': choose_project_options_map,
                'handler': lambda selection: {
                    'config_file': choose_project_options_map[selection],
                    'configs': DataObject(load_config(join(settings.configs_dir, choose_project_options_map[selection]))),
                    'active_screen': 'project_details'
                },
                'condition': lambda: self.state.active_screen == 'main_menu' and config_files
            },
            'project_options_menu': {
                'header': MENUS['project_options_menu']['label'],
                'options': [ACTIONS[value]['label'] for value in ACTIONS],
                'handler': lambda selection: self.options_selection_handler(
                    project_options_menu_options_map[selection]),
                'condition': lambda: self.state.configs and self.state.config_file
            }
        }

        current_menus = []
        for key, menu in menus.items():
            if menu['condition']():
                menu['width'] = width

                if align == 'center':
                    menu['x'] = self.term.width // 2 - width // 2
                elif align == 'right':
                    menu['x'] = self.term.width - width - x_offset
                else:  # align == 'left':
                    menu['x'] = x_offset

                menu['y'] = y_offset
                y_offset += len(menu['options']) + 2
                current_menus.append(menu)

        return current_menus

