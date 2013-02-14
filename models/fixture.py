from ui.fixturewidget import FixtureWidget


class Fixture:

    def __init__(self, data=None, controller=None):
        self.id = 0
        self.strand = 0
        self.address = 0
        self.type = ""
        self.pixels = 0
        self.pos1 = (0, 0)
        self.pos2 = (0, 0)
        self.scale = 0.0
        self.angle = 0.0

        if data is not None:
            self.unpack(data)

        self.widget = None
        self.controller = controller

        self.pixel_data = [(0, 0, 0)] * self.pixels

    def __repr__(self):
        return "Fixture %d [%d:%d]" % (self.id, self.strand, self.address)

    def destroy(self):
        self.widget.deleteLater()

    def get_widget(self):
        if self.widget is None:
            self.widget = FixtureWidget(self.controller.get_canvas(), self.id, model=self, move_callback=self.fixture_move_callback)
            x, y = self.pos1[0], self.pos1[1]
            self.widget.setPos(x, y)
            self.widget.setRotation(self.angle)
        return self.widget

    def unpack(self, data):
        self.id = data.get("id", 0)
        self.strand = data.get("strand", 0)
        self.address = data.get("address", 0)
        self.type = data.get("type", "")
        self.pixels = data.get("pixels", 0)
        self.pos1 = data.get("pos1", [0, 0])
        self.pos2 = data.get("pos2", [0, 0])
        self.scale = float(data.get("scale", "0.0"))
        self.angle = float(data.get("angle", "0.0"))

    def pack(self):
        return {'id': self.id,
                'strand': self.strand,
                'address': self.address,
                'type': self.type,
                'pixels': self.pixels,
                'pos1': self.pos1,
                'pos2': self.pos2,
                'scale': self.scale,
                'angle': self.angle
        }

    def fixture_move_callback(self, pos):
        self.pos1 = map(int, pos.toTuple())

    def blackout(self):
        self.pixels = [(0, 0, 0)] * self.size

    def set(self, pixel, color):
        assert isinstance(color, tuple), "Color must be a 3-tuple (R, G, B)"
        self.pixels[pixel] = color

    def set_all(self, color):
        assert isinstance(color, tuple), "Color must be a 3-tuple (R, G, B)"
        self.pixels = [color] * self.size