import os
import pandas as pd
from PyQt5.QtWidgets import QFileDialog


class SignalFileUploader:
    last_opened_folder = "static/datasets"

    @classmethod
    def upload_signal_csv(cls):
        """Open a file dialog to select a CSV file, return the file path or None."""
        try:
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getOpenFileName(
                parent=None,
                caption="Select Signal CSV",
                directory=cls.last_opened_folder,
                filter="CSV Files (*.csv);;All Files (*)",
                options=options
            )

            if file_path:
                cls.last_opened_folder = os.path.dirname(file_path)
                return file_path
            else:
                print("No CSV file selected.")
                return None
        except Exception as e:
            raise Exception(f"An error occurred while uploading the CSV file: {str(e)}")

    @staticmethod
    def load_csv_data(filepath):
        """Load CSV data from a file, handling potential errors."""
        try:
            data = pd.read_csv(filepath)
            x_data = data.iloc[:, 0].tolist()
            y_data = data.iloc[:, 1].tolist()
            return x_data, y_data
        except pd.errors.EmptyDataError:
            print("No data: The file is empty.")
            return None, None
        except pd.errors.ParserError:
            print("Error parsing data: Check the file format.")
            return None, None
        except FileNotFoundError:
            print(f"File not found: {filepath}")
            return None, None
        except Exception as e:
            print(f"Failed to read or parse the CSV file: {e}")
            return None, None
