import json
import logging as log


class JSONLoader:

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
                    log.error("Error loading " + self.filename)
                    self.data = None
                    return

            log.info("Loaded " + self.filename)
            self.file_loaded = True

    def save(self):
        if self.filename is not None:
            with open(self.filename, 'w') as f:
                try:
                    json.dump(self.data, f, indent=2, sort_keys=True)
                except:
                    log.error("Error saving " + self.filename)
                    return

            log.info("Saved " + self.filename)

    def get(self, key, default=None):
        if self.data is None:
            log.warn("No file was loaded!")
        val = self.data.get(key, default)
        return val
