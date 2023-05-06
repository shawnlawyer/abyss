from const import *
import time
import json
import threading
import blessed

class BufferedTerminal(blessed.Terminal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.screen_matrix = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        self.lock = threading.Lock()

    def write(self, x, y, text):
        with self.lock:
            for i, char in enumerate(list(text)):
                self.screen_matrix[y][x + i] = char

    def print_buffer(self):
        with self.lock:
            self.clear()
            self.home()
            print('\n'.join([''.join(row) for row in self.screen_matrix]))

    def clear_buffer(self):
        with self.lock:
            self.screen_matrix = [[' ' for _ in range(self.width)] for _ in range(self.height)]

class AppState(dict):
    def update(self, new_dict):
        for key, value in new_dict.items():
            setattr(self, key, value)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self
        self.selection = None
        self.configs = None
        self.config_file = None
        self.active_screen = None

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value


class UI():

    menus = {}
    app_title = ""
    def __init__(self):
        self.term = BufferedTerminal()
        self.state = AppState()

    def unpack_box_style(self, box_string):
        if len(box_string) != 6:
            raise ValueError('box_string must be 6 characters long')
        return tuple(box_string)

    def json_to_report(self, json_str):
        data = json.loads(json_str)
        lines = []
        for key, value in data.items():
            label = key.replace('_', ' ').title()
            lines.append(f"{label}: {value}")
        return lines

    def form_fields(self, values, labels, validators):
        fields = []

        for key in values:
            value = values[key]
            if isinstance(value, list):  # Convert list to comma-separated string
                value = ', '.join(value)
            fields.append({'key':key, 'prompt': labels[key] + ": ", 'response': str(value), 'validator':validators[key], 'active': False})
        return fields

    def draw_form(self, fields, x=0, y=1, width=0, header=None, style=BOX_1):
        console_width = self.term.width
        top_left, top_right, bottom_left, bottom_right, horizontal, vertical = self.unpack_box_style(style)
        lines = []
        for idx, field in enumerate(fields):
            if field['active']:
                # Toggle the display of the cursor character.
                if time.time() % 1 < 0.5:
                    text = field['prompt'] + field['response'] + '|'
                else:
                    text = field['prompt'] + field['response']
            else:
                text = field['prompt'] + field['response']

            text = text[:width - 2] + '...' if len(text) > width - 2 else text.ljust(width - 2)

            if not field['validator'](field['response']):
                text += self.term.red(f'  Invalid input for field "{field["prompt"]}"!')

            line = vertical + ' ' + text + ' ' + vertical
            lines.append()

        height = len(lines)

        self.draw_box(header, '\n'.join(lines), width, height, x, y)

    def form(self, fields, x=0, y=1, width=None, header=None, style=BOX_1):
        current_field = 0

        def form_key_handler(key, selected, options_length=None):
            if key.is_sequence:
                if key.name == 'KEY_UP':
                    if selected > 0:
                        fields[selected]['active'] = False
                        selected -= 1
                        fields[selected]['active'] = True
                    return 'field_change_selected', selected
                elif key.name == 'KEY_DOWN':
                    if selected < len(fields) - 1:
                        fields[selected]['active'] = False
                        selected += 1
                        fields[selected]['active'] = True
                    return 'field_change_selected', selected
                elif key.name == 'KEY_BACKSPACE':
                    fields[selected]['response'] = fields[selected]['response'][:-1]
                    return 'form_backspace', selected
            else:
                fields[selected]['response'] += key
                return 'form_input', selected

            return None, None

        custom_handlers = [form_key_handler]

        while True:
            action, current_field = self.handle_key_input(current_field, custom_handlers=custom_handlers)
            if action == 'enter':
                invalid_fields = [field['prompt'] for field in fields if not field['validator'](field['response'])]
                if invalid_fields:
                    print(f'These fields have invalid inputs: {", ".join(invalid_fields)}')
                else:
                    values = {}
                    for field in fields:
                        values[field['key']] = field['response']
                    converted_dict = {}
                    for key, value in values.items():
                        if key in CONVERTERS:
                            try:
                                converted_dict[key] = CONVERTERS[key](value)
                            except Exception as e:
                                print(f"Error converting key {key}: {e}")
                        else:
                            print(f"No converter found for key {key}. Keeping value as is.")
                            converted_dict[key] = value
                    return converted_dict
            self.draw_form(fields, x, y, width, header, style)

    def draw_box(self, header, text, width, height, x=1, y=1, style=BOX_1):
        top_left, top_right, bottom_left, bottom_right, horizontal, vertical = self.unpack_box_style(style)

        line = top_left + header + horizontal * (width - len(header) - 2) + top_right
        self.term.write(x, y, line)

        lines = text.split('\n')
        for i in range(height):
            if i < len(lines):
                line = lines[i]  # truncate if too long
                line = vertical + lines[i].ljust(width - 2) + vertical
            else:
                line = vertical + ' ' * (width - 2) + vertical
            self.term.write(x, y + i + 1, line)

        line = bottom_left + horizontal * (width - 2) + bottom_right
        self.term.write(x, y + height + 1, line)

    def get_key_input(self):
        return self.term.inkey(timeout=0.1)  # Lower timeout for smoother blinking.

    def handle_key_input(self, selected=None, options_length=None, custom_handlers=None):
        key = self.get_key_input()

        if custom_handlers is not None:
            for handler in custom_handlers:
                action, selected = handler(key, selected, options_length)
                if action:
                    return action, selected

        if key.is_sequence:
            if key.name == 'KEY_ESCAPE':
                quit()
        return (None, selected)

    def draw_menus(self, menus_list, style=BOX_1):
        selections = [0] * len(menus_list)
        console_width = self.term.width

        top_left, top_right, bottom_left, bottom_right, horizontal, vertical = self.unpack_box_style(style)

        active_menu = 0  # keep track of the active menu

        def menu_key_handler(key, selected, options_length):
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
                        active_menu = (active_menu + 1) % len(menus_list)  # move to the next menu
                        selections[active_menu] = 0  # select the first option in the new active menu
                        return ('menu_change_selected', selections[active_menu])
                    elif key.name == 'KEY_LEFT':
                        active_menu = (active_menu - 1) % len(menus_list)  # move to the previous menu
                        selections[active_menu] = 0  # select the first option in the new active menu
                        return ('menu_change_selected', selections[active_menu])
                    elif key.name == 'KEY_ENTER':
                        return ('enter', selected)
                elif key.name == 'KEY_ESCAPE':
                    # quit() return to main menu
                    pass
            return ('other', selected)

        custom_handlers = [menu_key_handler]

        while True:
            for menu_id, menu_dict in enumerate(menus_list):
                options = menu_dict['options']
                header = menu_dict.get('header', None)
                x = menu_dict.get('x', 0)
                y = menu_dict.get('y', 1)
                width = menu_dict.get('width', 0)
                height = menu_dict.get('height', len(options))
                selected = selections[menu_id] if menu_id == active_menu else None  # reset selection if not active menu

                lines = []
                for i, option in enumerate(options):
                    line = option + ' *' if i == selected else option
                    #line = option[:width - 4] + '... ' if len(option) > width - 2 else option.ljust(width - 2)
                    #lines.append(self.term.on_black(self.term.white(line)) if i == selected else line)
                    lines.append(line.ljust(width - 2))

                self.draw_box(header, '\n'.join(lines) , width, height, x, y)

                action, selected = self.handle_key_input(selected, len(options), custom_handlers=custom_handlers)
                if action == 'enter':
                    return menu_id, selected
                elif action == 'menu_change_selected':
                    selections[active_menu] = selected
                elif action == 'field_change_selected':
                    selections[menu_id] = selected
    def draw_current_state_menus(self, thread=None): #should be menus controller

        menus = []
        handlers = []

        for menu_name, gen_func_name in self.menus.items():
            gen_func = getattr(self, gen_func_name)
            menu, handler = gen_func()
            if menu:
                menus.append(menu)
                handlers.append(handler)

        menu_id, selection = self.draw_menus(menus)
        update_dict = handlers[menu_id](selection)
        if update_dict is not None:
            self.state.update(update_dict)




# Use the function


if __name__ == "__main__":
    pass