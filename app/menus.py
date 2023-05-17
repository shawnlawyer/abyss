import time
from os.path import join, basename
from glob import glob
from util import DataObject
from const import *
from lib import load_config
from input import MenuItem, SeparatorMenuItem

settings = DataObject(SETTINGS)
defaults = DataObject(DEFAULTS)

class Menus():

    def sidebar_menu_controller(self, thread=None):
        while not thread.stop_event.is_set():
            menus = self.get_menus()
            menu = {'header':'Menu', 'options':[]}
            for value in menus:
                menu['options'].append(SeparatorMenuItem(value['header']))
                menu['options'].extend(value['options'])

            self.state.sidebar_menu = self.set_sidebar_screen_location(menu, MENUS_WIDTH, MENUS_X, MENUS_Y, MENUS_ALIGN)
            self.state.input_handlers['sidebar_menu'] = self.sidebar_menu_key_handler
            self.handle_sidebar_menu()

    def get_menus(self):
        config_files = glob(f"{settings.projects_dir}/*.json")
        create_menu_options_map = ['create_project', 'tune_project']
        application_menu_options_map = ['application_settings']
        choose_project_options_map = [basename(config_file) for config_file in config_files] if config_files else []
        project_training_menu_options_map = ['restart_training']
        project_options_menu_options_map = ['train']

        def handle_change_active_screen(selection):
            state = {'active_screen': selection}
            self.state.update(state)

        def handle_choose_project_menu(selection):
            state = {
                'config_file': selection,
                'configs': load_config(join(settings.projects_dir, selection)),
                'active_screen': 'project_details'
            }
            self.state.update(state)

        def handle_project_options_menu(selection):

            key = selection
            thread = self.thread(key)
            callback = None
            callback_thread = None
            if 'callback' in ACTIONS[key]:
                callback = ACTIONS[key]['callback']
                callback_thread = self.thread(ACTIONS[key]['callback'])

            if thread.can_start():
                thread.start()
                if callback_thread:
                    if callback_thread.can_start():
                        callback_thread.start()
            else:
                thread.restart()
                if callback_thread:
                    callback_thread.restart()

        menus = {

            'choose_project_menu': {
                'header': MENUS['choose_project_menu']['label'],
                'options': [MenuItem(option, handle_choose_project_menu, option) for option in
                            choose_project_options_map],
                'condition': lambda: config_files
            },
            'project_options_menu': {
                'header': MENUS['project_options_menu']['label'],
                'options': [MenuItem(ACTIONS[value]['label'], handle_project_options_menu, value) for value in project_options_menu_options_map],
                'condition': lambda: self.state.configs and self.state.config_file
            },
            'project_training_options_menu': {
                'header': MENUS['project_training_menu']['label'],
                'options': [MenuItem(ACTIONS[value]['label'], handle_project_options_menu, value) for value in project_training_menu_options_map],
                'condition': lambda: self.thread('train').is_alive()
            },
            'create_menu': {
                'header': MENUS['create_menu']['label'],
                'options': [MenuItem(SCREENS[value]['label'], handle_change_active_screen, value) for value in
                            create_menu_options_map],
                'condition': lambda: True
            },
            'application_menu': {
                'header': MENUS['application_menu']['label'],
                'options': [MenuItem(SCREENS[value]['label'], handle_change_active_screen, value) for value in application_menu_options_map],
                'condition': lambda: True
            }
        }

        current_menus = []
        for key, menu in menus.items():
            if menu['condition']():
                current_menus.append(menu)

        return current_menus

    def set_sidebar_screen_location(self, menu, width=25, x=1, y=1, align='left'):

        menu['width'] = width

        if align == 'center':
            menu['x'] = self.term.width // 2 - width // 2
        elif align == 'right':
            menu['x'] = self.term.width - width - x
        else:  # align == 'left':
            menu['x'] = x

        menu['y'] = y

        return menu


    def handle_sidebar_menu(self):
        menu = self.state.sidebar_menu
        while True:
            lines = []
            for idx, item in enumerate(self.state.sidebar_menu['options']):

                    if isinstance(item, SeparatorMenuItem):
                        lines.append(str(SeparatorMenuItem()))
                    lines.append(str(item))
                    if isinstance(item, SeparatorMenuItem):
                        lines.append(str(SeparatorMenuItem()))
            lines = self.add_border(menu['header'], '\n'.join(lines), menu['width'], menu.get('height', len('\n'.join(lines).split('\n')) + 1 ))
            self.write_to_screen_buffer(lines, menu['x'], menu['y'])

            action = self.handle_key_input()
            self.term.print_buffer()
            if action == 'enter':
                return


    def add_padding(self, text, width, pad=' '):
        padding_needed = width - len(text)
        left_padding = padding_needed // 2
        right_padding = padding_needed - left_padding
        return pad * left_padding + text + pad * right_padding
