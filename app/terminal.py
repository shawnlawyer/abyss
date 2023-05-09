import threading
import blessed

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

if __name__ == "__main__":
    pass