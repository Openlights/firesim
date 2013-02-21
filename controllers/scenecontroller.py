import logging as log
from PySide import QtGui

from ui.canvaswidget import CanvasWidget
from ui.fixturewidget import FixtureWidget

from models.scene import Scene
from models.fixture import Fixture

class SceneController:

    def __init__(self, app=None, canvas=None, scene=None):
        self.canvas = canvas
        self.scene = scene
        self.app = app
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
        self.app.widget_selected(selected, fixture, multi)

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

    def update_all(self):
        for f in self.fixtures:
            f.widget.update()

    def toggle_background_enable(self):
        if self.scene.get("backdrop_enable", False):
            self.scene.set("backdrop_enable", False)
            self.load_backdrop()
            return False
        else:
            self.scene.set("backdrop_enable", True)
            self.load_backdrop()
            return True

    def toggle_labels_enable(self):
        enabled = not self.scene.get("labels_enable", False)
        self.scene.set("labels_enable", enabled)
        self.update_all()
        return enabled

    def toggle_locked(self):
        locked = not self.scene.get("locked", False)
        self.scene.set("locked", locked)
        self.update_all()
        return locked

    def net_set(self, strand, address, pixel, color):
        for f in self.fixtures:
            if (strand == -1 or f.strand == strand) and (address == -1 or f.address == address):
                if pixel == -1:
                    f.set_all(color)
                else:
                    f.set(pixel, color)

    def process_command(self, packet):
        assert len(packet) >= 3
        packet = [ord(c) for c in packet]
        cmd = packet[0]
        datalen = (packet[1] << 8) + packet[2]
        data = packet[3:]

        # Set All
        if cmd == 0x21:
            assert datalen == 3
            for f in self.fixtures:
                f.set_all((data[0], data[1], data[2]))
            return

        # Set Strand
        if cmd == 0x22:
            assert datalen == 4
            for f in self.fixtures:
                if f.strand == data[0]:
                    f.set_all((data[1], data[2], data[3]))
            return

        # Set Fixture
        if cmd == 0x23:
            assert datalen == 5
            for f in self.fixtures:
                if f.strand == data[0] and f.address == data[1]:
                    f.set_all((data[2], data[3], data[4]))
            return

        # Set Pixel
        if cmd == 0x24:
            assert datalen == 6
            for f in self.fixtures:
                if f.strand == data[0] and f.address == data[1]:
                    f.set(data[2], (data[3], data[4], data[5]))
            return

        # Set Strand Pixels
        if cmd == 0x25:
            raise NotImplementedError

        # Set Fixture Pixels
        if cmd == 0x26:
            raise NotImplementedError

        # Bulk Set
        if cmd == 0x27:
            raise NotImplementedError
