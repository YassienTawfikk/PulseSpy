from PyQt5.QtCore import QObject, pyqtSignal
import time


class PlaybackWorker(QObject):
    update_signal = pyqtSignal(int)

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.is_playing = True

    def run(self):
        step_size = int(self.controller.sampling_rate * 0.05)
        current_index = 0

        while self.is_playing and current_index < len(self.controller.filtered_signal):
            start_time = time.time()
            current_index = min(current_index + step_size, len(self.controller.filtered_signal))
            self.update_signal.emit(current_index)

            elapsed = time.time() - start_time
            time.sleep(max(0.05 - elapsed, 0))
