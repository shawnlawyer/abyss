from const import *
import json
from form import Form
from terminal import BufferedTerminal
from state import AppState
from threads import StoppableThread, ThreadedSubprocess

class UI(Form):

    app_title = ""
    def __init__(self):
        self.term = BufferedTerminal()
        self.state = AppState()

    def setup_thread(self, key):

        if 'command' in THREADS.get(key):
            command = THREADS[key]['command']
            self.threads[key] = ThreadedSubprocess(command, self)
        else:
            target = getattr(self, key)
            self.threads[key] = StoppableThread(target)

        return self.threads[key]

    def debug(self):
        self.threads['draw_screen_buffer'].stop()

    def unpack_box_style(self, box_string):
        return tuple(box_string)

    def json_to_report(self, json_str):
        data = json.loads(json_str)
        lines = []
        for key, value in data.items():
            label = key.replace('_', ' ').title()
            lines.append(f"{label}: {value}")
        return lines

    def add_border(self, header, text, width, height, style=BOX_1):
        top_left, top_right, bottom_left, bottom_right, horizontal, vertical = self.unpack_box_style(style)

        border = []
        top_line = top_left + header + horizontal * (width - len(header) - 2) + top_right
        border.append(top_line)

        lines = text.split('\n')
        for i in range(height):
            if i < len(lines):
                line = lines[i]  # truncate if too long
                line = vertical + lines[i].ljust(width - 2) + vertical
            else:
                line = vertical + ' ' * (width - 2) + vertical
            border.append(line)

        bottom_line = bottom_left + horizontal * (width - 2) + bottom_right
        border.append(bottom_line)

        return border
    def write_to_screen_buffer(self, text_with_border, x=1, y=1):
        lines = text_with_border
        for i, line in enumerate(lines):
            self.term.write(x, y + i, line)

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