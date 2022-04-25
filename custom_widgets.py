from PyQt6.QtWidgets import QWidget, QLabel, QComboBox

from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import serial
from serial.tools import list_ports
from obtained_data import ObtainedData


class PIDInformer(QWidget):
    def __init__(self):
        super().__init__()
        # create labels
        self.p_label = QLabel('P')
        self.i_label = QLabel('I')
        self.d_label = QLabel('D')
        self.t_label = QLabel('T')
        self.p_value_label = QLabel('0')
        self.i_value_label = QLabel('0')
        self.d_value_label = QLabel('0')
        self.t_value_label = QLabel('0')

        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.p_label, 0, 0)
        layout.addWidget(self.i_label, 1, 0)
        layout.addWidget(self.d_label, 2, 0)
        layout.addWidget(self.t_label, 3, 0)
        layout.addWidget(self.p_value_label, 0, 1)
        layout.addWidget(self.i_value_label, 1, 1)
        layout.addWidget(self.d_value_label, 2, 1)
        layout.addWidget(self.t_value_label, 3, 1)
        self.setLayout(layout)

    def set_values(self, obtained_data: ObtainedData):
        self.p_value_label.setText(str(obtained_data.p[-1]))
        self.i_value_label.setText(str(obtained_data.i[-1]))
        self.d_value_label.setText(str(obtained_data.d[-1]))
        self.t_value_label.setText(str(obtained_data.temperature[-1]))


class BaudrateCombo(QComboBox):
    def __init__(self):
        super().__init__()
        self.addItems([str(i) for i in serial.Serial.BAUDRATES])
        self.setCurrentIndex(self.count() - 1)


class PortCombo(QComboBox):
    def __init__(self):
        super().__init__()
        self.update_ports()

    def showPopup(self) -> None:
        self.update_ports()
        super().showPopup()

    def update_ports(self):
        # delete all ports
        while self.count() > 0:
            self.removeItem(0)
        # set available
        self.addItems([i.device for i in list_ports.comports()])


class MplCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure()
        self.axes = self.fig.add_subplot(1, 1, 1)
        super().__init__(self.fig)

    def update_plot(self, obtained_data: ObtainedData):
        data_to_draw = [obtained_data.output,
                        obtained_data.temperature,
                        obtained_data.set_point]

        if not len(self.axes.lines):
            for i in data_to_draw:
                self.axes.plot(obtained_data.datetime, i,)
            self.axes.grid()

        # set new data to display
        for i, data in enumerate(data_to_draw):
            self.axes.lines[i].set_xdata(obtained_data.datetime)
            self.axes.lines[i].set_ydata(data)

        # recompute limits of axes
        self.axes.relim()
        # apply new limits
        self.axes.autoscale_view()
        # Trigger the mpl_canvas to update and redraw.
        self.draw()
