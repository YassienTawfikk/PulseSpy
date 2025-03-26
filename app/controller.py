from PyQt5 import QtWidgets
from app.utils.clean_cache import remove_directories
from app.design.design import Ui_MainWindow
from app.services.upload_signal import SignalFileUploader
from pyqtgraph import mkPen
import numpy as np
import pandas as pd
from scipy.signal import find_peaks, butter, filtfilt
import time
import threading

class MainWindowController:
    def __init__(self):
        self.app = QtWidgets.QApplication([])
        self.MainWindow = QtWidgets.QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.MainWindow)
        self.service = SignalFileUploader()
        self.setupConnections()

        self.x_data = None
        self.y_data = None
        self.is_playing = False
        self.playback_thread = None
        self.current_index = 0  # To keep track of the current position in the signal

    def setupConnections(self):
        self.ui.quit_app_button.clicked.connect(self.closeApp)
        self.ui.upload_button.clicked.connect(self.upload_signal)
        self.ui.clear_signal_button.clicked.connect(self.clear_signal)
        self.ui.toggle_play_pause_signal_button.clicked.connect(self.toggle_play_pause_signal)

    def upload_signal(self):
        filepath = self.service.upload_signal_csv()
        if filepath:
            self.x_data, self.y_data = self.service.load_csv_data(filepath)
            if self.x_data is not None and self.y_data is not None:
                self.process_ecg_signal(self.y_data)  # Process the ECG data

    def process_ecg_signal(self, ecg_signal):
        # Filter the signal to extract QRS
        fs = 1.0  # Sampling frequency (adjust as necessary)
        cutoff = 0.1  # Cut-off frequency for low-pass filter
        filtered_signal = self.butter_lowpass_filter(ecg_signal, cutoff, fs)

        # Find QRS peaks
        self.qrs_peaks = self.find_qrs_peaks(filtered_signal)

        # Smooth the signal
        self.smoothed_signal = self.moving_average(filtered_signal, window_size=5)

        # Plot the signals
        self.plot_signals(self.smoothed_signal, self.qrs_peaks)

    def butter_lowpass_filter(self, data, cutoff, fs, order=5):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return filtfilt(b, a, data)

    def find_qrs_peaks(self, signal):
        peaks, _ = find_peaks(signal, height=0.5)
        return peaks

    def moving_average(self, data, window_size):
        return np.convolve(data, np.ones(window_size)/window_size, mode='valid')

    def plot_signals(self, smoothed_signal, qrs_peaks):
        try:
            self.ui.ecg_plot_widget.clear()
            # Plot smoothed signal
            self.ui.ecg_plot_widget.plot(smoothed_signal, pen=mkPen('b', width=1), name='Smoothed Signal')


        except Exception as e:
            print(f"Failed to plot signals: {e}")

    def clear_signal(self):
        try:
            self.ui.ecg_plot_widget.clear()
            print("Signal cleared successfully.")
            self.is_playing = False
            self.current_index = 0
            self.ui.toggle_play_pause_signal_button.setText("Play")
        except Exception as e:
            print(f"Failed to clear the signal: {e}")

    def toggle_play_pause_signal(self):
        if not self.is_playing:
            self.is_playing = True
            self.ui.toggle_play_pause_signal_button.setText("Pause")
            self.playback_thread = threading.Thread(target=self.play_signal)
            self.playback_thread.start()
        else:
            self.is_playing = False
            self.ui.toggle_play_pause_signal_button.setText("Play")

    def play_signal(self):
        while self.current_index < len(self.qrs_peaks) and self.is_playing:
            peak = self.qrs_peaks[self.current_index]
            # Draw the signal up to the current peak
            self.ui.ecg_plot_widget.clear()
            self.ui.ecg_plot_widget.plot(self.smoothed_signal, pen=mkPen('b', width=1), name='Smoothed Signal')
            self.ui.ecg_plot_widget.plot(self.smoothed_signal[:peak], pen=mkPen('b', width=2), name='Current Signal')

            # Highlight the current QRS peak
            self.ui.ecg_plot_widget.plot([peak, peak], [min(self.smoothed_signal), max(self.smoothed_signal)], pen=mkPen('k', width=10))

            self.current_index += 6
            time.sleep(1)  # Delay for demonstration (adjust as necessary)

        if not self.is_playing:
            self.current_index = 0  # Reset index when stopped

    def clear_signal(self):
        try:
            self.ui.ecg_plot_widget.clear()
            print("Signal cleared successfully.")
        except Exception as e:
            print(f"Failed to clear the signal: {e}")

    def run(self):
        self.MainWindow.showFullScreen()
        self.app.exec_()

    def closeApp(self):
        remove_directories()
        self.app.quit()
