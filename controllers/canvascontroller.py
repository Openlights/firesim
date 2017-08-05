import numpy as np

from PyQt5.QtCore import QObject, pyqtSlot

from models.pixelgroup import PixelGroup
from models.canvas import Canvas

from lib.dtypes import rgb888_color
from lib.geometry import hit_test_rect


class CanvasController(QObject):

    def __init__(self, view):
        super(CanvasController, self).__init__()
        self.view = view
        self.model = Canvas()

        self.selected = []
        self.candidates_for_selection = []

    @pyqtSlot(dict)
    def on_new_frame(self, frame):
        for strand, data in frame.items():
            self.model.color_data[strand] =\
                np.asarray(data).reshape((-1, 3))

    def try_select_under_cursor(self, pos):
        """
        Right now this is done in a naive way.  There are more advanced
        algorithms that could be put in place if performance is an issue.
        """
        pos = self.view.canvas_to_scene((pos.x(), pos.y()))

        candidates = [pg for pg in self.model.pixel_groups
                      if hit_test_rect(pg.bounding_box(), pos)]

        if len(candidates) == 0 and len(self.selected) > 0:
            self.deselect_all()

        self.candidates_for_selection = candidates
        for c in candidates:
            self.select(c, c.hit_test(pos))

    def select(self, pixel_group, select):
        if select:
            pixel_group.selected = True
            if pixel_group not in self.selected:
                self.selected.append(pixel_group)
        else:
            pixel_group.selected = False
            if pixel_group in self.selected:
                self.selected.remove(pixel_group)

    def deselect_all(self):
        for pg in self.selected:
            pg.selected = False
        self.selected.clear()

    def on_hover_move(self, event):
        pass

    def on_mouse_move(self, event):
        pass

    def on_mouse_press(self, event):
        pass

    def on_mouse_release(self, event):
        self.try_select_under_cursor(event.localPos())
