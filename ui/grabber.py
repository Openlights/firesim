from kivy.uix.widget import Widget
from kivy.uix.button import Button


class Grabber(Button):
    def __init__(self, **kwargs):
        Widget.__init__(self, **kwargs)
        self.dragging = False
        self.drag_center = (0, 0)

    def on_touch_up(self, touch):
        if self.dragging:
            self.dragging = False

    def on_touch_move(self, touch):
        if self.dragging:
            self.center_x = touch.x - self.drag_center[0]
            self.center_y = touch.y - self.drag_center[1]
        else:
            if self.collide_point(touch.x, touch.y):
                self.dragging = True
                self.drag_center = (touch.x - self.center_x, touch.y - self.center_y)