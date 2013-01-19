from PySide import QtCore, QtGui, QtDeclarative

from fixture import Fixture
from ui.canvaswidget import CanvasWidget
from ui.fixturewidget import FixtureWidget


class FireSimGUI(QtCore.QObject):

    def __init__(self):
        QtCore.QObject.__init__(self)

        self.app = QtGui.QApplication(["FireSim"])

        QtDeclarative.qmlRegisterType(CanvasWidget, "FireSim", 1, 0, "SimCanvas")
        QtDeclarative.qmlRegisterType(FixtureWidget, "FireSim", 1, 0, "Fixture")

        self.view = QtDeclarative.QDeclarativeView()
        self.view.setSource(QtCore.QUrl('ui/qml/firesimgui.qml'))
        self.view.setResizeMode(QtDeclarative.QDeclarativeView.SizeRootObjectToView)
        self.view.closeEvent = self.on_close

        self.context = self.view.rootContext()
        self.context.setContextProperty('main', self)

        self.root = self.view.rootObject()
        self.canvas = self.root.findChild(CanvasWidget)

        self.canvas.set_background_image(QtGui.QImage("light_dome.png"))

        self.fixture_list = [FixtureWidget(self.canvas)]

        self.view.show()

    def run(self):
        return self.app.exec_()

    def on_close(self, e):
        pass

    @QtCore.Slot()
    def on_btn_add_fixture(self):
        self.fixture_list.append(FixtureWidget(self.canvas))

    @QtCore.Slot()
    def on_btn_clear(self):
        while len(self.fixture_list) > 0:
            fixture = self.fixture_list.pop()
            fixture.deleteLater()