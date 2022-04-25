from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLineEdit, QGridLayout
from PyQt6.QtCore import pyqtSignal, QThread, QTimer, Qt

import sys

from custom_widgets import PIDInformer, BaudrateCombo, PortCombo, MplCanvas
from data_extractor import DataExtractor


class MainWindow(QMainWindow):
    # make a stop and start signals to communicate with the worker in another thread
    stop_recording_signal = pyqtSignal()
    start_recording_signal = pyqtSignal()
    connect_signal = pyqtSignal()
    disconnect_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Arduino Plot")

        # create widgets
        self.send_btn = QPushButton("send nudes")
        self.connect_btn = QPushButton("Connect")
        self.port_combo = PortCombo()
        self.baudrate_combo = BaudrateCombo()
        self.mpl_canvas = MplCanvas()
        self.text_input = QLineEdit()
        self.pid_informer = PIDInformer()

        # self.resize(QSize(1500, 800))

        # fill the layout
        self.layout = QGridLayout()
        self.layout.addWidget(self.mpl_canvas, 0, 0, 5, 5)
        self.layout.addWidget(self.baudrate_combo, 5, 0, 1, 1)
        self.layout.addWidget(self.port_combo, 5, 1, 1, 1)
        self.layout.addWidget(self.connect_btn, 5, 2, 1, 1)
        self.layout.addWidget(self.text_input, 6, 0, 1, 5)
        self.layout.addWidget(self.send_btn, 6, 6, 1, 1)
        self.layout.addWidget(self.pid_informer, 0, 6)

        # set layout as CentralWidget
        self.container = QWidget()
        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)

        # Thread:
        self.thread = QThread()
        self.worker = DataExtractor()
        self.worker.moveToThread(self.thread)

        self.connect_signal.connect(self.worker.connect_to_port)
        self.disconnect_signal.connect(self.worker.disconnect)

        self.worker.connected.connect(self.enable_recording)
        self.worker.failed_to_connect.connect(self.on_disconnect)
        self.worker.disconnected_signal.connect(self.on_disconnect)
        self.worker.finished.connect(self.on_disconnect)

        self.start_recording_signal.connect(self.worker.start_record)
        self.stop_recording_signal.connect(self.worker.stop_record, type=Qt.ConnectionType.DirectConnection)

        self.thread.start()

        # connect buttons to their functions
        self.connect_btn.clicked.connect(self.connect_action)
        self.send_btn.clicked.connect(self.send_handler)
        self.text_input.returnPressed.connect(self.send_handler)

        self.show()

        # Setup a timer to trigger redraw by calling update_plot.
        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_visual_data)
        self.timer.start()

    def connect_action(self):
        if self.connect_btn.text() == "Connect":
            self.worker.port_str = self.port_combo.currentText()
            self.worker.baudrate = self.baudrate_combo.currentText()
            self.connect_signal.emit()
            self.connect_btn.setDisabled(True)
        else:
            self.stop_recording_signal.emit()
            self.disconnect_signal.emit()
            self.connect_btn.setText("Connect")

    def enable_recording(self):
        # self.btn_record.setEnabled(True)
        self.start_recording_signal.emit()
        self.connect_btn.setText("Disconnect")
        self.connect_btn.setEnabled(True)

    def on_disconnect(self):
        # set everything to initial state
        self.connect_btn.setEnabled(True)
        self.connect_btn.setText("Connect")
        # self.btn_record.setDisabled(True)
        # self.btn_record.setText("Start record")

    def update_visual_data(self):
        self.pid_informer.set_values(self.worker.obtained_data)
        self.mpl_canvas.update_plot(self.worker.obtained_data)
        return

    def send_handler(self):
        message = self.text_input.text().strip()
        self.worker.send_message(message)
        self.text_input.clear()


app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()
