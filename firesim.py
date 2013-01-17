import sys
from PySide import QtCore, QtGui, QtDeclarative


class FireSimGUI(QtCore.QObject):

    def __init__(self):
        QtCore.QObject.__init__(self)

        self.app = QtGui.QApplication(["FireSim"])

        self.view = QtDeclarative.QDeclarativeView()
        self.view.setSource(QtCore.QUrl('ui/qml/firesimgui.qml'))
        self.view.setResizeMode(QtDeclarative.QDeclarativeView.SizeRootObjectToView)

        self.app.exec_()

if __name__ == "__main__":
    firesim = FireSimGUI()

