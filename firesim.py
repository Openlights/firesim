import sys
from PySide import QtCore, QtGui, QtDeclarative

from ui.simcanvas import SimCanvasDeclarative


class FireSimGUI(QtCore.QObject):

    def __init__(self):
        QtCore.QObject.__init__(self)

        self.app = QtGui.QApplication(["FireSim"])

        QtDeclarative.qmlRegisterType(SimCanvasDeclarative, "FireSim", 1, 0, "SimCanvas")

        self.view = QtDeclarative.QDeclarativeView()
        self.view.setSource(QtCore.QUrl('ui/qml/FireSimGUI.qml'))
        self.view.setResizeMode(QtDeclarative.QDeclarativeView.SizeRootObjectToView)
        self.view.closeEvent = self.on_close

        self.context = self.view.rootContext()
        self.context.setContextProperty('main', self)

        self.root = self.view.rootObject()
        self.canvas = self.root.findChild(SimCanvasDeclarative)

        self.view.show()
        sys.exit(self.app.exec_())

    def on_close(self, e):
        pass

    @QtCore.Slot()
    def on_btn_add_fixture(self):
        fixc = QtDeclarative.QDeclarativeComponent(self.view.engine(), QtCore.QUrl("ui/qml/Fixture_Strand.qml"))
        if fixc.isReady():
            fix = fixc.create(self.context)

    @QtCore.Slot()
    def on_btn_clear(self):
        self.canvas.set_color((255, 0, 255))


if __name__ == "__main__":
    sim = FireSimGUI()

