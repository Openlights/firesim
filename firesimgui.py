import logging as log
import os.path

# This is a workaround for a Linux + NVIDIA + PyQt5 bug causing no graphics to be rendered
# because PyQt5 is linking to the wrong libGL.so / NVIDIA isn't overriding the MESA one.
# See: https://bugs.launchpad.net/ubuntu/+source/python-qt4/+bug/941826
from OpenGL import GL

from PyQt5.QtCore import pyqtProperty, pyqtSignal, pyqtSlot, QObject, QUrl, QTimer, QSize
from PyQt5.QtQml import qmlRegisterType, QQmlComponent
from PyQt5.QtQuick import QQuickView
from PyQt5.QtWidgets import QApplication

from ui.canvasview import CanvasView

from util.config import Config
from models.scene import Scene, FixtureIdError
from controllers.scenecontroller import SceneController
from controllers.netcontroller import NetController


class UIState(QObject):
    def __init__(self, parent=None):
        super(UIState, self).__init__(parent)
        self.parent = parent
        self._backdrop_enable = parent.scenecontroller.scene.get("backdrop-enable", False)
        self._labels_visible = parent.scenecontroller.scene.get("labels-visible", False)
        self._locked = parent.scenecontroller.scene.get("locked", False)
        self._center_visible = parent.scenecontroller.scene.get("center-visible", False)
        self._blur_enable = parent.scenecontroller.scene.get("blur-enable", False)

    backdrop_enable_changed = pyqtSignal()
    labels_visible_changed = pyqtSignal()
    locked_changed = pyqtSignal()
    center_visible_changed = pyqtSignal()
    blur_enable_changed = pyqtSignal()

    @pyqtProperty(bool, notify=backdrop_enable_changed)
    def backdrop_enable(self):
        return self._backdrop_enable

    @backdrop_enable.setter
    def backdrop_enable(self, val):
        if self._backdrop_enable != val:
            self._backdrop_enable = val
            self.backdrop_enable_changed.emit()

    @pyqtProperty(bool, notify=labels_visible_changed)
    def labels_visible(self):
        return self._labels_visible

    @labels_visible.setter
    def labels_visible(self, val):
        if self._labels_visible != val:
            self._labels_visible = val
            self.labels_visible_changed.emit()

    @pyqtProperty(bool, notify=locked_changed)
    def locked(self):
        return self._locked

    @locked.setter
    def locked(self, val):
        if self._locked != val:
            self._locked = val
            self.locked_changed.emit()

    @pyqtProperty(bool, notify=center_visible_changed)
    def center_visible(self):
        return self._center_visible

    @center_visible.setter
    def center_visible(self, val):
        if self._center_visible != val:
            self._center_visible = val
            self.center_visible_changed.emit()

    @pyqtProperty(bool, notify=blur_enable_changed)
    def blur_enable(self):
        return self._blur_enable

    @blur_enable.setter
    def blur_enable(self, val):
        if self._blur_enable != val:
            self._blur_enable = val
            self.blur_enable_changed.emit()


