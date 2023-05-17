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
    debug = False
    debug_log = []
    def __init__(self):
        self.term = BufferedTerminal()
        self.state = AppState()

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

    def log_debug(self, text='', stop_buffer=False):
        if self.debug is False:
            return

        self.debug_log.extend(str(text).split('\n'))
        if stop_buffer:
            self.thread('draw_screen_buffer').stop()
            print('\n'.join(self.debug_log[-4:]))
        else:
            text = self.add_border('Woops', '\n'.join(self.debug_log[-4:]), self.term.width - 2, 4)
            x = 1
            y = self.term.height - 6
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

if __name__ == "__main__":
    pass