from const import *
import time
class Form():

    def form_fields(self, values, labels, validators):
        fields = []

        for key in values:
            value = values[key]
            if isinstance(value, list):  # Convert list to comma-separated string
                value = ', '.join(value)
            fields.append({'key':key, 'prompt': labels[key] + ": ", 'response': str(value), 'validator':validators[key], 'active': False})
        return fields

    def write_form_to_screen_buffer(self, fields, x=0, y=1, width=0, header=None):
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

            line = text
            lines.append(line)

        height = len(lines)

        text = self.add_border(header, '\n'.join(lines), width, height)
        self.write_to_screen_buffer(text, x, y)

    def form(self, fields, x=0, y=1, width=None, header=None):
        current_field = 0

        def form_key_handler(key, selected=0, options_length=None):
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

            self.write_form_to_screen_buffer(fields, x, y, width, header)
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





# Use the function


if __name__ == "__main__":
    pass