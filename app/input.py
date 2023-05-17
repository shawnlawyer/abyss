import time
from const import *

class Input():
    def get_key_input(self):
        return self.key_input()

    def handle_key_input(self, custom_handlers=None):
        handler = self.state.input_handlers[self.state.focus]
        return handler()

    def sidebar_menu_key_handler(self):
        if self.state.focus != 'sidebar_menu':
            return False
        active = None

        for idx, item in enumerate(self.state.sidebar_menu['options']):
            if item.active == True:
                active = idx
                break

        if active is None:
            self.state.sidebar_menu['options'][1].active = True
            active = 1 # this should actually be the first selectable menu item

        options_length = len(self.state.sidebar_menu['options'])
        with self.term.hidden_cursor(), self.term.cbreak(), self.term.keypad():

            key = self.term.inkey()
            if key.is_sequence:
                if key.code == self.term.KEY_BTAB:
                    active -= 1
                    if active < 0:
                        active = options_length - 1  # loop back to end
                    while isinstance(self.state.sidebar_menu['options'][active],
                                     SeparatorMenuItem):  # Skip SeparatorMenuItems
                        active -= 1
                        if active < 0:
                            active = options_length - 1  # loop back to end
                    for idx, item in enumerate(self.state.sidebar_menu['options']):
                        self.state.sidebar_menu['options'][idx].active = True if idx == active else False
                    return 'sidebar_menu_change_active'
                elif key.code == self.term.KEY_TAB:
                    active += 1
                    if active >= options_length:
                        active = 0  # loop back to start
                    while isinstance(self.state.sidebar_menu['options'][active],
                                     SeparatorMenuItem):  # Skip SeparatorMenuItems
                        active += 1
                        if active >= options_length:
                            active = 0  # loop back to start
                    for idx, item in enumerate(self.state.sidebar_menu['options']):
                        self.state.sidebar_menu['options'][idx].active = True if idx == active else False
                    return 'sidebar_menu_change_active'
                elif key.name == 'KEY_ENTER':
                    selected = self.state.sidebar_menu['options'][active]
                    if isinstance(selected, MenuItem):
                        selected.handler(selected.value)
                    return 'enter'
                elif  key.name == 'KEY_ESCAPE':
                    # quit()
                    return 'exit'


    def form_key_handler(self):
        if self.state.focus != 'form':
            return False

        active = None

        for idx, field in enumerate(self.state.form['fields']):
            if field.active == True:
                active = idx
                break

        if active is None:
            active = 0
            self.state.form['fields'][active].active = True

        with self.term.hidden_cursor(), self.term.cbreak(), self.term.keypad():
            key = self.term.inkey(timeout=self.refresh_rate, esc_delay=0.35)
            if key.is_sequence:

                if key.code in (self.term.KEY_BACKSPACE, self.term.KEY_DELETE):
                    self.state.form['fields'][active].backspace()
                    return 'form_backspace'
                elif key.code == self.term.BKEY_TAB:
                    active -= 1
                    if active < 0:
                        active = len(self.state.form['fields'])  # loop back to end
                    for idx, item in enumerate(self.state.form['fields']):
                        self.state.form['fields'][idx].active = True if idx == active else False
                    return 'field_change_selected'
                elif key.code == self.term.KEY_TAB:
                    active += 1
                    if active >= len(self.state.form['fields']):
                        active = 0  # loop back to start
                    for idx, item in enumerate(self.state.form['fields']):
                        self.state.form['fields'][idx].active = True if idx == active else False
                    return 'field_change_selected'

                elif key.code == self.term.KEY_ENTER:
                    invalid_fields = [field.prompt for field in self.state.form['fields'] if not field.validate()]
                    if not invalid_fields:
                        converted_dict = {}
                        for field in self.state.form['fields']:
                            converted_dict[field.key] = field.convert()
                        self.state.form['output'] = converted_dict
                        self.state.form['handler']()

                        return 'enter'
                    return 'submit_attempt'
                elif key.code == self.term.KEY_LEFT:
                    self.state.update({
                        'focus': 'sidebar_menu'
                    })
                    return 'changed_focus'
            elif key:
                self.state.form['fields'][active].response += self.term.strip(key)
                return 'form_input'


class MenuItem:
    def __init__(self, label, handler, value=None):
        self.label = label
        self.handler = handler
        self.value = value
        self.active = False

    def __str__(self):
        prefix = ' * ' if self.active else ' - '
        return prefix + self.label

class SeparatorMenuItem:
    def __init__(self, label=''):
        self.label = label
        self.handler = None
        self.active = False

    def __str__(self):
        return ' ' + self.label

class InputField:

    def __init__(self, key, value, label, validator):
        self.key = key
        self.value = value
        self.label = label
        self.validator = validator
        self.active = False

    @property
    def response(self):
        if isinstance(self.value, list):
            return ', '.join(self.value)
        return str(self.value)

    @property
    def prompt(self):
        return self.label + ": "

    @response.setter
    def response(self, new_value):
        self.value = new_value

    def validate(self):
        return self.validator(self.response)


    def backspace(self):
        self.response = self.response[:-1]

    def convert(self):
        if self.key in CONVERTERS:
            try:
                return CONVERTERS[self.key](self.value)
            except Exception as e:
                print(f"Error converting key {self.key}: {e}")
                return self.value
        else:
            print(f"No converter found for key {self.key}. Keeping value as is.")
            return self.value

    def get_display_text(self, cursor_character=CURSOR):
        if self.active:
            # Toggle the display of the cursor character.
            if time.time() % 1 < 0.75:
                text = self.prompt + self.response + cursor_character
            else:
                text = self.prompt + self.response

            #if not self.validate():
                #text += f" Woops!: {self.prompt}"
        else:
            text = self.prompt + self.response

        return text
