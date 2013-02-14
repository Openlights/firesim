import logging as log

from util.jsonloader import JSONLoader

class Scene(JSONLoader):

    def __init__(self, filename=None):
        JSONLoader.__init__(self, filename)
