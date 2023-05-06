import threading
import subprocess
class StoppableThread(threading.Thread):
    def __init__(self, target, args=(), kwargs=None, *args_, **kwargs_):
        super().__init__(*args_, **kwargs_)
        self.target = target
        self.args = args
        self.kwargs = kwargs or {}
        self.kwargs['thread'] = self
        self.stop_event = threading.Event()

    def run(self):
        while not self.stop_event.is_set():
            self.target(*self.args, **self.kwargs)

    def stop(self):
        self.stop_event.set()

class ThreadedSubprocess(StoppableThread):
    log_flag = None
    process = None
    output = None

    def __init__(self, cmd, log_flag):
        super().__init__(target=self.capture_output)
        self.cmd = cmd
        self.log_flag = log_flag

    def capture_output(self, thread):
        while self.process.poll() is None and not thread.stop_event.is_set():
            str = self.process.stdout.readline().decode().strip()
            if (str == '' and self.process.poll() is not None ) or (self.log_flag != '' and self.log_flag not in str):
                continue
            self.output = str.replace(self.log_flag, '') if self.log_flag and self.log_flag in str else str

    def start(self):
        self.process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        super().start()

    def stop(self):
        super().stop()
        self.process.terminate()
        self.process.wait()
