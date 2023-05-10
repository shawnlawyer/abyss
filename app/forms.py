from os.path import join
import time
from util import DataObject
from const import *
from lib import save_config

settings = DataObject(SETTINGS)
defaults = DataObject(DEFAULTS)

class Forms():

    def forms_controller(self):
        if 'form' in SCREENS[self.state.active_screen]:
            form = SCREENS[self.state.active_screen]['form']
            form = self.get_form_config(form)
            form = self.set_form_screen_location(form, FORMS_WIDTH, FORMS_X, FORMS_Y, FORMS_ALIGN)
            fields = self.form_fields(form['values'], form['labels'], form['validators'])
            values = self.handle_form(fields, form['x'], form['y'], form['width'], form['header'])
            form['handler'](values)

    def get_form_config(self, form):
        def create_project_config_form_handler (fields):
            self.state.configs = fields
            self.state.config_file = self.state.configs['name'] + '.json'
            config_filepath = join(settings.configs_dir, self.state.config_file)
            self.state.configs.pop('name')
            save_config(self.state.configs, config_filepath)
            self.state.active_screen = 'main_menu'
        def tuning_settings_form (fields): # this should be tune project
            self.state.configs_tuning = fields
            self.state.active_screen = 'tuning_settings_detail'
        def application_settings_form (fields):
            self.state.settings = fields
            config_filepath = join('~/', '.abyss')
            save_config(self.state.settings, config_filepath)
            self.state.active_screen = 'main_menu'

        forms = {
            'create_project_config_form': {
                'header' : SCREENS['create_project']['label'],
                'values': {**SAVE_FILE_FORM_FIELDS, **DEFAULTS},
                'labels': {**SAVE_FILE_FORM_FIELD_LABELS, **DEFAULTS_LABELS},
                'validators': {**SAVE_FILE_FORM_FIELD_VALIDATORS, **VALIDATORS},
                'handler' : create_project_config_form_handler
            },
            'tuning_settings_form': {
                'header' : SCREENS['tune_project']['label'],
                'values': TUNING_SETTINGS_FORM_FIELDS,
                'labels': TUNING_SETTINGS_LABELS,
                'validators': TUNING_SETTINGS_VALIDATORS,
                'handler' : tuning_settings_form
            },
            'application_settings_form': {
                'header' : SCREENS['application_settings']['label'],
                'values': SETTINGS,
                'labels': SETTINGS_LABELS,
                'validators': SETTINGS_VALIDATORS,
                'handler' : application_settings_form
            }
        }

        if form in forms:
            return forms[form]

        return None


    def set_form_screen_location(self, form, width=60, x_offset=1, y_offset=1, align='left'):

        form['width'] = width
        if align == 'center':
            form['x'] = self.term.width // 2 - width // 2
        elif align == 'right':
            form['x'] = self.term.width - width - x_offset
        else:  # align == 'left':
            form['x'] = x_offset

        form['y'] = y_offset

        return form


    def form_fields(self, values, labels, validators):

        fields = []
        for key in values:
            value = values[key]
            if isinstance(value, list):
                value = ', '.join(value)
            fields.append({'key':key, 'prompt': labels[key] + ": ", 'response': str(value), 'validator':validators[key], 'active': False})

        return fields

    def handle_form(self, fields, x=0, y=1, width=None, header=None): # becomes handle form
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
