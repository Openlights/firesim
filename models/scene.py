import logging as log

from util.jsonloader import JSONLoader
from models.fixture import Fixture

class Scene(JSONLoader):

    def __init__(self, filename=None):
        JSONLoader.__init__(self, filename)
