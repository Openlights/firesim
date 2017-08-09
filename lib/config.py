import logging as log

from lib.json_dict import JSONDict

class Config(JSONDict):

    def __init__(self, filename=None):
        super(Config, self).__init__('firesim-config', filename, False)
