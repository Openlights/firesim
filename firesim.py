import sys
from PySide import QtCore, QtGui, QtDeclarative

from fixture import Fixture
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
        assert isinstance(self.canvas, SimCanvasDeclarative)

        self.fixture_list = [Fixture(32, (1, 1, 64, 2))]

        self.canvas.update_fixtures(self.fixture_list)

        self.view.show()
        sys.exit(self.app.exec_())

    def on_close(self, e):
        pass

    def update_fixtures(self):
        self.canvas.update_fixtures(self.fixture_list)

    @QtCore.Slot()
    def on_btn_add_fixture(self):
        for i, _ in enumerate(self.fixture_list):
            self.fixture_list[i].set_all((255, 0, 255))
        self.update_fixtures()

    @QtCore.Slot()
    def on_btn_clear(self):
        self.fixture_list = []
        self.update_fixtures()


if __name__ == "__main__":
    sim = FireSimGUI()

