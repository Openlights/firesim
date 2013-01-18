from PySide import QtCore, QtGui, QtDeclarative

from fixture import Fixture

class CanvasWidget(QtDeclarative.QDeclarativeItem):
    def __init__(self, parent = None):
        super(CanvasWidget, self).__init__()
        self.setFlag(QtGui.QGraphicsItem.ItemHasNoContents, False)
        self.setFlag(QtGui.QGraphicsItem.ItemClipsChildrenToShape, True)
        self.setAcceptedMouseButtons(QtCore.Qt.MouseButton.LeftButton)
        self.setAcceptsHoverEvents(True)
        self.color = QtGui.QColor(100, 100, 100)
        self.fixture_list = []
        self.background_image = None
        self.rect = None

    def paint(self, painter, options, widget):
        self.rect = QtCore.QRect(0, 0, self.width(), self.height())
        painter.fillRect(self.rect, QtGui.QColor(0, 0, 0))
        if self.background_image is not None:
            painter.drawImage(self.rect, self.background_image)
        pen = QtGui.QPen(self.color, 2)
        painter.setPen(pen)
        painter.setRenderHints(QtGui.QPainter.Antialiasing, True)

        # TODO: support multi-dimensional fixtures
        for fixture in self.fixture_list:
            x, y, w, h = fixture.pos_rect
            painter.fillRect(x, y, w, h, self.color)
            for px, color in enumerate(fixture.pixels):
                r, g, b = color
                xp = int(x + w * (float(px) / fixture.num_pixels))
                painter.fillRect(xp, y, (w / fixture.num_pixels), h, QtGui.QColor(r, g, b))

    def update_fixtures(self, fixture_list):
        self.fixture_list = fixture_list
        self.update()

    def set_background_image(self, image):
        assert isinstance(image, QtGui.QImage), "You must pass a QtGui.QImage to set_background_image()"
        self.background_image = image

    def hoverMoveEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        pass

    def mousePressEvent(self, event):
        pass