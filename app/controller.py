from PyQt5 import QtWidgets
from app.utils.clean_cache import remove_directories
from app.design.design import Ui_MainWindow
from app.services.upload_signal import SignalFileUploader
from pyqtgraph import mkPen


class MainWindowController:
    def __init__(self):
        self.app = QtWidgets.QApplication([])
        self.MainWindow = QtWidgets.QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.MainWindow)
        self.service = SignalFileUploader()
        self.setupConnections()

    def setupConnections(self):
        self.ui.quit_app_button.clicked.connect(self.closeApp)
        self.ui.upload_button.clicked.connect(self.upload_signal)
        self.ui.clear_signal_button.clicked.connect(self.clear_signal)

    def upload_signal(self):
        filepath = self.service.upload_signal_csv()
        if filepath:
            x_data, y_data = self.service.load_csv_data(filepath)
            if x_data and y_data:
                self.plot_data(x_data, y_data)

    def plot_data(self, x_data, y_data):
        try:
            self.ui.ecg_plot_widget.clear()
            self.ui.ecg_plot_widget.plot(x_data, y_data, pen=mkPen('#55b135', width=3))
        except Exception as e:
            print(f"Failed to plot data: {e}")

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
