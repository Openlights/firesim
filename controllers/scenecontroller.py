import logging as log
import array
import time
import numpy as np
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
        self._num_packets = 0
        self._max_fixtures = 0
        self._max_pixels = 0
        self._output_buffer = None
        self._strand_keys = list()
        if self.canvas is not None:
            self.init_view()
        self.create_pixel_array()

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
        self.update_scene()
        self.create_pixel_array()

    def delete_fixture(self, fixture):
        self.fixtures = [f for f in self.fixtures if f is not fixture]
        log.info("Destroying fixture %s" % fixture)
        fixture.destroy()
        self.update_scene()
        self.create_pixel_array()

    def clear_fixtures(self):
        while len(self.fixtures) > 0:
            fixture = self.fixtures.pop()
            fixture.destroy()
            del fixture
        self.update_scene()
        self.create_pixel_array()

    def widget_selected(self, selected, fixture, multi):
        if multi:
            pass
        else:
            for f in self.fixtures:
                if f is not fixture:
                    f.get_widget().select(False)
        self.app.widget_selected(selected, fixture, multi)

    def update_scene(self):
        fd = []
        for fixture in self.fixtures:
            fd.append(fixture.pack())
        self.scene.set_fixture_data(fd)

    def save_scene(self):
        self.update_scene()
        self.scene.save()

    def get_fixture(self, id):
        for f in self.fixtures:
            if f.id == id:
                return f

    def get_fixtures(self):
        return self.fixtures

    def update_all(self):
        for f in self.fixtures:
            f.get_widget().update()

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

    def create_pixel_array(self):
        """
        Initializes the array of colors used for displaying incoming data from the network.
        Needs to be called when the shape of the scene has changed
        (fixtures added/removed, addresses changed, pixels per fixture changed)
        """
        fh = self.scene.fixture_hierarchy()
        self._strand_keys = list()
        for strand in fh:
            self._strand_keys.append(strand)
            if len(fh[strand]) > self._max_fixtures:
                self._max_fixtures = len(fh[strand])
            for fixture in fh[strand]:
                if fh[strand][fixture].pixels() > self._max_pixels:
                    self._max_pixels = fh[strand][fixture].pixels()
        log.info("Scene has %d strands, creating array using %d fixtures by %d pixels." % (len(self._strand_keys), self._max_fixtures, self._max_pixels))
        self._output_buffer = np.zeros((len(self._strand_keys), self._max_fixtures, self._max_pixels, 3))

    def net_set(self, strand, address, color):
        #start = time.time()
        for f in self.fixtures:
            if (strand == -1 or f.strand() == strand) and (address == -1 or f.address() == address):
                if isinstance(color, tuple):
                    f.set_all(color)
                else:
                    assert isinstance(color, list)
                    f.set_array(color)
        #dt = time.time() - start
        #log.info("net_set completed in %0.2f ms" % (dt * 1000.0))

    def set_strand(self, strand, pixels, bgr=False):
        start = 0
        strand_fixtures = [f for f in self.fixtures if (f.strand() == strand or strand == -1)]
        for f in sorted(strand_fixtures, key=lambda f: f.address()):
            if (strand == -1 or f.strand() == strand):
                nd = 3 * f.pixels()
                if len(pixels) >= (start + nd):
                    f.set_flat_array(pixels[start:start + nd], bgr)
                start += nd

    def process_command(self, packet):
        if len(packet) < 3:
            log.error("Malformed packet!")
            print packet
            return

        self._num_packets += 1

        while True:
            strand = packet[0]
            cmd = packet[1]
            datalen = (packet[3] << 8) + packet[2]
            data = packet[4:]

            # Set All
            if cmd == 0x21:
                assert datalen == 3
                for f in self.fixtures:
                    f.set_all((data[0], data[1], data[2]))

            # Set Strand
            if cmd == 0x22:
                assert datalen == 4
                for f in self.fixtures:
                    if f.strand == data[0]:
                        f.set_all((data[1], data[2], data[3]))

            # Set Fixture
            if cmd == 0x23:
                assert datalen == 5
                for f in self.fixtures:
                    if f.strand == data[0] and f.address == data[1]:
                        f.set_all((data[2], data[3], data[4]))

            # Set Pixel
            if cmd == 0x24:
                assert datalen == 6
                for f in self.fixtures:
                    if f.strand == data[0] and f.address == data[1]:
                        f.set(data[2], (data[3], data[4], data[5]))

            # Set Strand Pixels
            if cmd == 0x25:
                raise NotImplementedError

            # Set Fixture Pixels
            if cmd == 0x26:
                raise NotImplementedError

            # Bulk Strand Set
            # TODO: This will break if the addressing is not continuous.
            # TODO: Need to validate addressing in the GUI.  See #10
            if cmd == 0x10 or cmd == 0x20:
                self.set_strand(strand, data)


            if len(packet) > (4 + datalen):
                packet = packet[4 + datalen:]
                #print len(packet)
            else:
                break
