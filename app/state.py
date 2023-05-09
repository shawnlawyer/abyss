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

if __name__ == "__main__":
    pass