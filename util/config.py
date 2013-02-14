import json
import logging as log


class Config:

    def __init__(self, filename=None):
        self.filename = filename
        self.loaded = False
        self.data = None
        self.load()

    def load(self):
        self.file_loaded = False
        if self.filename is not None:
            with open(self.filename) as f:
                try:
                    self.data = json.load(f)
                except:
                    log.error("Error loading config from " + self.filename)
                    self.data = None
                    return

            log.info("Loaded config from " + self.filename)
            self.file_loaded = True

    def get(self, key, default=None):
        return self.data.get(key, default)