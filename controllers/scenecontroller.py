import logging as log
from PySide import QtGui

from ui.canvaswidget import CanvasWidget
from ui.fixturewidget import FixtureWidget

from models.scene import Scene
from models.fixture import Fixture

class SceneController:

    def __init__(self, canvas=None, scene=None):
        self.canvas = canvas
        self.scene = scene
        self.fixtures = []
        self.init_view()

    def init_view(self):
        if self.scene.get("backdrop_enable", False):
            log.info("Loading backdrop from " + self.scene.get("backdrop_filename"))
            self.canvas.set_background_image(QtGui.QImage(self.scene.get("backdrop_filename")))

        self.fixtures = []
        fixture_data = self.scene.get("fixtures", [])
        for fixture_data_item in fixture_data:
            self.fixtures.append(Fixture(fixture_data_item, controller=self))
        self.update_canvas()

    def get_canvas(self):
        return self.canvas

    def update_canvas(self):
        fl = [f.get_widget() for f in self.fixtures]
        self.canvas.update_fixtures(fl)

    def add_fixture(self):
        self.fixtures.append(Fixture( controller=self))
        self.update_canvas()

    def clear_fixtures(self):
        while len(self.fixtures) > 0:
            fixture = self.fixtures.pop()
            fixture.destroy()
            del fixture

    def save_scene(self):
        fd = []
        for fixture in self.fixtures:
            fd.append(fixture.pack())
        self.scene.data["fixtures"] = fd
        self.scene.save()

    def get_fixture(self, id):
        for f in self.fixtures:
            if f.id == id:
                return f

    def fixture_move_callback(self, id, pos):
        f = self.get_fixture(id)
        f.pos1 = map(int, pos.toTuple())
