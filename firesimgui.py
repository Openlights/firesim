import logging as log
import os.path

from PySide import QtCore, QtGui, QtDeclarative

from ui.canvaswidget import CanvasWidget
from ui.fixturewidget import FixtureWidget
from util.config import Config
from models.scene import Scene
from models.fixture import FixtureWrapper
from ui.fixtureinfolistmodel import FixtureInfoListModel
from controllers.scenecontroller import SceneController


class FireSimGUI(QtCore.QObject):

    def __init__(self, args=None):
        QtCore.QObject.__init__(self)

        self.app = QtGui.QApplication(["FireSim"])
        self.args = args
        self.config = Config("data/config.json")

        self.scene = Scene(os.path.join(self.config.get("scene_root"), self.args.scene) + ".json")
        self.scenecontroller = SceneController(scene=self.scene)

        QtDeclarative.qmlRegisterType(CanvasWidget, "FireSim", 1, 0, "SimCanvas")
        QtDeclarative.qmlRegisterType(FixtureWidget, "FireSim", 1, 0, "Fixture")

        self.view = QtDeclarative.QDeclarativeView()

        self.view.setWindowTitle("FireSim")
        self.view.setResizeMode(QtDeclarative.QDeclarativeView.SizeRootObjectToView)
        w, h = self.view.size().toTuple()
        self.view.setFixedSize(w, h)
        self.view.closeEvent = self.on_close

        self.context = self.view.rootContext()
        self.context.setContextProperty('main', self)

        self.fixture_info_list = []
        self.context.setContextProperty('fixtureInfoModel', self.fixture_info_list)

        self.view.setSource(QtCore.QUrl('ui/qml/FireSimGUI.qml'))

        self.root = self.view.rootObject()
        self.canvas = self.root.findChild(CanvasWidget)

        self.scenecontroller.set_canvas(self.canvas)

        self.root.backdrop_showhide_callback.connect(self.on_btn_backdrop_showhide)

        self.fixture_wrapper_list = [FixtureWrapper(fix) for fix in self.scenecontroller.get_fixtures()]
        self.fixture_info_list = FixtureInfoListModel(self.fixture_wrapper_list)
        self.context.setContextProperty('fixtureInfoModel', self.fixture_info_list)

        log.info("FireSimGUI Ready.")
        self.view.show()

    def run(self):
        return self.app.exec_()

    def on_close(self, e):
        pass

    @QtCore.Slot(result=bool)
    def is_backdrop_enabled(self):
        return self.scenecontroller.scene.get("backdrop_enable", False)

    @QtCore.Slot()
    def on_btn_add_fixture(self):
        self.scenecontroller.add_fixture()

    @QtCore.Slot()
    def on_btn_clear(self):
        self.scenecontroller.clear_fixtures()

    @QtCore.Slot()
    def on_btn_save(self):
        self.scenecontroller.save_scene()

    @QtCore.Slot(result=bool)
    def on_btn_backdrop_showhide(self, obj):
        enabled = self.scenecontroller.toggle_background_enable()
        if enabled:
            obj.setProperty("text", "Hide Backdrop")
        else:
            obj.setProperty("text", "Show Backdrop")
        return enabled

