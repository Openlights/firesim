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
        self.view.setSource(QtCore.QUrl('ui/qml/FireSimGUI.qml'))
        self.view.setResizeMode(QtDeclarative.QDeclarativeView.SizeRootObjectToView)
        self.view.closeEvent = self.on_close

        self.context = self.view.rootContext()
        self.context.setContextProperty('main', self)

        self.root = self.view.rootObject()
        self.canvas = self.root.findChild(CanvasWidget)

        self.fix0 = FixtureWidget(self.canvas)
        self.fix0.setParentItem(self.canvas)

        self.canvas.set_background_image(QtGui.QImage("light_dome.png"))

        self.fixture_list = [Fixture(32, (1, 1, 64, 2))]

        #self.canvas.update_fixtures(self.fixture_list)

        self.view.show()

    def run(self):
        return self.app.exec_()

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