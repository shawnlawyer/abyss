from const import *
from blessed import Terminal
import time

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

    def form_fields(self, values, labels, validators):
        fields = []

        for key in values:
            value = values[key]
            if isinstance(value, list):  # Convert list to comma-separated string
                value = ', '.join(value)
            fields.append({'key':key, 'prompt': labels[key] + ": ", 'response': str(value), 'validator':validators[key], 'active': False})
        return fields

    def draw_form(self, fields):
        for idx, field in enumerate(fields):
            if field['active']:
                # Toggle the display of the cursor character.
                if time.time() % 1 < 0.5:
                    line = self.term.reverse + field['prompt'] + self.term.normal + field['response'] + '|'
                else:
                    line = self.term.reverse + field['prompt'] + self.term.normal + field['response']
            else:
                line = field['prompt'] + field['response']

            if not field['validator'](field['response']):
                line += self.term.red(f'  Invalid input for field "{field["prompt"]}"!')

            print(line)


    def get_key_input(self):
        return self.term.inkey(timeout=0.1)  # Lower timeout for smoother blinking.

    def handle_key_input(self, selected=None, options_length=None):
        key = self.get_key_input()

        if key.is_sequence:
            if selected is not None and options_length is not None:
                if key.name == 'KEY_UP':
                    selected = max(0, selected - 1)
                elif key.name == 'KEY_DOWN':
                    selected = min(options_length - 1, selected + 1)
            if key.name == 'KEY_ENTER':
                return ('enter', selected)
            elif key.name == 'KEY_ESCAPE':
                quit()
        return ('other', selected)

    def form(self, fields):
        current_field = 0
        with self.term.cbreak(), self.term.hidden_cursor():
            print(self.term.home + self.term.clear)
            self.draw_form(fields)
            while True:
                action, _ = self.handle_key_input()
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
                else:
                    key = self.get_key_input()
                    if not key and not key.is_sequence:
                        print(self.term.home + self.term.clear)
                        self.draw_form(fields)
                        continue
                    if key.is_sequence:
                        if key.name == 'KEY_UP':
                            if current_field > 0:
                                fields[current_field]['active'] = False
                                current_field -= 1
                                fields[current_field]['active'] = True
                        elif key.name == 'KEY_DOWN':
                            if current_field < len(fields) - 1:
                                fields[current_field]['active'] = False
                                current_field += 1
                                fields[current_field]['active'] = True
                        elif key.name == 'KEY_BACKSPACE':
                            fields[current_field]['response'] = fields[current_field]['response'][:-1]
                    else:
                        fields[current_field]['response'] += key
                print(self.term.home + self.term.clear)
                self.draw_form(fields)

    def menu(self, options, header=None, x=0, y=0, style=BOX_1):
        selected = 0
        console_width = self.term.width
        max_width = min(max(len(option) + 4 for option in options), console_width - 4)  # padding for box
        lines = []

        top_left, top_right, bottom_left, bottom_right, horizontal, vertical = unpack_box_style(style)

        while True:
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
                    text = option[:max_width - 2] + '... ' if len(option) > max_width - 2 else option.ljust(max_width - 2)
                    line = self.term.on_black(self.term.white(text)) if i == selected else text
                    print(self.term.move_x(x, i + 1) + vertical + ' ' + line + ' ' + vertical)
                # Bottom border
                print(self.term.move_x(x) + bottom_left + horizontal * max_width + bottom_right)

            action, selected = self.handle_key_input(selected, len(options))
            if action == 'enter':
                return selected
def draw_box(header, text, width, height, style=BOX_1):
    top_left, top_right, bottom_left, bottom_right, horizontal, vertical = unpack_box_style(style)

    # Initialize an empty list to store each line of the box
    box_lines = []

    # Draw top border
    box_lines.append(top_left + header + horizontal * (width - len(header) - 2) + top_right)

    # Draw text lines
    lines = text.split('\n')
    for i in range(height):
        if i < len(lines):
            line = lines[i]
            line = line if len(line) <= width - 2 else line[:width - 5] + '...'  # truncate if too long
            box_lines.append(vertical + line.ljust(width - 2) + vertical)
        else:
            box_lines.append(vertical + ' ' * (width - 2) + vertical)  # print empty line

    # Draw bottom border
    box_lines.append(bottom_left + horizontal * (width - 2) + bottom_right)

    # Join the list of lines into a single string with newline characters between each line
    return '\n'.join(box_lines)



# Use the function


if __name__ == "__main__":
    # Test the function
    header = "Main Menu"
    text = "Create New Project\nLoad Project\nAnother line of text"
    print(draw_box(header, text, 25, 5))
