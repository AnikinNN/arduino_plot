import serial
from datetime import datetime
from obtained_data import ObtainedData
from PyQt6.QtCore import pyqtSignal, QObject

from recorder import Recorder


class DataExtractor(QObject):
    finished = pyqtSignal()
    connected = pyqtSignal()
    failed_to_connect = pyqtSignal()
    disconnected_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.obtained_data = ObtainedData()

        self.continue_record = None
        self.port = None
        self.port_str = None
        self.baudrate = None
        self.disconnect_req = False

        self.recorder = None

    def start_record(self):
        self.continue_record = True
        self.recorder = Recorder()
        while self.continue_record:
            raw_data = self.port.read_until().decode().strip()
            self.obtained_data.append_data(raw_data, datetime.now())
            self.recorder.write(raw_data, datetime.now())
        self.recorder.close()
        self.finished.emit()  # emit the finished signal when the loop is done

    def stop_record(self):
        self.continue_record = False

    def connect_to_port(self):
        if self.port_str == "emulator":
            self.port = serial.serial_for_url("emulator://", baudrate=self.baudrate, timeout=10)
        else:
            try:
                self.port = serial.Serial(port=self.port_str, baudrate=self.baudrate, timeout=2)
            except serial.serialutil.SerialException as e:
                print(e)
                self.failed_to_connect.emit()
                return
        try:
            answer = self.port.read_until().decode().strip()
        except UnicodeDecodeError as e:
            answer = str(e)
        if answer != "kalich ready":
            self.failed_to_connect.emit()
            print(f"got unexpected message:\n{answer}\nDisconnecting")
            self.disconnect()
        else:
            print(answer)
            self.send_message('n\n')
            self.connected.emit()

    def send_message(self, message: str):
        if self.port is not None:
            if self.port.isOpen():
                if message[-1] != '\n':
                    message = message + '\n'
                self.port.write(message.encode())
            else:
                print(f'port is closed, attempt to send {message}')
        else:
            print(f'port is None, attempt to send {message}')

    def disconnect(self):
        if self.port.isOpen():
            self.port.close()
        self.disconnected_signal.emit()
