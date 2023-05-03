from const import *
from blessed import Terminal
import time
import json
BOX_1 = '╔╗╚╝═║'

def unpack_box_style(box_string):
    if len(box_string) != 6:
        raise ValueError('box_string must be 6 characters long')
    return tuple(box_string)

class AppState:
    def __init__(self):
        self.selection = None
        self.configs = None
        self.config_file = None
        self.active_screen = None

class UI:

    def __init__(self):
        self.term = Terminal()
        self.app_title = ""
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

    def draw_form(self, fields, x=0, y=0, max_width=None, header=None, style=BOX_1):
        console_width = self.term.width
        top_left, top_right, bottom_left, bottom_right, horizontal, vertical = self.unpack_box_style(style)
        if max_width == None:
            max_width = min(max(len(field['prompt'] + field['response']) + 4 for field in fields), console_width - 4)

            if header:
                max_width = min(max(max_width, len(header)), console_width - 4)  # adjust for header length

        with self.term.location(x, y):
            # Top border
            if header:
                text = header.ljust(max_width - 1, horizontal)
                print(self.term.move_x(x) + top_left + horizontal + text + top_right)
            else:
                print(self.term.move_x(x) + top_left + horizontal * max_width + top_right)

            for idx, field in enumerate(fields):
                if field['active']:
                    # Toggle the display of the cursor character.
                    if time.time() % 1 < 0.5:
                        text = field['prompt'] + field['response'] + '|'
                    else:
                        text = field['prompt'] + field['response']
                else:
                    text = field['prompt'] + field['response']

                text = text[:max_width - 2] + '...' if len(text) > max_width - 2 else text.ljust(max_width - 2)

                if not field['validator'](field['response']):
                    text += self.term.red(f'  Invalid input for field "{field["prompt"]}"!')

                print(self.term.move_x(x, idx + 1) + vertical + ' ' + text + ' ' + vertical)

            # Bottom border
            print(self.term.move_x(x) + bottom_left + horizontal * max_width + bottom_right)

    def form(self, fields, x=0, y=0, width=None, header=None, style=BOX_1):
        current_field = 0
        with self.term.cbreak(), self.term.hidden_cursor():
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
                print(self.term.home + self.term.clear)
                self.draw_form(fields, x, y, width, header, style)

    def draw_box(self, header, text, width, height, x=1, y=1, style=BOX_1):
        top_left, top_right, bottom_left, bottom_right, horizontal, vertical = self.unpack_box_style(style)

        # Initialize an empty list to store each line of the box
        # Draw top border
        with self.term.location(x, y):
            print(top_left + header + horizontal * (width - len(header) - 2) + top_right)
        # Draw text lines
        lines = text.split('\n')
        for i in range(height):
            with self.term.location(x, y + i + 1):
                if i < len(lines):
                    line = lines[i]  # truncate if too long
                    print(self.term.move_x(x) + vertical + lines[i].ljust(width - 2) + vertical)
                else:
                    print(self.term.move_x(x) + vertical + ' ' * (width - 2) + vertical)  # print empty line

        # Draw bottom border
        with self.term.location(x, y + height + 2):
            print(self.term.move_x(x) + bottom_left + horizontal * (width - 2) + bottom_right)

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

    def menus(self, menus_list, style=BOX_1):
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
                y = menu_dict.get('y', 0)
                selected = selections[menu_id] if menu_id == active_menu else None  # reset selection if not active menu

                max_width = min(max(len(option) + 4 for option in options), console_width - 4)  # padding for box

                if header:
                    max_width = min(max(max_width, len(header)), console_width - 4)  # adjust for header length

                with self.term.location(x, y):
                    # Top border
                    if header:
                        text = header.ljust(max_width - 1, horizontal)
                        print(self.term.move_x(x) + top_left + horizontal + text + top_right)
                    else:
                        print(self.term.move_x(x) + top_left + horizontal * max_width + top_right)

                    for i, option in enumerate(options):
                        text = option[:max_width - 2] + '... ' if len(option) > max_width - 2 else option.ljust(
                            max_width - 2)
                        line = self.term.on_black(self.term.white(text)) if i == selected else text
                        print(self.term.move_x(x, i + 1) + vertical + ' ' + line + ' ' + vertical)
                        # Bottom border
                    print(self.term.move_x(x) + bottom_left + horizontal * max_width + bottom_right)

                action, selected = self.handle_key_input(selected, len(options), custom_handlers=custom_handlers)
                if action == 'enter':
                    return menu_id, selected
                elif action == 'menu_change_selected':
                    selections[active_menu] = selected
                elif action == 'field_change_selected':
                    selections[menu_id] = selected




# Use the function


if __name__ == "__main__":
    # Test the function
    header = "Main Menu"
    text = "Create New Project\nLoad Project\nAnother line of text"
    print(draw_box(header, text, 25, 5))
