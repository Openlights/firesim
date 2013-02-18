import colorsys
import random

from PySide import QtCore, QtGui, QtDeclarative


class CanvasWidget(QtDeclarative.QDeclarativeItem):
    def __init__(self, parent = None):
        super(CanvasWidget, self).__init__()
        self.setFlag(QtGui.QGraphicsItem.ItemHasNoContents, False)
        self.setFlag(QtGui.QGraphicsItem.ItemClipsChildrenToShape, True)
        self.setAcceptedMouseButtons(QtCore.Qt.MouseButton.LeftButton | QtCore.Qt.MouseButton.RightButton)
        self.setAcceptsHoverEvents(True)
        self.color = QtGui.QColor(100, 100, 100)
        self.fixture_list = []
        self.background_image = None
        self.rect = None
        self.controller = None
        self.next_new_fixture_pos = (10, 10)
        self.markup_color = (255, 255, 0)

    def paint(self, painter, options, widget):
        self.rect = QtCore.QRect(0, 0, self.width(), self.height())
        painter.fillRect(self.rect, QtGui.QColor(0, 0, 0))

        if self.background_image is not None:
            painter.drawImage(self.rect, self.background_image)

    def update_fixtures(self, fixture_list):
        self.fixture_list = fixture_list
        self.update()

    def set_background_image(self, image):
        if image is not None:
            assert isinstance(image, QtGui.QImage), "You must pass a QtGui.QImage to set_background_image()"
        self.background_image = image

    def get_next_new_fixture_pos_and_increment(self):
        x, y = self.next_new_fixture_pos
        self.next_new_fixture_pos = (x + 10, y + 10)
        return (x, y)

    def hoverMoveEvent(self, event):
        pass
        #self.propagate_hover_move(None, event)

    def mouseMoveEvent(self, event):
        pass

    def mousePressEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.controller.widget_selected(False, None, False)
        elif event.button() == QtCore.Qt.MouseButton.RightButton:
            self.generate_markup_color()

    def generate_markup_color(self):
        r, g, b = [int(255.0 * c) for c in colorsys.hsv_to_rgb(random.random(), 1.0, 1.0)]
        self.markup_color = (r, g, b)

    def on_fixture_click(self, fixture):
        pass

    @QtCore.Slot()
    def propagate_hover_move(self, widget, scenepos):
        self.hover_move_event.emit(widget, scenepos)

    hover_move_event = QtCore.Signal(QtGui.QWidget, QtCore.QEvent)