

class Fixture:

    def __init__(self, data=None):
        self.id = 0
        self.strand = 0
        self.address = 0
        self.type = ""
        self.pixels = 0
        self.pos1 = (0, 0)
        self.pos2 = (0, 0)
        self.scale = 0.0
        self.angle = 0.0

        if data:
            self.unpack(data)

    def __repr__(self):
        return "Fixture %d [%d:%d]" % (self.id, self.strand, self.address)

    def unpack(self, data):
        self.id = data.get("id", 0)
        self.strand = data.get("strand", 0)
        self.address = data.get("address", 0)
        self.type = data.get("type", "")
        self.pixels = data.get("pixels", 0)
        self.pos1 = data.get("pos1", (0, 0))
        self.pos2 = data.get("pos2", (0, 0))
        self.scale = data.get("scale", 0.0)
        self.angle = data.get("angle", 0.0)