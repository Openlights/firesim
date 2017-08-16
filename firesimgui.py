import logging as log
import os.path

# This is a workaround for a Linux + NVIDIA + PyQt5 bug causing no graphics to be rendered
# because PyQt5 is linking to the wrong libGL.so / NVIDIA isn't overriding the MESA one.
# See: https://bugs.launchpad.net/ubuntu/+source/python-qt4/+bug/941826
from OpenGL import GL

from PyQt5.QtCore import (pyqtProperty, pyqtSignal, pyqtSlot, QObject, QUrl,
                          QTimer, QSize)
from PyQt5.QtQml import qmlRegisterType, QQmlComponent
from PyQt5.QtQuick import QQuickView
from PyQt5.QtWidgets import QApplication, QFileDialog
from PyQt5.QtGui import QIcon

from ui.canvasview import CanvasView

from lib.config import Config
from models.scene import Scene
from controllers.netcontroller import NetController


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

        self.selected_fixture = None
        self.is_blurred = False

        scene_file_path = (self.args.scene if self.args.scene is not None
                           else self.config.get("last-opened-scene"))

        self.scene = Scene(scene_file_path)

        qmlRegisterType(CanvasView, "FireSim", 1, 0, "Canvas")

        self.view = QQuickView()

        self.view.setResizeMode(QQuickView.SizeRootObjectToView)

        self.view.closeEvent = self.on_close

        self.context = self.view.rootContext()
        self.context.setContextProperty('main', self)
        self.context.setContextProperty('view', self.view)

        self.view.setSource(QUrl('ui/qml/FireSimGUI.qml'))

        self.root = self.view.rootObject()
        self.canvas = self.root.findChild(CanvasView)
        self.canvas.gui = self
        self.canvas.model.scene = self.scene

        self.set_properties_from_scene()

        #self.net_thread = QThread()
        #self.net_thread.start()
        self.netcontroller = NetController(self)
        #self.netcontroller.moveToThread(self.net_thread)
        #self.netcontroller.start.emit()

        self.redraw_timer = QTimer()
        self.redraw_timer.setInterval(33)
        self.redraw_timer.timeout.connect(self.canvas.update)
        self.redraw_timer.start()

        self.netcontroller.new_frame.connect(self.canvas.controller.on_new_frame)

        self.view.setMinimumSize(QSize(550, 550))
        self.view.resize(QSize(700, 550))

        self.view.show()
        #self.view.showFullScreen()
        #self.view.setGeometry(self.app.desktop().availableGeometry())

    def set_properties_from_scene(self):
        self.view.setTitle("FireSim - %s" % self.scene.name)

        cw, ch = self.scene.extents
        self.canvas.setWidth(cw)
        self.canvas.setHeight(ch)

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
    def on_network_event(self):
        self.canvas.update()

    @pyqtSlot()
    def on_btn_open(self):
        file_name = QFileDialog.getOpenFileName(self.app.focusWidget(),
                                                "Open Scene", "",
                                                "Scene Files (*.json)")
        if len(file_name[0]) > 0:
            self.scene.save()
            self.redraw_timer.stop()
            self.scene.set_filepath_and_load(file_name[0])
            self.config['last-opened-scene'] = file_name[0]
            self.config.save()
            self.set_properties_from_scene()
            self.redraw_timer.start()

    @pyqtSlot()
    def on_btn_save(self):
        self.scene.save()

    @pyqtSlot()
    def on_btn_open_backdrop(self):
        file_types = "Image Files (*.png *.jpg *.bmp *.jpeg *.xpm *.xbm *.ppm)"
        file_name = QFileDialog.getOpenFileName(self.app.focusWidget(),
                                                "Open Scene", "",
                                                file_types)

        if len(file_name[0]) > 0:
            self.scene.backdrop_filepath = file_name[0]
