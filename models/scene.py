import logging as log

from util.jsonloader import JSONLoader
from models.fixture import Fixture

class Scene(JSONLoader):

    def __init__(self, filename=None):
        JSONLoader.__init__(self, filename)
        fd = self.data.get("fixtures", [])
        self.fixtures = []
        if len(fd) > 0:
            for f in fd:
                self.fixtures.append(Fixture(f))
