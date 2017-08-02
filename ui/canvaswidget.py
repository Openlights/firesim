from __future__ import division
from past.utils import old_div
import colorsys
import random

from PyQt5 import QtCore
from PyQt5.QtGui import QColor, QFont, QImage
from PyQt5.QtQuick import QQuickItem, QQuickPaintedItem
from PyQt5.QtWidgets import QWidget


class CanvasWidget(QQuickPaintedItem):
    def __init__(self, parent = None):
        super(CanvasWidget, self).__init__()
        self.setFlag(QQuickItem.ItemClipsChildrenToShape, True)
        self.setAcceptedMouseButtons(QtCore.Qt.LeftButton | QtCore.Qt.RightButton)
        self.setAcceptHoverEvents(False)
        #self.setRenderTarget(QQuickPaintedItem.FramebufferObject)
        self.setMipmap(True)
        #self.setAntialiasing(True)
        self.setFillColor(QColor(0, 0, 0))

        self.color = QColor(100, 100, 100)
        self.fixture_list = []
        self.background_image = None
        self.net_stats = {'pps': 0, 'ups': 0}
        self.controller = None
        self.next_new_fixture_pos = (25, 25)
        self.markup_color = (255, 255, 0)
        self.coordinate_scale = 1.0
        self.x_offset = 0
        self.y_offset = 0
        self.gui = None

    def contains(self, point):
        if point.x() < 0 or point.y() < 0:
            return False
        if point.x() > self.width() or point.y() > self.height():
            return False
        return True

    def paint(self, painter):
        if self.background_image is not None:
            rect = QtCore.QRect(0, 0, self.width(), self.height())
            img = self.background_image.scaled(rect.size(), QtCore.Qt.KeepAspectRatio)
            # FIXME
            #if img.rect().width() != self.background_image.rect().width():
            #    self.coordinate_scale = float(img.rect().width()) / self.background_image.rect().width()
            if img.rect().width() <= rect.width():
                self.x_offset = old_div((rect.width() - img.rect().width()), 2)
                painter.drawImage(self.x_offset, 0, img)
            elif img.rect().height() <= rect.height():
                self.y_offset = old_div((rect.height() - img.rect().height()), 2)
                painter.drawImage(0, self.y_offset, img)

        f = QFont()
        f.setPointSize(8)
        painter.setFont(f)
        painter.setPen(QColor(170, 170, 200, 255))
        painter.drawText(8, 16, "%0.1f packets/sec" % self.net_stats['pps'])
        painter.drawText(8, 32, "%0.1f frames/sec" % self.net_stats['ups'])

        #for i, time in enumerate(self.controller.times):
        #    painter.drawLine(10 + i, 100, 10 + i, (100 - int(time * 3000.0)))

    def update_fixtures(self, fixture_list):
        self.fixture_list = fixture_list
        for fixture in fixture_list:
            fixture.update()
        self.update()

    def set_background_image(self, image):
        if image is not None:
            assert isinstance(image, QImage), "You must pass a QImage to set_background_image()"
            # self.w = image.width()
            # self.h = image.height()
            # self.setWidth(self.w/2)
            # self.setHeight(self.h/2)
        self.background_image = image

    def get_next_new_fixture_pos_and_increment(self):
        x, y = self.next_new_fixture_pos
        self.next_new_fixture_pos = (x + 5, y + 5)
        return (x, y)

    def hoverMoveEvent(self, event):
        for fixture in self.fixture_list:
            if fixture.shape().contains(event.pos()):
                fixture.hover_enter()
            else:
                fixture.hover_leave()

    def mouseMoveEvent(self, event):
        pass

    def mousePressEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.deselect_all()
        elif event.button() == QtCore.Qt.RightButton:
            self.generate_markup_color()

    def deselect_all(self):
        self.controller.widget_selected(False, None, False)

    def generate_markup_color(self):
        r, g, b = [int(255.0 * c) for c in colorsys.hsv_to_rgb(random.random(), 1.0, 1.0)]
        self.markup_color = (r, g, b)

    def on_fixture_click(self, fixture):
        pass

    def scene_to_canvas(self, a, b=None):
        """
        Scales coordinates to the GUI
        """
        if b is None:
            a, b = a
        # FIXME: Coordinate scaling doesn't work
        #return (self.coordinate_scale * (a + self.x_offset), self.coordinate_scale * (b + self.y_offset))
        return (int(a + self.x_offset), int(b + self.y_offset))

    def canvas_to_scene(self, a, b=None):
        if b is None:
            a, b = a
        return (int(a - self.x_offset), int(b - self.y_offset))

