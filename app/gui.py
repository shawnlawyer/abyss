import threading
import subprocess
from time import sleep
from util import DataObject
from const import *
from ui import UI
from threads import StoppableThread, ThreadedSubprocess
from menus import Menus, MENUS
from forms import Forms
from lang.en import *

settings = DataObject(SETTINGS)
defaults = DataObject(DEFAULTS)

class GUI(UI, Menus, Forms, ThreadedSubprocess,):
    # Your GUI class code...

    def __init__(self):
        super().__init__()
        self.app_title = APP_TITLE
        self.menus = MENUS
        self.log_flag = LOG_FLAG
        self.state.active_screen = 'main_menu'
        self.threads = {}
        self.setup_thread('draw_screen').start()

    def draw_screen(self, thread=None):
        active_screen = ''
        with self.term.fullscreen(), self.term.cbreak(), self.term.hidden_cursor():
            while True if not thread else not thread.stop_event.is_set():
                if active_screen == self.state.active_screen:
                    continue
                else:
                    active_screen = self.state.active_screen

                self.reset_screen()

                if self.state.active_screen == 'create_project':
                    self.create_project_config_form()
                elif 'train' in self.threads:

                    if 'train' in self.threads and 'draw_training_progress_report' not in self.threads:
                        self.setup_thread('draw_training_progress_report').start()

                if 'draw_menus' not in self.threads:
                    self.setup_thread('draw_menus').start()


    def redraw_screen(self):
        if 'draw_screen' in self.threads:
            self.threads['draw_screen'].stop()
            self.setup_thread('draw_screen').start()
        else:
            self.draw_screen()

    def draw_training_progress_report(self, thread=None):
        status = loading()
        while True if not thread else not thread.stop_event.is_set():
            status = loading(status)
            if self.threads['train'].output is None:
                training_info_report = f"Loading Model:{self.state.configs.model_filename}\nOne Moment{status}"
            else:
                training_info_data = self.threads['train'].output
                training_info_report = '\n'.join(self.json_to_report(training_info_data))

            width = 50
            height = 8
            x = 75
            y = 0

            self.draw_box('Training Progress', training_info_report, width, height, x, y)
            sleep(1)

    def setup_thread(self, key):
        if 'target' in threads.get(key):
            target = getattr(self, threads[key]['target'])
            self.threads[key] = StoppableThread(target)
        else:

            command = [arg.format(**self.state) for arg in threads[key]['command']]
            self.threads[key] = ThreadedSubprocess(command, self.log_flag)
        return self.threads[key]

    def do_actions(self, key):
        if key in self.threads and self.threads[key].process.poll() is not None:
            return

        self.setup_thread(key).start()
        if 'callback' in ACTIONS[key]:
            self.setup_thread(ACTIONS[key]['callback']).start()
def loading(loading=''):
    if loading == '':
        loading = '.'
    elif loading == '.':
        loading = '..'
    elif loading == '..':
        loading = '...'
    else:
        loading = ''
    return loading

if __name__ == "__main__":
    key='train'
    state = {"config_file":"lstm3.json"}
    command = [arg.format(**state) for arg in threads[key]['command']]
    thread = ThreadedSubprocess(command, LOG_FLAG)
    thread.start()
    while True:
        print(thread.output)
        sleep(1)

