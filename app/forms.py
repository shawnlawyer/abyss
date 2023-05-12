from os.path import join, expanduser
import time
from util import DataObject
from const import *
from lib import save_config

settings = DataObject(SETTINGS)
defaults = DataObject(DEFAULTS)

class Forms():

    def forms_controller(self):
        if 'form' in SCREENS[self.state.active_screen]:
            self.state.focus = 'form'
            form = SCREENS[self.state.active_screen]['form']
            form = self.get_form_config(form)
            form = self.set_form_screen_location(form, FORMS_WIDTH, FORMS_X, FORMS_Y, FORMS_ALIGN)
            form['fields'] = self.form_fields(form['values'], form['labels'], form['validators'])
            self.state.form = form
            self.active_form_field = 0
            self.handle_form()
            self.state.focus = 'menu'

    def get_form_config(self, form):
        def create_project_config_form_handler ():
            self.state.configs = DataObject(self.state.form['output'])
            self.state.config_file = self.state.configs['name'] + '.json'
            filepath = join(settings.projects_dir, self.state.config_file)
            self.state.configs.pop('name')
            save_config(self.state.form['output'], filepath)
            self.state.active_screen = 'home'
        def tuning_settings_form (): # this should be tune project
            self.state.configs_tuning = self.state.form['fields']
            self.state.active_screen = 'tuning_settings_detail'
        def application_settings_form ():
            self.state.settings = DataObject(self.state.form['output'])
            filepath = join(expanduser("~"), '.abyss')
            save_config(self.state.form['output'], filepath)
            self.state.active_screen = 'home'
        forms = {
            'create_project_config_form': {
                'header' : SCREENS['create_project']['label'],
                'values': {**SAVE_FILE_FORM_FIELDS, **DEFAULTS},
                'labels': {**SAVE_FILE_FORM_FIELD_LABELS, **DEFAULTS_LABELS},
                'validators': {**SAVE_FILE_FORM_FIELD_VALIDATORS, **VALIDATORS},
                'handler' : create_project_config_form_handler,
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
                'values': self.settings.to_dict(),
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

    def handle_form(self):
        fields = self.state.form['fields']
        selected = 0

        def form_key_handler(key, selected=0, options_length=None):
            if self.state.focus == 'form':

                if key.is_sequence:
                    if key.name == 'KEY_UP':
                        if self.active_form_field > 0:
                            self.state.form['fields'][self.active_form_field]['active'] = False
                            self.active_form_field -= 1
                            self.state.form['fields'][self.active_form_field]['active'] = True
                        return 'field_change_selected', self.active_form_field
                    elif key.name == 'KEY_DOWN':
                        if self.active_form_field < len(fields) - 1:
                            self.state.form['fields'][self.active_form_field]['active'] = False
                            self.active_form_field += 1
                            self.state.form['fields'][self.active_form_field]['active'] = True
                        return 'field_change_selected', self.active_form_field
                    elif key.name == 'KEY_BACKSPACE':
                        self.state.form['fields'][self.active_form_field]['response'] = fields[self.active_form_field]['response'][:-1]
                        return 'form_backspace', self.active_form_field

                    elif key.name == 'KEY_ENTER':
                        invalid_fields = [field['prompt'] for field in fields if
                                          not field['validator'](field['response'])]
                        if not invalid_fields:
                            values = {}
                            for field in self.state.form['fields']:
                                values[field['key']] = field['response']
                            converted_dict = {}
                            for key, value in values.items():
                                if key in CONVERTERS:
                                    try:
                                        converted_dict[key] = CONVERTERS[key](value)
                                    except Exception as e:
                                        pass
                                        # self.debug(f"Error converting key {key}: {e}")
                                else:
                                    # self.debug(f"No converter found for key {key}. Keeping value as is.")
                                    converted_dict[key] = value
                                self.state.form['output'] = converted_dict
                        self.state.form['handler']()
                        return 'enter', True
                else:
                    self.state.form['fields'][self.active_form_field]['response'] += key
                    return 'form_input', self.active_form_field

            return None, self.active_form_field

        custom_handlers = [form_key_handler]
        while True:

            self.write_form_to_screen_buffer(
                self.state.form['fields'],
                self.state.form['x'],
                self.state.form['y'],
                self.state.form['width'],
                self.state.form['header']
            )
            action, selected = self.handle_key_input(selected, custom_handlers=custom_handlers)
            if action == 'enter':
                return

    def write_form_to_screen_buffer(self, fields, x=0, y=1, width=0, header=None):
        lines = []
        for idx, field in enumerate(fields):
            if field['active']:
                # Toggle the display of the cursor character.
                if time.time() % 1 < 0.5:
                    text = field['prompt'] + field['response'] + CURSOR
                else:
                    text = field['prompt'] + field['response']
            else:
                text = field['prompt'] + field['response']


            if not field['validator'](field['response']):
                text +=  f"Woops!: {field['prompt']}"

            text = text[:width - 2] + '...' if len(text) > width - 2 else text.ljust(width - 2)

            line = text
            lines.append(line)

        height = len(lines)

        text = self.add_border(header, '\n'.join(lines), width, height)
        self.write_to_screen_buffer(text, x, y)
