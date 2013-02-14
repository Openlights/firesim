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
        self.fixture_widget_list = []
        self.init_view()

    def init_view(self):
        if self.scene.get("backdrop_enable", False):
            log.info("Loading backdrop from " + self.scene.get("backdrop_filename"))
            self.canvas.set_background_image(QtGui.QImage(self.scene.get("backdrop_filename")))

        self.fixture_list = []
        if len(self.scene.fixtures) > 0:
            for fixture in self.scene.fixtures:
                fw = FixtureWidget(self.canvas, fixture.id)
                x, y = fixture.pos1
                fw.setPos(x, y)
                fw.setRotation(fixture.angle)
                self.fixture_widget_list.append(fw)

    def get_fixture_list(self):
        return self.fixture_widget_list

    def add_fixture(self):
        self.fixture_widget_list.append(FixtureWidget(self.canvas))

    def clear_fixtures(self):
        while len(self.fixture_widget_list) > 0:
            fixture = self.fixture_widget_list.pop()
            fixture.deleteLater()