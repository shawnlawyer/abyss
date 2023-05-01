from const import *
from blessed import Terminal
import time
class AppState:
    def __init__(self):
        self.selection = None
        self.configs = None
        self.config_file = None

class UI:

    def __init__(self):
        self.term = Terminal()
        self.app_title = ""
        self.state = AppState()

    def draw_dashboard(self):
        print(self.term.home + self.term.clear)
        print(self.term.move_y(2) + self.term.center((self.app_title)))
        print(self.term.move_y(self.term.height // 4))

        with self.term.location(0, self.term.height - 1):
            print(self.term.center('Arrow Keys to Navigate - Enter to Select - ESC to Exit'), end='')


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

    def menu(self, options, header=None, x=0, y=0):
        selected = 0
        while True:
            if header:
                with self.term.location(x, y):
                    print(header)
                    for i, option in enumerate(options):
                        if i == selected:
                            print(self.term.move_x(x, i+1) + self.term.on_black(self.term.white(option)))
                        else:
                            print(self.term.move_x(x, i+1) + option)
            action, selected = self.handle_key_input(selected, len(options))
            if action == 'enter':
                return selected


if __name__ == "__main__":
    app = GUI()
    app.run()
