import threading

class AppState(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self
        self.configs = None
        self.config_file = None
        self.active_screen = None
        self.sidebar_menu = None
        self.form = None
        self.lock = threading.Lock()
        self.focus = None
        self.input_handlers = {'sidebar_menu':None, 'form':None}

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def update(self, new_dict):
        with self.lock:
            for key, value in new_dict.items():
                setattr(self, key, value)


if __name__ == "__main__":
    pass