import time
from blessed import Terminal
from const import DEFAULTS, DEFAULTS_LABELS, VALIDATORS, CONVERTERS

term = Terminal()

def form_fields(values, labels, validators):
    fields = []

    for key in values:
        value = values[key]
        if isinstance(value, list):  # Convert list to comma-separated string
            value = ', '.join(value)
        fields.append({'key':key, 'prompt': labels[key] + ": ", 'response': str(value), 'validator':validators[key], 'active': False})
    return fields

def draw_form(fields):
    for idx, field in enumerate(fields):
        if field['active']:
            # Toggle the display of the cursor character.
            if time.time() % 1 < 0.5:
                line = term.reverse + field['prompt'] + term.normal + field['response'] + '|'
            else:
                line = term.reverse + field['prompt'] + term.normal + field['response']
        else:
            line = field['prompt'] + field['response']

        if not field['validator'](field['response']):
            line += term.red(f'  Invalid input for field "{field["prompt"]}"!')

        print(line)

def model_config_form():
    fields=[{'key':'name', 'prompt': 'Name: ', 'response': 'aibyss', 'validator': lambda s: s.isalpha(), 'active': True}]
    fields.extend(form_fields(DEFAULTS, DEFAULTS_LABELS, VALIDATORS))
    return form(fields)

def form(fields):
    current_field = 0
    with term.cbreak(), term.hidden_cursor():
        print(term.home + term.clear)
        draw_form(fields)
        while True:
            key = term.inkey(timeout=0.1)  # Lower timeout for smoother blinking.
            if not key and not key.is_sequence:
                print(term.home + term.clear)
                draw_form(fields)
                continue
            if key.is_sequence:
                if key.name == 'KEY_ENTER':
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

                elif key.name == 'KEY_UP':
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
            print(term.home + term.clear)
            draw_form(fields)

if __name__ == '__main__':
    model_config_form()