class FireSimGUI(QObject):

    def __init__(self, args=None):
        QObject.__init__(self)

        self.app = QApplication(["FireSim"])
        self.args = args
        self.config = Config("data/config.json")

        if self.args.profile:
            try:
                import yappi
                yappi.start()
            except ImportError:
                log.error("Could not enable YaPPI profiling")

        self._selected_fixture_strand = 0
        self._selected_fixture_address = 0
        self._selected_fixture_pixels = 0

        self.selected_fixture = None
        self.is_blurred = False

        self.scene = Scene(os.path.join(self.config.get("scene-root"), self.args.scene) + ".json")
        self.scenecontroller = SceneController(app=self, scene=self.scene)

        qmlRegisterType(CanvasView, "FireSim", 1, 0, "Canvas")

        self.view = QQuickView()

        self.view.setTitle("FireSim")
        self.view.setResizeMode(QQuickView.SizeRootObjectToView)

        self.view.closeEvent = self.on_close

        self.context = self.view.rootContext()
        self.context.setContextProperty('main', self)

        self.state = UIState(self)
        self.context.setContextProperty('App', self.state)

        self.state.backdrop_enable_changed.connect(self.scenecontroller.on_backdrop_enable_changed)
        self.state.labels_visible_changed.connect(self.scenecontroller.on_labels_visible_changed)

        self.fixture_info_list = []
        self.context.setContextProperty('fixtureInfoModel', self.fixture_info_list)

        self.view.setSource(QUrl('ui/qml/FireSimGUI.qml'))

        self.root = self.view.rootObject()
        self.canvas = self.root.findChild(CanvasView)
        self.canvas.gui = self

        cw, ch = self.scenecontroller.scene.extents()
        self.canvas.setWidth(cw)
        self.canvas.setHeight(ch)

        self.scenecontroller.set_canvas(self.canvas)
        self.canvas.controller.import_legacy_scene(self.scene)

        #self.net_thread = QThread()
        #self.net_thread.start()
        self.netcontroller = NetController(self)
        #self.netcontroller.moveToThread(self.net_thread)
        #self.netcontroller.start.emit()

        self.net_stats_timer = QTimer()
        self.net_stats_timer.setInterval(1000)
        self.net_stats_timer.timeout.connect(self.update_net_stats)
        self.net_stats_timer.start()

        self.redraw_timer = QTimer()
        self.redraw_timer.setInterval(33)
        self.redraw_timer.timeout.connect(self.scenecontroller.update_all)
        self.redraw_timer.start()

        self.netcontroller.new_frame.connect(self.canvas.controller.on_new_frame)

        self.view.setMinimumSize(QSize(800, 600))

        self.view.show()
        #self.view.showFullScreen()
        #self.view.setGeometry(self.app.desktop().availableGeometry())

    @pyqtSlot()
    def quit(self):
        self.app.quit()

    def run(self):
        return self.app.exec_()

    def on_close(self, e):
        self.netcontroller.running = False
        #self.net_thread.quit()
        if self.args.profile:
            try:
                import yappi
                yappi.get_func_stats().print_all()
            except ImportError:
                pass

    @pyqtSlot()
    def update_net_stats(self):
        self.canvas.net_stats = self.netcontroller.get_stats()

    @pyqtSlot()
    def on_network_event(self):
        self.canvas.update()

    @pyqtSlot()
    def on_btn_add_fixture(self):
        self.scenecontroller.add_fixture()

    @pyqtSlot()
    def on_btn_clear(self):
        self.scenecontroller.clear_fixtures()

    @pyqtSlot()
    def on_btn_save(self):
        self.scenecontroller.save_scene()

    def widget_selected(self, selected, fixture, multi):
        self.selected_fixture = None

        if multi:
            pass
        else:
            if selected:
                self.selected_fixture_strand = fixture.strand()
                self.selected_fixture_address = fixture.address()
                self.selected_fixture_pixels = fixture.pixels()
            else:
                self.selected_fixture_strand = 0
                self.selected_fixture_address = 0
                self.selected_fixture_pixels = 0

        if selected:
            self.selected_fixture = fixture

    def update_selected_fixture_properties(self):
        if self.selected_fixture is not None:
            new_strand = int(self.selected_fixture_strand)
            new_address = int(self.selected_fixture_address)
            if (self.selected_fixture.strand() != new_strand
                or self.selected_fixture.address() != new_address):
                try:
                    self.scenecontroller.update_fixture(
                        self.selected_fixture, new_strand, new_address
                    )
                except FixtureIdError:
                    log.exception("Error updating fixture properties")
                    return
            self.selected_fixture.set_pixels(int(self.selected_fixture_pixels))
            self.selected_fixture.get_widget().update()

    def _get_selected_fixture_strand(self):
        return self._selected_fixture_strand

    def _set_selected_fixture_strand(self, strand):
        if self._selected_fixture_strand == strand:
            return
        self._selected_fixture_strand = strand
        self.update_selected_fixture_properties()
        self.on_selected_fixture_strand.emit()

    def _get_selected_fixture_address(self):
        return self._selected_fixture_address

    def _set_selected_fixture_address(self, address):
        if self._selected_fixture_address == address:
            return
        self._selected_fixture_address = address
        self.update_selected_fixture_properties()
        self.on_selected_fixture_address.emit()

    def _get_selected_fixture_pixels(self):
        return self._selected_fixture_pixels

    def _set_selected_fixture_pixels(self, pixels):
        if self._selected_fixture_pixels == pixels:
            return
        self._selected_fixture_pixels = pixels
        self.update_selected_fixture_properties()
        self.on_selected_fixture_pixels.emit()

    on_selected_fixture_strand = pyqtSignal()
    on_selected_fixture_address = pyqtSignal()
    on_selected_fixture_pixels = pyqtSignal()

    selected_fixture_strand = pyqtProperty(int, _get_selected_fixture_strand, _set_selected_fixture_strand, notify=on_selected_fixture_strand)
    selected_fixture_address = pyqtProperty(int, _get_selected_fixture_address, _set_selected_fixture_address, notify=on_selected_fixture_address)
    selected_fixture_pixels = pyqtProperty(int, _get_selected_fixture_pixels, _set_selected_fixture_pixels, notify=on_selected_fixture_pixels)

