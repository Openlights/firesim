import logging as log
import os.path

from PySide import QtCore, QtGui, QtDeclarative

from fixture import Fixture
from ui.canvaswidget import CanvasWidget
from ui.fixturewidget import FixtureWidget
from util.config import Config
from models.scene import Scene


class FireSimGUI(QtCore.QObject):

    def __init__(self, args=None):
        QtCore.QObject.__init__(self)

        self.app = QtGui.QApplication(["FireSim"])
        self.args = args
        self.config = Config("data/config.json")

        self.scene = Scene(os.path.join(self.config.get("scene_root"), self.args.scene) + ".json")

        QtDeclarative.qmlRegisterType(CanvasWidget, "FireSim", 1, 0, "SimCanvas")
        QtDeclarative.qmlRegisterType(FixtureWidget, "FireSim", 1, 0, "Fixture")

        self.view = QtDeclarative.QDeclarativeView()
        self.view.setSource(QtCore.QUrl('ui/qml/FireSimGUI.qml'))
        self.view.setWindowTitle("FireSim")
        self.view.setResizeMode(QtDeclarative.QDeclarativeView.SizeRootObjectToView)
        w, h = self.view.size().toTuple()
        self.view.setFixedSize(w, h)
        self.view.closeEvent = self.on_close

        self.context = self.view.rootContext()
        self.context.setContextProperty('main', self)

        self.root = self.view.rootObject()
        self.canvas = self.root.findChild(CanvasWidget)

        if self.scene.get("backdrop_enable", False):
            log.info("Loading backdrop from " + self.scene.get("backdrop_filename"))
            self.canvas.set_background_image(QtGui.QImage(self.scene.get("backdrop_filename")))

        self.fixture_list = [FixtureWidget(self.canvas)]

        log.info("FireSimGUI Ready.")
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