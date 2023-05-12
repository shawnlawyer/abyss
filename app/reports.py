from time import sleep
from const import *

class Reports():

    def draw_training_progress_report(self, thread=None):
        def loading(loading='', length=8 , loading_str='.'):
            if loading == (loading_str) * length:
                return ''
            return loading + '.'

        status = loading()
        while True if not thread else not thread.stop_event.is_set():
            status = loading(status)
            if self.thread('train').output is None:
                training_info_report = f"Loading Model:{self.state.configs.model_filename}\nOne Moment{status}"
            else:
                training_info_data = self.thread('train').output
                training_info_report = '\n'.join(self.json_to_report(training_info_data))
            width = REPORTS_WIDTH
            height = REPORTS_HEIGHT
            x = REPORTS_X
            y = REPORTS_Y

            text = self.add_border('Training Progress', training_info_report, width, height)
            self.write_to_screen_buffer(text, x, y)
            sleep(self.refresh_rate)


if __name__ == "__main__":
    pass

