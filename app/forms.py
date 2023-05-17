from os.path import join, expanduser
from util import DataObject
from const import *
from lib import save_config
from input import InputField

settings = DataObject(SETTINGS)
defaults = DataObject(DEFAULTS)

class Forms():

    def forms_controller(self):
        if 'form' in SCREENS[self.state.active_screen]:

            form = SCREENS[self.state.active_screen]['form']
            form = self.get_form_config(form)
            form = self.set_form_screen_location(form, FORMS_WIDTH, FORMS_X, FORMS_Y, FORMS_ALIGN)
            form['fields'] = self.form_fields(form['values'], form['labels'], form['validators'])
            self.state.update({
                'focus': 'form',
                'form' : form
            })
            self.state.input_handlers['form'] = self.form_key_handler
            self.handle_form()

    def get_form_config(self, form):
        def create_project_config_form_handler ():

            outputs = self.state.form['output']
            config_filename = outputs['name'] + '.json'
            outputs.pop('name')
            filepath = join(settings.projects_dir, config_filename)
            save_config(outputs, filepath)

            self.state.update({
                'configs' : DataObject(outputs),
                'config_file' : config_filename,
                'active_screen' : 'home',
                'focus' : 'sidebar_menu'
            })

        def tuning_settings_form (): # this should be tune project

            self.state.update({
                'configs_tuning' : DataObject(self.state.form['output']),
                'active_screen' : 'home',
                'focus' : 'sidebar_menu'
            })

        def application_settings_form ():
            self.settings = DataObject(self.state.form['output'])
            filepath = join(expanduser("~"), '.abyss')
            save_config(self.state.form['output'], filepath)

            self.state.update({
                'active_screen' : 'home',
                'focus' : 'sidebar_menu'
            })

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
            field = InputField(key, values[key], labels[key], validators[key])
            fields.append(field)
        return fields

    def handle_form(self):
        action = None
        while True:
            self.write_form_to_screen_buffer(
                self.state.form['fields'],
                self.state.form['x'],
                self.state.form['y'],
                self.state.form['width'],
                self.state.form['header']
            )
            self.handle_key_input()

    def write_form_to_screen_buffer(self, fields, x=0, y=1, width=0, header=None):
        lines = []
        for idx, field in enumerate(fields):
            text = field.get_display_text()
            line = text
            lines.append(line)

        height = len(lines)
        text = self.add_border(header, '\n'.join(lines), width, height)
        self.write_to_screen_buffer(text, x, y)
        self.term.print_buffer()
