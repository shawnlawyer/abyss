from lib import load_config
from util import DataObject
from const import *
from ui import UI
from menus import Menus
from forms import Forms
from reports import Reports
from lang.en import *
from os.path import join, expanduser
settings = DataObject(SETTINGS)
defaults = DataObject(DEFAULTS)

class GUI(UI, Menus, Forms, Reports):
    # Your GUI class code...

    def __init__(self):
        super().__init__()
        self.app_title = APP_TITLE
        self.log_flag = LOG_FLAG
        self.refresh_rate = REFRESH_RATE
        self.state.active_screen = 'home'
        self.state.focus = 'menu'
        self.settings = load_config(join(expanduser("~"), '.abyss'))

        if not isinstance(self.settings, DataObject) :
            self.settings = settings
            self.state.active_screen = 'application_settings'

        self.threads = THREADS
        self.initialize_threads()



if __name__ == "__main__":
    pass

