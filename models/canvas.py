from PyQt5.QtCore import pyqtProperty, pyqtSignal, QObject


class Canvas(QObject):

    changed = pyqtSignal()

    def __init__(self):
        super(Canvas, self).__init__()

        self.scene = None
        self.color_data = {}

        # The canvas is always in either design mode or sim mode.
        # In design mode, pixel colors are not drawn, and object manipulation
        # is allowed.  In sim mode, only pixel colors are drawn.
        self._design_mode = False

        self._blurred = False

    @pyqtProperty(bool, notify=changed)
    def design_mode(self):
        return self._design_mode

    @design_mode.setter
    def design_mode(self, val):
        if self._design_mode != val:
            self._design_mode = val
            self.changed.emit()

    @pyqtProperty(bool, notify=changed)
    def blurred(self):
        return self._blurred

    @blurred.setter
    def blurred(self, val):
        if self._blurred != val:
            self._blurred = val
            self.changed.emit()

    @pyqtProperty(bool, notify=changed)
    def backdrop_enable(self):
        return self.scene.backdrop_enable if self.scene else False

    @backdrop_enable.setter
    def backdrop_enable(self, s):
        self.scene.backdrop_enable = s
