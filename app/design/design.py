from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QDateTime, QTimer
import pyqtgraph as pg

COMMON_PUSHBUTTON_STYLESHEET = """
QPushButton {
    color: white;
    border: none;
    text-align: center;
    text-decoration: none;
    font-size: 16px;
    margin: 4px 2px;
    border-radius: 8px;
    border:1px solid white;
}
"""

QUIT_APP_BUTTON_STYLESHEET = """
QPushButton {
    color: rgb(255, 255, 255);
    border: 3px solid rgb(255, 255, 255);
}
QPushButton:hover {
    border-color: rgb(253, 94, 80);
    color: rgb(253, 94, 80);
}
"""

BACKGROUND_BLACK_STYLESHEET = """
background-color:black
"""

HEADER_STYLESHEET = """
background-color:#2b2d2c;
"""

GROUPBOX_STYLESHEET = """
color:#55b135
"""

LABEL_WHITE_STYLESHEET = """
color:white
"""


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        # ---------------------------------------------------------
        # 1) Screen-Specific Setup
        # ---------------------------------------------------------
        self.screen_size = QtWidgets.QApplication.primaryScreen().size()
        self.screen_width = self.screen_size.width()
        self.screen_height = self.screen_size.height()

        # Make the main window fill the current screen
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(self.screen_width, self.screen_height)
        MainWindow.setWindowTitle("MainWindow")
        MainWindow.setStyleSheet(BACKGROUND_BLACK_STYLESHEET)

        # Keep a style for groupboxes
        self.groupbox_style = GROUPBOX_STYLESHEET

        # Create the central widget
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)

        # ---------------------------------------------------------
        # 2) Build Each Section
        # ---------------------------------------------------------
        self.setupHeader(MainWindow)
        self.setupControllerButtons(MainWindow)
        self.setupGroupBoxes(MainWindow)

    # ----------------------------------------------------------------
    # Helper Methods: createButton, createLabel, createGroupBox, addGraphView
    # ----------------------------------------------------------------
    def createButton(self, text, parent, max_size, stylesheet, object_name, cursor=None, font=None):
        button = QtWidgets.QPushButton(parent)
        button.setText(text)
        button.setMaximumSize(max_size)
        button.setStyleSheet(stylesheet)
        button.setObjectName(object_name)
        if cursor:
            button.setCursor(QtGui.QCursor(cursor))
        if font:
            button.setFont(font)
        return button

    def createLabel(self, text, parent, stylesheet, object_name,
                    max_size=None, min_size=None, alignment=None, font=None):
        label = QtWidgets.QLabel(parent)
        label.setObjectName(object_name)
        label.setText(text)
        if stylesheet:
            label.setStyleSheet(stylesheet)
        if max_size:
            label.setMaximumSize(max_size)
        if min_size:
            label.setMinimumSize(min_size)
        if alignment:
            label.setAlignment(alignment)
        if font:
            label.setFont(font)
        return label

    def createGroupBox(self, title, size, style=None, isGraph=False, content=None):
        groupBox = QtWidgets.QGroupBox()
        groupBox.setTitle(title)
        groupBox.setMinimumSize(size)
        groupBox.setMaximumSize(size)
        groupBox.setStyleSheet(style if style else self.groupbox_style)

        if isGraph:
            widget = self.addGraphView(groupBox)
        else:
            if content is None:
                content = {
                    "text": "",
                    "font": None,  # Default font
                    "color": "white"  # Default text color
                }
            label = self.createLabel(
                text=content.get("text", ""),
                parent=groupBox,
                stylesheet=f"color: {content.get('color', 'white')}; background-color: transparent; border: none;",
                object_name="labelInsideGroupBox",
                max_size=QtCore.QSize(600, 250),
                alignment=QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter,
                font=content.get("font", None)
            )
            group_box_layout = QtWidgets.QVBoxLayout(groupBox)
            group_box_layout.setContentsMargins(10, 10, 10, 10)
            group_box_layout.addWidget(label)
            widget = label

        return groupBox, widget

    def addGraphView(self, group_box):
        plot_widget = pg.PlotWidget()
        plot_widget.getAxis('left').setTicks([])
        plot_widget.getAxis('bottom').setTicks([])
        plot_widget.getAxis('left').setPen(None)
        plot_widget.getAxis('bottom').setPen(None)
        plot_widget.setLabel('left', 'mV')

        color = pg.mkPen('#033500')
        plot_widget.getAxis('left').setTextPen(color)
        plot_widget.addLegend()
        graph_layout = QtWidgets.QVBoxLayout()
        graph_layout.addWidget(plot_widget)
        graph_layout.setContentsMargins(5, 25, 5, 5)
        group_box.setLayout(graph_layout)
        return plot_widget

    # ----------------------------------------------------------------
    # Setup Sections
    # ----------------------------------------------------------------
    def setupHeader(self, MainWindow):
        """
        Original code:
            self.Header.setGeometry(QtCore.QRect(-1, 0, 1441, 91))
        We'll turn that into fractions of screen_width and screen_height.
        """
        header_x = 0
        header_y = 0
        header_w = int(self.screen_width * (1441 / 1440.0))
        header_h = int(self.screen_height * (91 / 900.0))

        self.Header = QtWidgets.QWidget(self.centralwidget)
        self.Header.setGeometry(QtCore.QRect(header_x, header_y, header_w, header_h))
        self.Header.setStyleSheet(HEADER_STYLESHEET)
        self.Header.setObjectName("Header")

        # Create your "verticalLayoutWidget" in the top-right corner
        # Original geometry was (1350, 0, 72, 91). We'll scale similarly:
        icon_layout_x = int(self.screen_width * (1350 / 1440.0))
        icon_layout_y = 0
        icon_layout_w = int(self.screen_width * (72 / 1440.0))
        icon_layout_h = header_h

        self.verticalLayoutWidget = QtWidgets.QWidget(self.Header)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(icon_layout_x, icon_layout_y,
                                                           icon_layout_w, icon_layout_h))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")

        self.title_layout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.title_layout.setContentsMargins(0, 0, 0, 0)
        self.title_layout.setObjectName("title_layout")

        # Icon label
        self.icon_label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.icon_label.setMaximumSize(QtCore.QSize(60, 60))
        self.icon_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.icon_label.setText("")
        self.icon_label.setPixmap(QtGui.QPixmap("app/design/ui/../../../static/images/icon.png"))
        self.icon_label.setScaledContents(True)
        self.icon_label.setAlignment(QtCore.Qt.AlignCenter)
        self.icon_label.setObjectName("icon_label")
        self.title_layout.addWidget(self.icon_label)

        # Title label
        font_title = QtGui.QFont()
        font_title.setFamily("Luminari")
        font_title.setPointSize(15)
        font_title.setBold(False)
        font_title.setItalic(True)
        font_title.setUnderline(False)
        font_title.setWeight(50)
        font_title.setKerning(False)

        self.title_label = self.createLabel(
            text="Pulse Spy",
            parent=self.verticalLayoutWidget,
            stylesheet=LABEL_WHITE_STYLESHEET,
            object_name="title_label",
            max_size=QtCore.QSize(70, 20),
            alignment=QtCore.Qt.AlignCenter,
            font=font_title
        )
        self.title_layout.addWidget(self.title_label)

        # The horizontal layout for time/person/diagnosis
        hlayout_x = int(self.screen_width * (40 / 1440.0))
        hlayout_y = int(self.screen_height * (9 / 900.0))
        hlayout_w = int(self.screen_width * (1241 / 1440.0))
        hlayout_h = int(self.screen_height * (81 / 900.0))

        self.horizontalLayoutWidget_4 = QtWidgets.QWidget(self.Header)
        self.horizontalLayoutWidget_4.setGeometry(QtCore.QRect(hlayout_x, hlayout_y,
                                                               hlayout_w, hlayout_h))
        self.horizontalLayoutWidget_4.setObjectName("horizontalLayoutWidget_4")

        self.header_layout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_4)
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.header_layout.setObjectName("header_layout")

        # Time label
        font_time = QtGui.QFont()
        font_time.setBold(True)
        font_time.setItalic(True)
        font_time.setWeight(75)

        self.time_label = self.createLabel(
            text="",  # We'll fill in actual time via updateTime()
            parent=self.horizontalLayoutWidget_4,
            stylesheet=LABEL_WHITE_STYLESHEET,
            object_name="time_label",
            max_size=QtCore.QSize(80, 70),
            font=font_time
        )
        self.header_layout.addWidget(self.time_label)

        # Person data label
        font_person = QtGui.QFont()
        font_person.setBold(True)
        font_person.setItalic(True)
        font_person.setWeight(75)

        self.person_data_label = self.createLabel(
            text="Patient: Name - Age - Sex - Height - Weight",
            parent=self.horizontalLayoutWidget_4,
            stylesheet=LABEL_WHITE_STYLESHEET,
            object_name="person_data_label",
            max_size=QtCore.QSize(410, 70),
            font=font_person
        )
        self.header_layout.addWidget(self.person_data_label)

        # Diagnosis label
        font_diagnosis = QtGui.QFont()
        font_diagnosis.setBold(True)
        font_diagnosis.setItalic(True)
        font_diagnosis.setWeight(75)

        self.diagnosis_label = self.createLabel(
            text="Diagnosis: XXXXXXX",
            parent=self.horizontalLayoutWidget_4,
            stylesheet=LABEL_WHITE_STYLESHEET,
            object_name="diagnosis_label",
            max_size=QtCore.QSize(410, 70),
            font=font_diagnosis
        )
        self.header_layout.addWidget(self.diagnosis_label)

        # ---------------------------------------------------------
        #  Attach a timer to update the time label every second
        # ---------------------------------------------------------
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateTime)
        self.timer.start(1000)  # 1 second interval
        # Immediately set the correct time at startup
        self.updateTime()

    def updateTime(self):
        """Update the time label with the current time every second."""
        current_time = QDateTime.currentDateTime().toString('hh:mm AP')
        self.time_label.setText(current_time)

    def setupControllerButtons(self, MainWindow):
        buttons_x = int(self.screen_width * (60 / 1440.0))
        buttons_y = int(self.screen_height * (730 / 900.0))
        buttons_w = int(self.screen_width * (1321 / 1440.0))
        buttons_h = int(self.screen_height * (141 / 900.0))

        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(buttons_x, buttons_y, buttons_w, buttons_h))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")

        self.controller_buttons_layout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.controller_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.controller_buttons_layout.setObjectName("controller_buttons_layout")

        self.toggle_alarm_button = self.createButton(
            text="Alarm\nOFF",
            parent=self.horizontalLayoutWidget,
            max_size=QtCore.QSize(120, 90),
            stylesheet=COMMON_PUSHBUTTON_STYLESHEET,
            object_name="toggle_alarm_button",
            cursor=QtCore.Qt.PointingHandCursor
        )
        self.controller_buttons_layout.addWidget(self.toggle_alarm_button)

        self.pause_alarm_button = self.createButton(
            text="Alarm Pause",
            parent=self.horizontalLayoutWidget,
            max_size=QtCore.QSize(120, 90),
            stylesheet=COMMON_PUSHBUTTON_STYLESHEET,
            object_name="pause_alarm_button",
            cursor=QtCore.Qt.PointingHandCursor
        )
        self.controller_buttons_layout.addWidget(self.pause_alarm_button)

        self.upload_button = self.createButton(
            text="Upload",
            parent=self.horizontalLayoutWidget,
            max_size=QtCore.QSize(120, 90),
            stylesheet=COMMON_PUSHBUTTON_STYLESHEET,
            object_name="upload_button",
            cursor=QtCore.Qt.PointingHandCursor
        )
        self.controller_buttons_layout.addWidget(self.upload_button)

        self.toggle_play_pause_signal_button = self.createButton(
            text="Play",
            parent=self.horizontalLayoutWidget,
            max_size=QtCore.QSize(120, 90),
            stylesheet=COMMON_PUSHBUTTON_STYLESHEET,
            object_name="toggle_play_pause_signal_button",
            cursor=QtCore.Qt.PointingHandCursor
        )
        self.controller_buttons_layout.addWidget(self.toggle_play_pause_signal_button)

        self.reset_signal_button = self.createButton(
            text="Reset",
            parent=self.horizontalLayoutWidget,
            max_size=QtCore.QSize(120, 90),
            stylesheet=COMMON_PUSHBUTTON_STYLESHEET,
            object_name="reset_signal_button",
            cursor=QtCore.Qt.PointingHandCursor
        )
        self.controller_buttons_layout.addWidget(self.reset_signal_button)

        self.clear_signal_button = self.createButton(
            text="Clear",
            parent=self.horizontalLayoutWidget,
            max_size=QtCore.QSize(120, 90),
            stylesheet=COMMON_PUSHBUTTON_STYLESHEET,
            object_name="clear_signal_button",
            cursor=QtCore.Qt.PointingHandCursor
        )
        self.controller_buttons_layout.addWidget(self.clear_signal_button)

        quit_font = QtGui.QFont()
        quit_font.setFamily("Hiragino Sans GB")
        quit_font.setPointSize(50)
        quit_font.setBold(True)
        quit_font.setItalic(False)
        quit_font.setUnderline(False)
        quit_font.setWeight(75)
        quit_font.setStrikeOut(False)
        quit_font.setKerning(False)

        self.quit_app_button = self.createButton(
            text="X",
            parent=self.horizontalLayoutWidget,
            max_size=QtCore.QSize(70, 70),
            stylesheet=QUIT_APP_BUTTON_STYLESHEET,
            object_name="quit_app_button",
            cursor=QtCore.Qt.PointingHandCursor,
            font=quit_font
        )
        self.controller_buttons_layout.addWidget(self.quit_app_button)

    def setupGroupBoxes(self, MainWindow):
        gb_area_x = int(self.screen_width * (10 / 1440.0))
        gb_area_y = int(self.screen_height * (170 / 900.0))
        gb_area_w = int(self.screen_width * (1401 / 1440.0))
        gb_area_h = int(self.screen_height * (481 / 900.0))

        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(gb_area_x, gb_area_y, gb_area_w, gb_area_h))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")

        self.groupboxes_layout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.groupboxes_layout.setContentsMargins(0, 0, 0, 0)
        self.groupboxes_layout.setObjectName("groupboxes_layout")

        ecg_w = int(gb_area_w * (1170 / 1401.0))
        ecg_h = int(gb_area_h * (340 / 481.0))

        self.ecg_groupbox, self.ecg_plot_widget = self.createGroupBox(
            title="ECG",
            size=QtCore.QSize(ecg_w, ecg_h),
            style=self.groupbox_style,
            isGraph=True
        )
        self.groupboxes_layout.addWidget(self.ecg_groupbox)

        hr_w = int(gb_area_w * (230 / 1401.0))
        hr_h = int(gb_area_h * (340 / 481.0))

        font_large = QtGui.QFont()
        font_large.setPointSize(100)  # Large font size
        font_large.setBold(True)

        self.heart_rate_groupbox, self.heart_rate_widget = self.createGroupBox(
            title="Heart Rate",
            size=QtCore.QSize(hr_w, hr_h),
            style=self.groupbox_style,
            isGraph=False,
            content={
                "text": "72",  # Example heart rate value
                "font": font_large,
                "color": "#55b135"  # Green text color
            }
        )
        self.groupboxes_layout.addWidget(self.heart_rate_groupbox)

    def updateHeartRate(self, new_rate):
        # Check if the heart rate widget has been created and is a QLabel
        if isinstance(self.heart_rate_widget, QtWidgets.QLabel):
            self.heart_rate_widget.setText(new_rate)
