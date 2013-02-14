

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
        self.id = int(data.get("id", "0"))
        self.strand = int(data.get("strand", "0"))
        self.address = int(data.get("address", "0"))
        self.type = data.get("type", "")
        self.pixels = int(data.get("pixels", "0"))
        self.pos1 = map(int, data.get("pos1", "0,0").split(','))
        self.pos2 = map(int, data.get("pos2", "0,0").split(','))
        self.scale = float(data.get("scale", "0.0"))
        self.angle = float(data.get("angle", "0.0"))