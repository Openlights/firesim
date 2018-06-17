import numpy as np
from copy import copy

from PyQt5.QtCore import Qt, QObject, pyqtSlot, QPointF
from PyQt5.QtGui import QGuiApplication

from models.pixelgroup import *
from models.canvas import Canvas

from lib.dtypes import rgb888_color
from lib.geometry import hit_test_rect, inflate_rect, vec2_sum


class CanvasController(QObject):

    def __init__(self, view):
        super(CanvasController, self).__init__()
        self.view = view
        self.model = Canvas()

        self.mouse_down_pos = None
        self.cursor_loc = (0, 0)

        self.selected = []
        self.selection_candidates = []
        self.selection_index = 0
        self.hovering = []
        self.dragging = False
        self.drag_canceled = False
        self.drag_delta = None
        self.child_handling_drag = None

        self.adding_type = None
        self.ghost_item = None

    @pyqtSlot(dict)
    def on_new_frame(self, frame):
        for strand, data in frame.items():
            self.model.color_data[strand] =\
                np.asarray(data).reshape((-1, 3))


# Adding pixel groups should actually be a toggle-able mode, not a single click.
# When in the mode, the mouse should ghost around a pixel group with default
# properties.  When you click, it converts that to a real new pixel group and
# stores it in the scene.  self.ghost_item can be temporary storage.  view should
# be updated to draw ghost items in a special way (translucent, glowing border?)


    @pyqtSlot(str)
    def add_new_pixel_group(self, grouptype):
        if grouptype == "linear":
            self.ghost_item = LinearPixelGroup(start=self.cursor_loc,
                                               end=(vec2_sum(self.cursor_loc,
                                                             (50, 50))))

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

        candidates = [pg for pg in self.model.scene.pixel_groups
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
        self.cursor_loc = event.pos().x(), event.pos().y()
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
        self.cursor_loc = event.localPos().x(), event.localPos().y()

        if self.model.design_mode and len(self.selected) > 0:

            delta = event.localPos() - QPointF(*self.mouse_down_pos)

            # TODO: For multiple objects selected, we should create a bounding
            #       box to encompass them all, and then only start a drag if the
            #       mouse is inside that bounding box.

            # Start a drag if the mouse has moved a little bit and we are either
            # doing a multi-select drag or the mouse started inside the selected
            # object.
            if (delta.manhattanLength() > 5 and
                (len(self.selected) > 1 or
                 self.selected[0].hit_test(
                    self.view.canvas_to_scene(self.mouse_down_pos)))):
                self.dragging = True
            elif not self.dragging:
                return

            if self.dragging:
                if self.drag_canceled:
                    return

                self.drag_delta = delta.x(), delta.y()

            if self.child_handling_drag is not None:
                delta = self.view.canvas_to_scene(self.drag_delta)
                self.child_handling_drag.on_drag_move(delta)
            elif len(self.selected) == 1:
                start_pos = self.view.canvas_to_scene(self.mouse_down_pos)
                if self.selected[0].hit_test(start_pos):
                    self.child_handling_drag = self.selected[0]
                    self.child_handling_drag.on_drag_start(start_pos)

    def on_mouse_press(self, event):
        self.mouse_down_pos = event.localPos().x(), event.localPos().y()

    def on_mouse_release(self, event):
        if self.model.design_mode:

            if self.drag_canceled:
                self.drag_canceled = False
                self.dragging = False
                self.child_handling_drag = None
                return

            if self.dragging:
                self.dragging = False

                if self.child_handling_drag:
                    delta = self.view.canvas_to_scene(self.drag_delta)
                    self.child_handling_drag.on_drag_end(delta)
                    self.child_handling_drag = None
                else:
                    for pg in self.selected:
                        pg.move_by(self.view.canvas_to_scene(self.drag_delta))
                return

            delta = (event.localPos() - QPointF(*self.mouse_down_pos))
            if delta.manhattanLength() <= 5:
                self.unhover_all()
                self.try_select_under_cursor(event.localPos())

    def on_key_press(self, event):
        pass

    def on_key_release(self, event):
        # TODO: Hotkey remapping
        mods = event.modifiers()

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
                    self.drag_canceled = True
                    if self.child_handling_drag is not None:
                        self.child_handling_drag.on_drag_cancel()
                else:
                    self.deselect_all()

        elif event.key() == Qt.Key_Up:
            if self.model.design_mode and len(self.selected) > 0:
                delta = 5 if (mods & Qt.ShiftModifier) else 1
                for pg in self.selected:
                    pg.move_by((0, -delta))

        elif event.key() == Qt.Key_Down:
            if self.model.design_mode and len(self.selected) > 0:
                delta = 5 if (mods & Qt.ShiftModifier) else 1
                for pg in self.selected:
                    pg.move_by((0, delta))

        elif event.key() == Qt.Key_Right:
            if self.model.design_mode and len(self.selected) > 0:
                delta = 5 if (mods & Qt.ShiftModifier) else 1
                for pg in self.selected:
                    pg.move_by((delta, 0))

        elif event.key() == Qt.Key_Left:
            if self.model.design_mode and len(self.selected) > 0:
                delta = 5 if (mods & Qt.ShiftModifier) else 1
                for pg in self.selected:
                    pg.move_by((-delta, 0))
