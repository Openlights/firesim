import logging as log
from PySide import QtGui

from ui.canvaswidget import CanvasWidget
from ui.fixturewidget import FixtureWidget

from models.scene import Scene
from models.fixture import Fixture

class SceneController:

    def __init__(self, parent=None, canvas=None, scene=None):
        self.canvas = canvas
        self.scene = scene
        self.parent = parent
        self.fixtures = []
        if self.canvas is not None:
            self.init_view()

    def init_view(self):
        self.load_backdrop()
        self.fixtures = []
        fixture_data = self.scene.get("fixtures", [])
        for fixture_data_item in fixture_data:
            self.fixtures.append(Fixture(fixture_data_item, controller=self))
        self.update_canvas()

    def load_backdrop(self):
        if self.canvas is not None:
            if self.scene.get("backdrop_enable", False):
                log.info("Loading backdrop from " + self.scene.get("backdrop_filename"))
                self.canvas.set_background_image(QtGui.QImage(self.scene.get("backdrop_filename")))
            else:
                self.canvas.set_background_image(None)
            self.canvas.update()

    def set_canvas(self, canvas):
        self.canvas = canvas
        canvas.controller = self
        self.init_view()

    def get_canvas(self):
        return self.canvas

    def update_canvas(self):
        if self.canvas is not None:
            fl = [f.get_widget() for f in self.fixtures]
            self.canvas.update_fixtures(fl)

    def add_fixture(self):
        self.fixtures.append(Fixture(controller=self))
        self.update_canvas()

    def delete_fixture(self, fixture):
        self.fixtures = [f for f in self.fixtures if f is not fixture]
        log.info("Destroying fixture %s" % fixture)
        fixture.destroy()

    def clear_fixtures(self):
        while len(self.fixtures) > 0:
            fixture = self.fixtures.pop()
            fixture.destroy()
            del fixture

    def widget_selected(self, selected, fixture, multi):
        if multi:
            pass
        else:
            for f in self.fixtures:
                if f is not fixture:
                    f.widget.select(False)
        self.parent.widget_selected(selected, fixture, multi)

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

    def get_fixtures(self):
        return self.fixtures

    def toggle_background_enable(self):
        if self.scene.get("backdrop_enable", False):
            self.scene.set("backdrop_enable", False)
            self.load_backdrop()
            return False
        else:
            self.scene.set("backdrop_enable", True)
            self.load_backdrop()
            return True
