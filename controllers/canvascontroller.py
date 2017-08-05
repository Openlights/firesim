import numpy as np

from PyQt5.QtCore import QObject, pyqtSlot

from models.pixelgroup import *
from models.canvas import Canvas

from lib.dtypes import rgb888_color
from lib.geometry import hit_test_rect, inflate_rect


class CanvasController(QObject):

    def __init__(self, view):
        super(CanvasController, self).__init__()
        self.view = view
        self.model = Canvas()

        self.selected = []
        self.selection_candidates = []
        self.hovering = []

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
        self.selection_candidates = self.get_objects_under_cursor(pos)
        if len(self.selection_candidates) == 0:
            self.deselect_all()
            return

        if len(self.selection_candidates) > 0:
            for pg in self.selected:
                if pg is not self.selection_candidates[0]:
                    self.select(pg, False)
            self.select(self.selection_candidates[0], True)

    def get_objects_under_cursor(self, pos):
        """
        Returns a list of all objects somewhat close to the cursor
        Pos is in canvas space.
        """
        pos = self.view.canvas_to_scene((pos.x(), pos.y()))

        candidates = [pg for pg in self.model.pixel_groups
                      if hit_test_rect(pg.bounding_box(), pos)]

        if len(candidates) == 0:
            return []

        e = self.view.canvas_to_scene((20, 20))[0]

        tested = [(c, c.hit_test(pos, e)) for c in candidates]
        tested = [c for c, d in sorted(tested, key=lambda x: x[1]) if d > 0]

        return tested


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
        self.selection_candidates.clear()

    def on_hover_move(self, event):
        under_cursor = self.get_objects_under_cursor(event.pos())
        for pg in self.hovering:
            if pg not in under_cursor:
                pg.hovering = False
                self.hovering.remove(pg)
            else:
                under_cursor.remove(pg)
        for pg in under_cursor:
            pg.hovering = True
            self.hovering.append(pg)

    def unhover_all(self):
        for pg in self.hovering:
            pg.hovering = False
        self.hovering.clear()

    def on_mouse_move(self, event):
        pass

    def on_mouse_press(self, event):
        pass

    def on_mouse_release(self, event):
        self.unhover_all()
        self.try_select_under_cursor(event.localPos())

    def import_legacy_scene(self, scene):
        self.model.size = scene.extents()
        self.model.center = scene.center()
        for fixture in scene.fixtures():
            self.model.pixel_groups.append(LinearPixelGroup(
                fixture.pos1(), fixture.pos2(), fixture.pixels(),
                (fixture.strand(), fixture._data_offset)
            ))
