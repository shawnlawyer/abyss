from const import *
import time
import json
import threading
import blessed
from form import Form
from menu import Menu

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


class UI(Form, Menu):

    menus = {}
    app_title = ""
    def __init__(self):
        self.term = BufferedTerminal()
        self.state = AppState()

    def unpack_box_style(self, box_string):
        return tuple(box_string)

    def json_to_report(self, json_str):
        data = json.loads(json_str)
        lines = []
        for key, value in data.items():
            label = key.replace('_', ' ').title()
            lines.append(f"{label}: {value}")
        return lines

    def draw_border(self, header, text, width, height, x=1, y=1, style=BOX_1):
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


if __name__ == "__main__":
    pass