import logging as log
import os.path

from PyQt5 import QtCore
from PyQt5.QtQml import qmlRegisterType, QQmlComponent
from PyQt5.QtQuick import QQuickView
from PyQt5.QtWidgets import QApplication

from ui.canvaswidget import CanvasWidget
from ui.fixturewidget import FixtureWidget
from util.config import Config
from models.scene import Scene, FixtureIdError
from controllers.scenecontroller import SceneController
from controllers.netcontroller import NetController


class FireSimGUI(QtCore.QObject):

    def __init__(self, args=None):
        QtCore.QObject.__init__(self)

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

        self.scene = Scene(os.path.join(self.config.get("scene_root"), self.args.scene) + ".json")
        self.scenecontroller = SceneController(app=self, scene=self.scene)

        qmlRegisterType(CanvasWidget, "FireSim", 1, 0, "SimCanvas")
        qmlRegisterType(FixtureWidget, "FireSim", 1, 0, "Fixture")

        self.view = QQuickView()

        self.view.setTitle("FireSim")
        self.view.setResizeMode(QQuickView.SizeRootObjectToView)

        self.view.closeEvent = self.on_close

        self.context = self.view.rootContext()
        self.context.setContextProperty('main', self)

        self.fixture_info_list = []
        self.context.setContextProperty('fixtureInfoModel', self.fixture_info_list)

        self.view.setSource(QtCore.QUrl('ui/qml/FireSimGUI.qml'))

        self.root = self.view.rootObject()
        self.canvas = self.root.findChild(CanvasWidget)
        self.canvas.gui = self

        cw, ch = self.scenecontroller.scene.extents()
        self.canvas.setWidth(cw)
        self.canvas.setHeight(ch)

        self.scenecontroller.set_canvas(self.canvas)

        self.root.backdrop_showhide_callback.connect(self.on_btn_backdrop_showhide)
        self.root.labels_showhide_callback.connect(self.on_btn_labels_showhide)
        self.root.lock_callback.connect(self.on_btn_lock)
        self.root.show_center_callback.connect(self.on_btn_show_center)
        self.root.toggle_blurred_callback.connect(self.on_btn_toggle_blurred)

        #self.net_thread = QtCore.QThread()
        #self.net_thread.start()
        self.netcontroller = NetController(self)
        #self.netcontroller.moveToThread(self.net_thread)
        #self.netcontroller.start.emit()

        self.net_stats_timer = QtCore.QTimer()
        self.net_stats_timer.setInterval(1000)
        self.net_stats_timer.timeout.connect(self.update_net_stats)
        self.net_stats_timer.start()

        self.netcontroller.data_received.connect(self.on_network_event)
        self.scenecontroller.new_frame.connect(self.netcontroller.frame_complete)
        self.netcontroller.data_received.connect(self.scenecontroller.process_command)

        self.view.setMaximumSize(QtCore.QSize(max(640, cw + 130), max(480, ch)))
        self.view.setMinimumSize(self.view.maximumSize())
        self.view.resize(self.view.maximumSize())

        self.view.show()
        #self.view.showFullScreen()
        #self.view.setGeometry(self.app.desktop().availableGeometry())

    @QtCore.pyqtSlot()
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

    @QtCore.pyqtSlot()
    def update_net_stats(self):
        self.canvas.net_stats = self.netcontroller.get_stats()

    @QtCore.pyqtSlot()
    def on_network_event(self):
        self.canvas.update()

    @QtCore.pyqtSlot(result=bool)
    def is_backdrop_enabled(self):
        return self.scenecontroller.scene.get("backdrop_enable", False)

    @QtCore.pyqtSlot(result=bool)
    def are_labels_enabled(self):
        return self.scenecontroller.scene.get("labels_enable", False)

    @QtCore.pyqtSlot(result=bool)
    def is_locked(self):
        return self.scenecontroller.scene.get("locked", False)

    @QtCore.pyqtSlot(result=bool)
    def is_center_shown(self):
        return self.scenecontroller.show_center

    @QtCore.pyqtSlot(result=bool)
    def is_blurred(self):
        return self.is_blurred

    @QtCore.pyqtSlot()
    def on_btn_add_fixture(self):
        self.scenecontroller.add_fixture()

    @QtCore.pyqtSlot()
    def on_btn_clear(self):
        self.scenecontroller.clear_fixtures()

    @QtCore.pyqtSlot()
    def on_btn_save(self):
        self.scenecontroller.save_scene()

    @QtCore.pyqtSlot(result=bool)
    def on_btn_backdrop_showhide(self, obj):
        enabled = self.scenecontroller.toggle_background_enable()
        if enabled:
            obj.setProperty("text", "Hide Backdrop")
        else:
            obj.setProperty("text", "Show Backdrop")
        return enabled

    @QtCore.pyqtSlot(result=bool)
    def on_btn_labels_showhide(self, obj):
        enabled = self.scenecontroller.toggle_labels_enable()
        if enabled:
            obj.setProperty("text", "Hide Labels")
        else:
            obj.setProperty("text", "Show Labels")
        return enabled

    @QtCore.pyqtSlot(result=bool)
    def on_btn_lock(self, obj):
        locked = self.scenecontroller.toggle_locked()
        if locked:
            obj.setProperty("text", "Unlock Scene")
        else:
            obj.setProperty("text", "Lock Scene")
        return locked

    @QtCore.pyqtSlot(result=bool)
    def on_btn_show_center(self, obj):
        show_center = self.scenecontroller.toggle_show_center()
        if show_center:
            obj.setProperty("text", "Hide Center")
        else:
            obj.setProperty("text", "Show Center")
        return show_center

    @QtCore.pyqtSlot(result=bool)
    def on_btn_toggle_blurred(self, obj):
        self.is_blurred = not self.is_blurred
        if self.is_blurred:
            obj.setProperty("text", "In Focus")
        else:
            obj.setProperty("text", "Blurred")
        return self.is_blurred

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

    on_selected_fixture_strand = QtCore.pyqtSignal()
    on_selected_fixture_address = QtCore.pyqtSignal()
    on_selected_fixture_pixels = QtCore.pyqtSignal()

    selected_fixture_strand = QtCore.pyqtProperty(int, _get_selected_fixture_strand, _set_selected_fixture_strand, notify=on_selected_fixture_strand)
    selected_fixture_address = QtCore.pyqtProperty(int, _get_selected_fixture_address, _set_selected_fixture_address, notify=on_selected_fixture_address)
    selected_fixture_pixels = QtCore.pyqtProperty(int, _get_selected_fixture_pixels, _set_selected_fixture_pixels, notify=on_selected_fixture_pixels)

