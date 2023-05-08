import threading
import subprocess
from const import *
class StoppableThread(threading.Thread):
    def __init__(self, target, args=(),  kwargs=None, *args_, **kwargs_):
        super().__init__(*args_, **kwargs_)
        self.target = target
        self.args = args
        self.kwargs = kwargs or {}
        self.kwargs['thread'] = self
        self.stop_event = threading.Event()
        self.started = False
    def has_started(self):
        return self.started
    def run(self):
        while not self.stop_event.is_set():
            self.target(*self.args, **self.kwargs)

    def can_start(self):
        return not (self.has_started() or self.stop_event.is_set())

    def start(self):
        self.started = True
        super().start()

    def stop(self):
        self.stop_event.set()

class ThreadedSubprocess(StoppableThread):
    log_flag = None
    process = None
    output = None
    started = False

    def __init__(self, command, app):
        super().__init__(target=self.capture_output)
        self.command = command
        self.log_flag = LOG_FLAG
        self.process = None
        self.app = app

    def capture_output(self, thread):
        while not self.stop_event.is_set():# this should be able to have is_alive()
            text = self.process.stdout.readline().decode().strip()
            if text == '' and self.process.poll() is not None:
                continue

            if self.log_flag in text:
                self.output = text.replace(self.log_flag, '') if self.log_flag and self.log_flag in text else text

    def start(self):
        command = [arg.format(**self.app.state) for arg in self.command]
        self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        super().start()

    def stop(self):
        super().stop()
        self.process.terminate()
        self.process.wait()
