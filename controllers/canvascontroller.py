import numpy as np
from copy import copy

from PyQt5.QtCore import Qt, QObject, pyqtSlot
from PyQt5.QtGui import QGuiApplication

from models.pixelgroup import *
from models.canvas import Canvas

from lib.dtypes import rgb888_color
from lib.geometry import hit_test_rect, inflate_rect


class CanvasController(QObject):

    def __init__(self, view):
        super(CanvasController, self).__init__()
        self.view = view
        self.model = Canvas()

        self.mouse_down_pos = None

        self.selected = []
        self.selection_candidates = []
        self.selection_index = 0
        self.hovering = []
        self.dragging = False
        self.drag_delta = None

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
        mods = QGuiApplication.keyboardModifiers()
        add_selection = (mods == Qt.ControlModifier)
        remove_selection = (mods == (Qt.ControlModifier | Qt.ShiftModifier))

        self.selection_candidates = self.get_objects_under_cursor(pos)

        if len(self.selection_candidates) == 0:
            if not add_selection and not remove_selection:
                self.deselect_all()
            return

        if not add_selection and not remove_selection:
            for pg in self.selected.copy():
                if pg is not self.selection_candidates[0]:
                    self.select(pg, False)
        self.select(self.selection_candidates[0], not remove_selection)

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

        e = self.view.canvas_to_scene((10,10))[0]

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
        self.view.selection_changed.emit()

    def deselect_all(self):
        for pg in self.selected:
            pg.selected = False
        self.selected.clear()
        self.selection_candidates.clear()
        self.view.selection_changed.emit()

    def on_hover_move(self, event):
        self.view.cursor_loc = event.pos()
        if len(self.selected) > 0:
            return

        under_cursor = self.get_objects_under_cursor(event.pos())
        for pg in self.hovering.copy():
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
        self.view.cursor_loc = event.localPos()

        if self.model.design_mode and len(self.selected) > 0:

            delta = event.localPos() - self.mouse_down_pos

            # TODO: Detect if we are starting a drag over a drag handle,
            # and behave differently.

            if delta.manhattanLength() > 5:
                self.dragging = True

            if self.dragging:
                self.drag_delta = delta

    def on_mouse_press(self, event):
        self.mouse_down_pos = event.localPos()

    def on_mouse_release(self, event):
        if self.model.design_mode:

            if self.dragging:
                self.dragging = False
                # Handle drag end

            if (event.localPos() - self.mouse_down_pos).manhattanLength() <= 5:
                self.unhover_all()
                self.try_select_under_cursor(event.localPos())

    def on_key_press(self, event):
        pass

    def on_key_release(self, event):
        # TODO: Hotkey remapping

        # Tab: selection disambiguation
        if event.key() == Qt.Key_Tab:
            if self.model.design_mode and len(self.selection_candidates) > 1:
                self.select(self.selection_candidates[self.selection_index], False)
                self.selection_index = \
                    (self.selection_index + 1) % len(self.selection_candidates)
                self.select(self.selection_candidates[self.selection_index], True)

        elif event.key() == Qt.Key_Escape:
            if self.model.design_mode:
                if self.dragging:
                    # Cancel drag
                    self.dragging = False
                else:
                    self.deselect_all()

    def import_legacy_scene(self, scene):
        self.model.size = scene.extents()
        self.model.center = scene.center()
        for fixture in scene.fixtures():
            self.model.pixel_groups.append(LinearPixelGroup(
                fixture.pos1(), fixture.pos2(), fixture.pixels(),
                (fixture.strand(), fixture._data_offset)
            ))
