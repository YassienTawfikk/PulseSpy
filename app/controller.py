from PyQt5 import QtWidgets
from app.utils.clean_cache import remove_directories
from app.design.design import Ui_MainWindow
from app.services.upload_signal import SignalFileUploader
from app.services.playback_worker import PlaybackWorker
from pyqtgraph import mkPen
import numpy as np
import time
from PyQt5.QtCore import QThread
from PyQt5.QtMultimedia import QSound

from app.processing.filtering import bandpass_filter
from app.processing.segmentation import segment_ecg_pipeline
from app.processing.classifier import ECGClassifier


class MainWindowController:
    def __init__(self):
        self.app = QtWidgets.QApplication([])
        self.MainWindow = QtWidgets.QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.MainWindow)
        self.service = SignalFileUploader()

        # Window settings
        self.window_size = 5.0
        self.current_window_start = 0

        # Signal data
        self.x_data = None
        self.y_data = None
        self.filtered_signal = None
        self.qrs_peaks = None

        # Playback control
        self.is_playing = False
        self.playback_thread = None
        self.current_index = 0
        self.sampling_rate = 250

        # Heart rate calculation
        self.current_heart_rate = 0
        self.heart_rate_history = []
        self.last_peak_time = 0

        self.ui.heart_rate_widget.setText("--")

        self.setup_connections()

        # alarm settings
        self.alert_sound = QSound("static/alarm/ECG_Alarm.wav")
        self.alarm_enabled = True  # master ON / OFF
        self.alarm_pause = False  # user-pressed “pause” button
        self.alarm_cooldown_sec = 4  # minimum seconds between repeats
        self._last_alarm_ts = 0  # internal timestamp

        self.valid_intervals = None

        # Load classifier once
        self.classifier = ECGClassifier("models/arrhythmia_model.h5")

    def setup_connections(self):
        self.ui.upload_button.clicked.connect(self.upload_signal)
        self.ui.clear_signal_button.clicked.connect(self.clear_signal)
        self.ui.toggle_play_pause_signal_button.clicked.connect(self.toggle_play_pause_signal)
        self.ui.quit_app_button.clicked.connect(self.close_app)
        self.ui.toggle_alarm_button.clicked.connect(self.toggle_alarm)
        self.ui.pause_alarm_button.clicked.connect(self.pause_alarm)

    def upload_signal(self):
        if self.x_data is not None and self.y_data is not None:
            self.clear_signal()
        filepath = self.service.upload_signal_file()
        if not filepath:
            return

        x_data, y_data, _ = self.service.load_signal_data(filepath)
        if x_data is not None and y_data is not None:
            self.x_data = x_data
            self.y_data = y_data
            self.process_ecg_signal(y_data)

    def process_ecg_signal(self, ecg_signal):
        try:
            if len(self.x_data) > 1:
                self.sampling_rate = 1 / (self.x_data[1] - self.x_data[0])

            self.filtered_signal = bandpass_filter(ecg_signal, fs=self.sampling_rate)

            # Segment the filtered signal around R-peaks
            beats = segment_ecg_pipeline(self.filtered_signal, sampling_rate=self.sampling_rate)

            # Classify the first few beats (optional debug)
            for i, beat in enumerate(beats[:3]):
                result = self.classifier.predict(beat)
                print(f"Beat {i}: {result}")

            # Detect QRS peaks for heart rate calc and plotting
            from biosppy.signals import ecg
            qrs_info = ecg.ecg(signal=self.filtered_signal, sampling_rate=self.sampling_rate, show=False)
            self.qrs_peaks = qrs_info['rpeaks']

            self.calculate_heart_rate()
            self.plot_signal()

        except Exception as e:
            print(f"Processing error: {e}")

    def calculate_heart_rate(self):
        if self.qrs_peaks is None or len(self.qrs_peaks) < 2:
            self.current_heart_rate = 0
            return

        rr_intervals = np.diff(self.x_data[self.qrs_peaks])
        self.valid_intervals = rr_intervals[(rr_intervals > 0.3) & (rr_intervals < 1.5)]

        if len(self.valid_intervals) > 0:
            avg_rr = np.mean(self.valid_intervals)
            self.current_heart_rate = 60 / avg_rr
        else:
            self.current_heart_rate = 0

        self.heart_rate_history.append(self.current_heart_rate)

    def plot_signal(self, current_pos=None):
        """Plots the filtered ECG signal with optional playback and QRS peaks."""
        self.ui.ecg_plot_widget.clear()

        if self.filtered_signal is None or self.x_data is None:
            return

        # Define window range
        window_start = self.current_window_start
        window_end = window_start + self.window_size
        mask = (self.x_data >= window_start) & (self.x_data <= window_end)
        x_window = self.x_data[mask]
        y_window = self.filtered_signal[mask]

        # Plot main ECG signal in dark green
        self.ui.ecg_plot_widget.plot(x_window, y_window, pen=mkPen('#033500', width=3))

        # Plot already-played signal portion in light green (during playback)
        if current_pos is not None and 0 < current_pos < len(self.x_data):
            mask_played = (self.x_data[:current_pos] >= window_start) & (self.x_data[:current_pos] <= window_end)
            self.ui.ecg_plot_widget.plot(
                self.x_data[:current_pos][mask_played],
                self.filtered_signal[:current_pos][mask_played],
                pen=mkPen('#55b135', width=2),
                name='Playback'
            )

        # Plot QRS peaks as red circles
        if self.qrs_peaks is not None:
            valid_peaks = [p for p in self.qrs_peaks if
                           p < len(self.x_data) and window_start <= self.x_data[p] <= window_end]
            for p in valid_peaks:
                self.ui.ecg_plot_widget.plot(
                    [self.x_data[p]],
                    [self.filtered_signal[p]],
                    pen=None,
                    symbol='o',
                    symbolSize=10,
                    symbolBrush='r',
                    symbolPen='r'
                )

        # Set plot view range
        self.ui.ecg_plot_widget.setXRange(window_start, window_end)
        self.ui.ecg_plot_widget.enableAutoRange(axis='y')

    def toggle_play_pause_signal(self):
        """Toggle signal playback."""
        if not self.is_playing:
            self.start_playback()
        else:
            self.stop_playback()

    def start_playback(self):
        """Start signal playback using QThread."""
        if self.filtered_signal is None:
            return
        self.is_playing = True
        self.ui.toggle_play_pause_signal_button.setText("Pause")
        self.alarm_pause = False

        self.playback_thread = QThread()
        self.worker = PlaybackWorker(self)
        self.worker.moveToThread(self.playback_thread)
        self.worker.update_signal.connect(self.update_playback_position)

        self.playback_thread.started.connect(self.worker.run)
        self.playback_thread.start()

    def update_playback_position(self, current_pos: int):
        """
        Slot called from the PlaybackWorker thread.
        Keeps the GUI in-sync with playback progress and updates HR in real-time.
        """
        # --- 1. Clamp index to valid range --------------------------------------
        if current_pos >= len(self.x_data):
            # End of signal reached – stop gracefully
            self.stop_playback()
            return

        self.current_index = current_pos

        # --- 2. Update scrolling window -----------------------------------------
        self.current_window_start = max(0,
                                        self.x_data[self.current_index] - self.window_size)

        # --- 3. Re-draw ----------------------------------------------------------
        self.plot_signal(self.current_index)

        # --- 4. Heart-rate update using the two most recent passed peaks --------
        if self.qrs_peaks is not None and len(self.qrs_peaks) > 1:
            # Peaks already behind (≤ current index)
            passed = [p for p in self.qrs_peaks if p <= self.current_index]

            if len(passed) >= 2:
                last, prev = passed[-1], passed[-2]
                rr = self.x_data[last] - self.x_data[prev]
                if 0.3 < rr < 1.5:  # physiologically plausible
                    self.current_heart_rate = 60 / rr
                    self.update_heart_rate_display()

        # --- 5. Auto-scroll window edge -----------------------------------------
        if self.x_data[self.current_index] > self.current_window_start + self.window_size:
            self.current_window_start = self.x_data[self.current_index] - self.window_size

    def get_current_heart_rate(self):
        return self.current_heart_rate if self.current_heart_rate > 0 else None

    def _should_fire_alarm(self) -> bool:
        """Return True if alarm is allowed to play now."""
        if not self.alarm_enabled or self.alarm_pause:
            return False
        return (time.time() - self._last_alarm_ts) > self.alarm_cooldown_sec

    def _start_alarm(self):
        if self._should_fire_alarm():
            self.alert_sound.play()
            self._last_alarm_ts = time.time()

    def _stop_alarm(self):
        """Silence buzzer and re-arm pause flag."""
        self.alert_sound.stop()
        # If we stopped programmatically (normal rhythm / clear / stop),
        # release any manual pause so the next event can fire again.
        self.alarm_pause = False

    def update_heart_rate_display(self):
        """Colour-code BPM label, set diagnosis, and manage alarm."""
        hr = self.get_current_heart_rate()

        # default UI
        style = "color: gray;"
        text = "--"
        diagnosis = ""

        # classify & colour
        if hr is not None:
            text = f"{int(round(hr))}"
            if hr < 60:
                style = "color: blue;"
                diagnosis = "Bradycardia"
                self._start_alarm()
            elif hr > 100:
                style = "color: red;"
                diagnosis = "Tachycardia"
                self._start_alarm()
            else:  # Normal 60-100 BPM
                style = "color: green;"
                self._stop_alarm()  # also clears self.alarm_pause

        # update labels
        self.ui.heart_rate_widget.setText(text)
        self.ui.heart_rate_widget.setStyleSheet(style)
        self.ui.diagnosis_label.setText(diagnosis)

    def stop_playback(self):
        """Stop signal playback safely."""
        if hasattr(self, 'worker'):
            self.worker.is_playing = False
        if hasattr(self, 'playback_thread'):
            self.playback_thread.quit()
            self.playback_thread.wait()

        self.is_playing = False
        self.ui.toggle_play_pause_signal_button.setText("Play")
        self.current_index = 0
        self.alert_sound.stop()

    def play_signal(self):
        """Playback thread function."""
        self.current_index = 0
        step_size = int(self.sampling_rate * 0.05)  # 50ms step

        while self.is_playing and self.current_index < len(self.filtered_signal):
            start_time = time.time()

            self.current_index = min(self.current_index + step_size, len(self.filtered_signal))
            self.plot_signal(self.current_index)

            # Maintain real-time playback speed
            elapsed = time.time() - start_time
            time.sleep(max(0.05 - elapsed, 0))

        self.stop_playback()

    def clear_signal(self):
        """Reset the display and clear loaded data."""
        self.stop_playback()
        self.ui.ecg_plot_widget.clear()
        self.x_data = None
        self.y_data = None
        self.filtered_signal = None
        self.qrs_peaks = None
        self.current_window_start = 0
        self.current_heart_rate = 0
        self.heart_rate_history = []
        self.last_peak_time = 0
        self.ui.heart_rate_widget.setText("--")
        self.alert_sound.stop()
        self.ui.toggle_alarm_button.setText("Alarm\nOFF")
        self.ui.diagnosis_label.setText("#######")

    def toggle_alarm(self):
        """Master enable/disable switch."""
        self.alarm_enabled = not self.alarm_enabled

        if self.alarm_enabled:
            self.ui.toggle_alarm_button.setText("Alarm ON")
            # re-enable future automatic firing
            self.alarm_pause = False
        else:
            self.ui.toggle_alarm_button.setText("Alarm OFF")
            self._stop_alarm()

    def pause_alarm(self):
        """Toggle temporary mute without switching master ON/OFF."""
        self.alarm_pause = not self.alarm_pause
        if self.alarm_pause:
            self._stop_alarm()
            self.ui.pause_alarm_button.setText("Resume Alarm")
        else:
            self.ui.pause_alarm_button.setText("Pause Alarm")
            # If HR still out of range, restart buzzer immediately
            self._start_alarm()

    def run(self):
        """Start the application."""
        self.MainWindow.showFullScreen()
        self.app.exec_()

    def close_app(self):
        """Clean up and exit."""
        # self.stop_playback()
        self.app.quit()
        remove_directories()
