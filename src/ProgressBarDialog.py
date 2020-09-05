from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui
import sys
import time

class ProgressBarDialog(QtWidgets.QDialog):
    def __init__(self, min_value: int, max_value: int):
        QtWidgets.QDialog.__init__(self)
        self.progress_bar = QtWidgets.QProgressBar()
        self.setMinimum(min_value)
        self.setMaximum(max_value)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)
    def setMinimum(self, value: int):
        self.progress_bar.setMinimum(value)
    def setMaximum(self, value: int):
        self.progress_bar.setMaximum(value)
    def setValue(self, value: int):
        self.progress_bar.setValue(value)

class ProgressBarDialogDuo(QtWidgets.QDialog):
    def __init__(self, min_value_1: int, max_value_1: int, min_value_2: int, max_value_2: int):
        QtWidgets.QDialog.__init__(self)
        self.progress_bar_1 = QtWidgets.QProgressBar()
        self.progress_bar_2 = QtWidgets.QProgressBar()
        self.setMinimum_1(min_value_1)
        self.setMaximum_1(max_value_1)
        self.setMinimum_2(min_value_2)
        self.setMaximum_2(max_value_2)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.progress_bar_1)
        layout.addWidget(self.progress_bar_2)
        self.setLayout(layout)
    def setMinimum_1(self, value: int):
        self.progress_bar_1.setMinimum(value)
    def setMaximum_1(self, value: int):
        self.progress_bar_1.setMaximum(value)
    def setValue_1(self, value: int):
        self.progress_bar_1.setValue(value)
    def setMinimum_2(self, value: int):
        self.progress_bar_2.setMinimum(value)
    def setMaximum_2(self, value: int):
        self.progress_bar_2.setMaximum(value)
    def setValue_2(self, value: int):
        self.progress_bar_2.setValue(value)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    pd = ProgressBarDialogDuo(0, 100, 2, 50)
    pd.show()
    time.sleep(5)
    pd.setValue_1(10)
    pd.setValue_2(3)
    time.sleep(5)
    pd.setValue_1(100)
    pd.setValue_2(43)
    
    sys.exit(app.exec_())