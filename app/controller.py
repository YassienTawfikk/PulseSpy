from PyQt5 import QtWidgets
from app.utils.clean_cache import remove_directories
from app.design.design import Ui_MainWindow
from app.services.upload_signal import SignalFileUploader
from app.services.playback_worker import PlaybackWorker
from pyqtgraph import mkPen
import numpy as np
from scipy.signal import find_peaks, butter, filtfilt
import time
from PyQt5.QtCore import QThread
from PyQt5.QtMultimedia import QSound


class MainWindowController:
    def __init__(self):
        self.app = QtWidgets.QApplication([])
        self.MainWindow = QtWidgets.QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.MainWindow)
        self.service = SignalFileUploader()

        # Window settings
        self.window_size = 5.0  # seconds of signal to display
        self.current_window_start = 0  # starting time of current window

        # Signal data
        self.x_data = None
        self.y_data = None
        self.filtered_signal = None
        self.qrs_peaks = None

        # Playback control
        self.is_playing = False
        self.playback_thread = None
        self.current_index = 0
        self.sampling_rate = 250  # Default sampling rate in Hz

        # Heart rate calculation
        self.current_heart_rate = 0
        self.heart_rate_history = []
        self.last_peak_time = 0

        self.ui.heart_rate_widget.setText("--")

        self.setup_connections()

        self.alert_sound = QSound("static/alarm/mixkit-warning-alarm-buzzer-991.wav")
        self.is_alarm = False


    def setup_connections(self):
        """Connect UI signals to slots."""
        self.ui.upload_button.clicked.connect(self.upload_signal)
        self.ui.clear_signal_button.clicked.connect(self.clear_signal)
        self.ui.toggle_play_pause_signal_button.clicked.connect(self.toggle_play_pause_signal)
        self.ui.quit_app_button.clicked.connect(self.close_app)
        self.ui.toggle_alarm_button.clicked.connect(self.toggle_alarm)

    def upload_signal(self):
        """Handle file upload and processing."""
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
        """Process and plot ECG signal."""
        try:
            # Estimate sampling rate if not available
            if len(self.x_data) > 1:
                self.sampling_rate = 1 / (self.x_data[1] - self.x_data[0])

            # Filter and find peaks
            self.filtered_signal = self.butter_lowpass_filter(
                ecg_signal,
                cutoff=15,  # Appropriate for QRS detection
                fs=self.sampling_rate
            )

            # Find peaks with ECG-specific parameters
            self.qrs_peaks, _ = find_peaks(
                self.filtered_signal,
                height=np.mean(self.filtered_signal) + 2 * np.std(self.filtered_signal),
                distance=self.sampling_rate * 0.2  # Minimum 200ms between peaks
            )
            # Calculate initial heart rate
            self.calculate_heart_rate()

            # Plot initial signal
            self.plot_signal()
        except Exception as e:
            print(f"Processing error: {e}")

    def calculate_heart_rate(self):
        """Calculate heart rate from detected peaks."""
        if self.qrs_peaks is None or len(self.qrs_peaks) < 2:
            self.current_heart_rate = 0
            return

        # Calculate RR intervals (time between peaks in seconds)
        rr_intervals = np.diff(self.x_data[self.qrs_peaks])

        # Filter out unrealistic intervals (e.g., <0.3s or >1.5s)
        valid_intervals = rr_intervals[(rr_intervals > 0.3) & (rr_intervals < 1.5)]

        if len(valid_intervals) > 0:
            # Calculate average heart rate in BPM
            avg_rr = np.mean(valid_intervals)
            self.current_heart_rate = 60 / avg_rr
        else:
            self.current_heart_rate = 0

        # Store for history
        self.heart_rate_history.append(self.current_heart_rate)

    def butter_lowpass_filter(self, data, cutoff, fs, order=4):
        """Apply Butterworth lowpass filter."""
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return filtfilt(b, a, data)

    def plot_signal(self, current_pos=None):
        """Plot ECG signal within the fixed window."""
        self.ui.ecg_plot_widget.clear()

        if self.filtered_signal is None or self.x_data is None:
            return

        # Calculate window bounds
        window_start = self.current_window_start
        window_end = window_start + self.window_size

        # Get indices for the current window
        mask = (self.x_data >= window_start) & (self.x_data <= window_end)
        x_window = self.x_data[mask]
        y_window = self.filtered_signal[mask]

        # Plot the windowed signal
        self.ui.ecg_plot_widget.plot(
            x_window,
            y_window,
            pen=mkPen('#033500', width=3),
        )

        # Highlight playback position if provided
        if current_pos is not None and current_pos > 0 and current_pos < len(self.x_data):
            mask_played = (self.x_data[:current_pos] >= window_start) & (self.x_data[:current_pos] <= window_end)
            self.ui.ecg_plot_widget.plot(
                self.x_data[:current_pos][mask_played],
                self.filtered_signal[:current_pos][mask_played],
                pen=mkPen('#55b135', width=2),
                name='Playback'
            )

        # Plot peaks within window - with additional validation
        if self.qrs_peaks is not None:
            valid_peaks = []
            for p in self.qrs_peaks:
                if (p < len(self.x_data) and
                        window_start <= self.x_data[p] <= window_end):
                    valid_peaks.append(p)

            if valid_peaks:
                self.ui.ecg_plot_widget.plot(
                    self.x_data[valid_peaks],
                    self.filtered_signal[valid_peaks],
                    pen=None,
                    symbol='x',
                    symbolSize=8,
                    symbolBrush='r',
                )

        # Set fixed X range and auto Y range
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

        self.playback_thread = QThread()
        self.worker = PlaybackWorker(self)
        self.worker.moveToThread(self.playback_thread)
        self.worker.update_signal.connect(self.update_playback_position)

        self.playback_thread.started.connect(self.worker.run)
        self.playback_thread.start()

    def update_playback_position(self, current_pos):
        """Slot to update playback position (runs in main thread)."""
        self.current_index = current_pos
        self.plot_signal(current_pos)

        # Check if we've passed any new peaks
        if self.qrs_peaks is not None and len(self.qrs_peaks) > 0:
            # Find all peaks that have been passed (index <= current_pos)
            passed_peaks = [p for p in self.qrs_peaks if p <= current_pos]

            # If we have passed at least 2 peaks, calculate heart rate
            if len(passed_peaks) >= 2:
                # Get the last two passed peaks
                last_two_peaks = passed_peaks[-2:]
                rr_interval = self.x_data[last_two_peaks[1]] - self.x_data[last_two_peaks[0]]

                # Calculate instant heart rate (not average)
                if 0.3 < rr_interval < 1.5:  # Valid RR interval range
                    self.current_heart_rate = 60 / rr_interval
                    self.update_heart_rate_display()

        # Auto-scroll window
        if self.current_index < len(self.x_data):
            current_time = self.x_data[self.current_index]
            if current_time > self.current_window_start + self.window_size:
                self.current_window_start = current_time - self.window_size / 2
                self.plot_signal(current_pos)

    def update_heart_rate_display(self):
        """Update the heart rate widget with current value."""
        if hasattr(self.ui, 'heart_rate_widget'):
            # Convert to integer and format as string
            hr_text = str(int(round(self.current_heart_rate)))
            self.ui.heart_rate_widget.setText(hr_text)

            # Force immediate update
            self.ui.heart_rate_widget.repaint()

            # Color coding "font": font_large,
            if self.current_heart_rate > 100:
                style = "color: red; font-size: 100px; font-weight: bold;"
                self.alert_sound.play()  # Play alert sound for high heart rate
                self.is_alarm=True
            elif self.current_heart_rate < 60:
                style = "color: red; font-size: 100px; font-weight: bold;"
                self.alert_sound.play()  # Play alert sound for high heart rate
                self.is_alarm=True
            else:
                style = "color: green; font-size: 100px; font-weight: bold;"
                self.alert_sound.stop()
                self.is_alarm=False

            self.ui.heart_rate_widget.setStyleSheet(style)

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
        self.is_alarm=False

    def toggle_alarm(self):
        if self.x_data is not None and self.y_data is not None:
            if not self.is_alarm:
                self.update_heart_rate_display()
                self.ui.toggle_alarm_button.setText("Alarm\nOFF")
            else:
                self.alert_sound.stop()
                self.ui.toggle_alarm_button.setText("Alarm\nON")
                self.is_alarm=False

    def run(self):
        """Start the application."""
        self.MainWindow.showFullScreen()
        self.app.exec_()

    def close_app(self):
        """Clean up and exit."""
        # self.stop_playback()
        self.app.quit()
        remove_directories()
