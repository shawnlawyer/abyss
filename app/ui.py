from time import sleep
import json
from const import *
from threads import StoppableThread, ThreadedSubprocess
from terminal import BufferedTerminal
from state import AppState

class UI():
    app_title = ''
    log_flag = ''
    refresh_rate = 1
    threads = {}
    def __init__(self):
        self.term = BufferedTerminal()
        self.state = AppState()

        #self.debug()
    def thread(self, key):
        return self.threads[key]['thread']


    def initialize_threads(self):
        for key in THREADS:
            thread = self.setup_thread(key)
            if self.threads[key]['required'] == True:
                thread.start()

    def setup_thread(self, key):

        if 'command' in self.threads[key]:
            command = self.threads[key]['command']
            thread = ThreadedSubprocess(command, self)
        else:
            target = getattr(self, key)
            thread = StoppableThread(target)

        self.threads[key]['thread'] = thread

        return self.threads[key]['thread']

    def screen_controller(self, thread):
        active_screen = ''
        with self.term.fullscreen(), self.term.cbreak(), self.term.hidden_cursor():
            while not thread.stop_event.is_set():
                if active_screen == self.state.active_screen:
                    continue
                else:
                    active_screen = self.state.active_screen

                    self.term.clear_buffer()

                self.forms_controller()
                sleep(self.refresh_rate)

    def draw_screen_buffer(self, thread):
        while not thread.stop_event.is_set():
            self.term.print_buffer()
            sleep(self.refresh_rate)

    def debug(self, text='', stop_buffer=False):

        text = str(text)
        if stop_buffer:
            self.thread('draw_screen_buffer').stop()
            print(text)
        else:
            text = self.add_border('Woops', text, self.term.width - 2, len(text))
            x = 1
            y = self.term.height - len(text)
            self.write_to_screen_buffer(text, x, y)

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
        top_line = top_left + horizontal + header + horizontal * (width - len(header) - 3) + top_right
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
    def write_to_screen_buffer(self, text, x=1, y=1):
        lines = text
        for i, line in enumerate(lines):
            self.term.write(x, y + i, line)

    def get_key_input(self):
        return self.term.inkey(timeout=0.1)  # Lower timeout for smoother blinking.

    def handle_key_input(self, selected=0, options_length=None, custom_handlers=None):
        action = None  # add this line
        key = self.get_key_input()

        if custom_handlers is not None:
            for handler in custom_handlers:
                action, selected = handler(key, selected)
                if action:
                    return action, selected

        if self.state.focus == "form":
            if key.is_sequence and key.name == 'KEY_ESCAPE':
                self.state.update({
                    'active_screen': 'home',
                    'focus': 'menu'
                })
                return 'exit', selected
        else:
            if key.is_sequence and key.name == 'KEY_ESCAPE':
                quit()
                return 'exit', selected

        return action, selected


if __name__ == "__main__":
    pass