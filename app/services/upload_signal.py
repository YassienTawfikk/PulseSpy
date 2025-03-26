import os

import numpy as np
import pandas as pd
import wfdb
from PyQt5.QtWidgets import QFileDialog


class SignalFileUploader:
    last_opened_folder = "static/datasets"

    @classmethod
    def upload_signal_file(cls):
        """Open a file dialog to select a signal file (CSV or WFDB) and return its path."""
        try:
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getOpenFileName(
                parent=None,
                caption="Select Signal File",
                directory=cls.last_opened_folder,
                filter="CSV Files (*.csv);;WFDB Files (*.dat *.hea *.atr);;All Files (*)",
                options=options
            )
            if file_path:
                cls.last_opened_folder = os.path.dirname(file_path)
                return file_path
            return None
        except Exception as e:
            raise Exception(f"File upload error: {str(e)}")

    @staticmethod
    def load_signal_data(file_path):
        """Load signal data from CSV or WFDB files."""
        if not file_path:
            return None, None, None

        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext == ".csv":
                return SignalFileUploader.load_csv_data(file_path)
            elif file_ext in [".dat", ".hea", ".atr"]:
                record_name = os.path.splitext(file_path)[0]
                return SignalFileUploader.load_wfdb_data(record_name)
            print("Unsupported file format.")
            return None, None, None
        except Exception as e:
            print(f"Error loading signal: {e}")
            return None, None, None

    @staticmethod
    def load_csv_data(filepath):
        """Load ECG data from CSV."""
        try:
            data = pd.read_csv(filepath)
            if data.shape[1] < 2:
                raise ValueError("CSV must have at least 2 columns")

            x_data = data.iloc[:, 0].values  # Use numpy array instead of list
            y_data = data.iloc[:, 1].values
            return x_data, y_data, None
        except Exception as e:
            print(f"CSV load error: {e}")
            return None, None, None

    @staticmethod
    def load_wfdb_data(record_name):
        """Load WFDB record."""
        try:
            record = wfdb.rdrecord(record_name)
            annotation = wfdb.rdann(record_name, "atr")

            fs = record.fs
            signal = record.p_signal[:, 0]
            time = np.arange(len(signal)) / fs
            arrhythmia_times = annotation.sample / fs

            return time, signal, arrhythmia_times  # Return numpy arrays
        except Exception as e:
            print(f"WFDB load error: {e}")
            return None, None, None
