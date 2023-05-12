from time import sleep
from os.path import join, basename
from glob import glob
from util import DataObject
from const import *
from lib import load_config

settings = DataObject(SETTINGS)
defaults = DataObject(DEFAULTS)

class MenuItem:
    def __init__(self, label, handler, value=None):
        self.label = label
        self.handler = handler
        self.value = value
        self.selected = False

    def __str__(self):
        prefix = ' * ' if self.selected else ' - '
        return prefix + self.label

class SeparatorMenuItem:
    def __init__(self, label=''):
        self.label = label
        self.handler = None
        self.selected = False

    def __str__(self):
        return ' ' + self.label


class Menus():

    def sidebar_menu_controller(self, thread=None):
        while not thread.stop_event.is_set():
            menus = self.get_menus()
            menu = {'header':'Menu', 'options':[]}
            for value in menus:
                menu['options'].append(SeparatorMenuItem(value['header']))
                menu['options'].extend(value['options'])

            self.state.sidebar_menu = self.set_sidebar_screen_location(menu, MENUS_WIDTH, MENUS_X, MENUS_Y, MENUS_ALIGN)
            self.handle_sidebar_menu()

    def get_menus(self):
        config_files = glob(f"{settings.projects_dir}/*.json")
        create_menu_options_map = ['create_project', 'tune_project']
        application_menu_options_map = ['application_settings']
        choose_project_options_map = [basename(config_file) for config_file in config_files] if config_files else []
        project_options_menu_options_map = ACTIONS #['train', 'chat', 'model']

        def handle_change_active_screen(selection):
            state = {'active_screen': selection}
            self.state.update(state)

        def handle_choose_project_menu(selection):
            state = {
                'config_file': selection,
                'configs': DataObject(load_config(join(settings.projects_dir, selection))),
                'active_screen': 'project_details'
            }
            self.state.update(state)

        def handle_project_options_menu(selection):
            key = selection
            if self.thread(key).can_start():
                self.thread(key).start()
                if 'callback' in ACTIONS[key]:
                    callback = ACTIONS[key]['callback']
                    if self.thread(callback).can_start():
                        self.thread(callback).start()

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
        custom_handlers = [self.sidebar_menu_key_handler]

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

                action, selected = self.handle_key_input(0, custom_handlers=custom_handlers)
                if selected:
                    return

                sleep(self.refresh_rate)

    def sidebar_menu_key_handler(self, key, selected=0):
        if self.state.focus == 'menu':
            for idx, item in enumerate(self.state.sidebar_menu['options']):
                if item.selected == True:
                    selected = idx
                    break

            options_length = len(self.state.sidebar_menu['options'])
            if key.is_sequence:
                if selected is not None and options_length is not None:
                    if key.name == 'KEY_UP':
                        selected -= 1
                        if selected < 0:
                            selected = options_length - 1  # loop back to end
                        while isinstance(self.state.sidebar_menu['options'][selected],
                                         SeparatorMenuItem):  # Skip SeparatorMenuItems
                            selected -= 1
                            if selected < 0:
                                selected = options_length - 1  # loop back to end
                        for idx, item in enumerate(self.state.sidebar_menu['options']):
                            self.state.sidebar_menu['options'][idx].selected = True if idx == selected else False
                        return True, False
                    elif key.name == 'KEY_DOWN':
                        selected += 1
                        if selected >= options_length:
                            selected = 0  # loop back to start
                        while isinstance(self.state.sidebar_menu['options'][selected],
                                         SeparatorMenuItem):  # Skip SeparatorMenuItems
                            selected += 1
                            if selected >= options_length:
                                selected = 0  # loop back to start
                        for idx, item in enumerate(self.state.sidebar_menu['options']):
                            self.state.sidebar_menu['options'][idx].selected = True if idx == selected else False
                        return True, False
                    elif key.name == 'KEY_ENTER':
                        selected_option = self.state.sidebar_menu['options'][selected]
                        if isinstance(selected_option, MenuItem):
                            selected_option.handler(selected_option.value)
                        return True, True
        return False, False

    def add_padding(self, text, width, pad=' '):
        padding_needed = width - len(text)
        left_padding = padding_needed // 2
        right_padding = padding_needed - left_padding
        return pad * left_padding + text + pad * right_padding
