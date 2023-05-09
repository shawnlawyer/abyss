from os.path import join, basename
from glob import glob
from util import DataObject
from const import *
from lib import save_config, load_config
from ui import UI

settings = DataObject(SETTINGS)
defaults = DataObject(DEFAULTS)

class Menus():
    def menus_controller(self, thread=None):
        while not thread.stop_event.is_set():
            menus = self.get_menus()
            menus = self.set_menus_screen_location(menus)
            self.handle_menus(menus)

    def get_menus(self):
        config_files = glob(f"{settings.configs_dir}/*.json")
        main_menu_options_map = ['main_menu', 'create_project', 'tune_project', 'application_settings']
        choose_project_options_map = [basename(config_file) for config_file in config_files] if config_files else []
        project_options_menu_options_map = ['train', 'chat', 'model']

        def handle_main_menu(selection):
            state = {'active_screen': main_menu_options_map[selection]}
            self.state.update(state)

        def handle_choose_project_menu(selection):
            state = {
                'config_file': choose_project_options_map[selection],
                'configs': DataObject(load_config(join(settings.configs_dir, choose_project_options_map[selection]))),
                'active_screen': 'project_details'
            }
            self.state.update(state)


        def handle_project_options_menu(selection):
            key = project_options_menu_options_map[selection]
            if self.threads[key].can_start():
                self.threads[key].start()
                if 'callback' in ACTIONS[key]:
                    callback = ACTIONS[key]['callback']
                    if callback in self.threads:
                        if self.threads[callback].can_start():
                            self.threads[callback].start()
        menus = {
            'main_menu': {
                'header': APP_TITLE,
                'options': [SCREENS[value]['label'] for value in main_menu_options_map ],
                'handler': handle_main_menu,
                'condition': lambda: True
            },
            'choose_project_menu': {
                'header': MENUS['choose_project_menu']['label'],
                'options': choose_project_options_map,
                'handler': handle_choose_project_menu,
                'condition': lambda: self.state.active_screen == 'main_menu' and config_files
            },
            'project_options_menu': {
                'header': MENUS['project_options_menu']['label'],
                'options': [ACTIONS[value]['label'] for value in ACTIONS],
                'handler': handle_project_options_menu,
                'condition': lambda: self.state.configs and self.state.config_file
            }
        }

        current_menus = []
        for key, menu in menus.items():
            if menu['condition']():
                current_menus.append(menu)
        return current_menus

    def set_menus_screen_location(self, menus, width=25, x_offset=4, y_offset=4, align='left'):

        for menu in menus:
            menu['width'] = width

            if align == 'center':
                menu['x'] = self.term.width // 2 - width // 2
            elif align == 'right':
                menu['x'] = self.term.width - width - x_offset
            else:  # align == 'left':
                menu['x'] = x_offset

            menu['y'] = y_offset
            y_offset += len(menu['options']) + 2

        return menus

    def handle_menus(self, menus):
        selections = [0] * len(menus)
        active_menu = 0  # keep track of the active menu

        def key_handler(key, selected, options_length):
            nonlocal active_menu
            if key.is_sequence:
                if selected is not None and options_length is not None:
                    if key.name == 'KEY_UP':
                        selected = max(0, selected - 1)
                        return 'field_change_selected', selected
                    elif key.name == 'KEY_DOWN':
                        selected = min(options_length - 1, selected + 1)
                        return 'field_change_selected', selected
                    elif key.name == 'KEY_RIGHT':
                        active_menu = (active_menu + 1) % len(menus)  # move to the next menu
                        selections[active_menu] = 0  # select the first option in the new active menu
                        return ('menu_change_selected', selections[active_menu])
                    elif key.name == 'KEY_LEFT':
                        active_menu = (active_menu - 1) % len(menus)  # move to the previous menu
                        selections[active_menu] = 0  # select the first option in the new active menu
                        return ('menu_change_selected', selections[active_menu])
                    elif key.name == 'KEY_ENTER':
                        return ('enter', selected)
                elif key.name == 'KEY_ESCAPE':
                    # quit() return to main menu
                    pass
            return ('other', selected)

        custom_handlers = [key_handler]

        while True:
            for menu_id, menu in enumerate(menus):
                selected = selections[menu_id] if menu_id == active_menu else None
                lines = []
                for i, option in enumerate(menu['options']):
                    line = option + ' *' if i == selected else option
                    lines.append(line.ljust(len(line) - 2))

                text = self.add_border(menu['header'], '\n'.join(lines) , menu['width'], menu.get('height', len(menu['options'])))
                self.write_to_screen_buffer(text, menu['x'], menu['y'])

                action, selected = self.handle_key_input(selected, len(menu['options']), custom_handlers=custom_handlers)

                if action == 'enter':
                    return menus[menu_id]['handler'](selected)
                elif action == 'menu_change_selected':
                    selections[active_menu] = selected
                elif action == 'field_change_selected':
                    selections[menu_id] = selected