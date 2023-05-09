from time import sleep
from util import DataObject
from const import *
from ui import UI
from menus import Menus, MENUS
from forms import Forms
from lang.en import *

settings = DataObject(SETTINGS)
defaults = DataObject(DEFAULTS)

class GUI(UI, Menus, Forms,):
    # Your GUI class code...

    def __init__(self):
        super().__init__()
        self.app_title = APP_TITLE
        self.menus = MENUS
        self.log_flag = LOG_FLAG
        self.refresh_rate = REFRESH_RATE
        self.debug_pause_rate = DEBUG_PAUSE_RATE
        self.state.active_screen = 'main_menu'

        self.threads = {}
        for key in THREADS:
            thread = self.setup_thread(key)
            if THREADS[key]['required'] == True:
                thread.start()

        #self.debug()

    def screen_controller(self, thread):
        active_screen = ''
        show_menus = True # this is a bit of a hack for now but
        with self.term.fullscreen(), self.term.cbreak(), self.term.hidden_cursor():
            while not thread.stop_event.is_set():
                if active_screen == self.state.active_screen:
                    continue
                else:
                    active_screen = self.state.active_screen

                self.forms_controller()

                sleep(self.refresh_rate)

    def draw_screen_buffer(self, thread):
        while not thread.stop_event.is_set():
            if self.debug_pause_rate > 0:
                sleep(self.debug_pause_rate)
            self.term.print_buffer()
            sleep(self.refresh_rate)

    def draw_training_progress_report(self, thread=None):

        def loading(loading='', length=8 , loading_str='.'):
            if loading == (loading_str) * length:
                return ''
            return loading + '.'

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
            x = self.term.width // 2 - width // 2
            y = 14

            text = self.add_border('Training Progress', training_info_report, width, height)
            self.write_to_screen_buffer(text, x, y)
            sleep(self.refresh_rate)


if __name__ == "__main__":
    pass

