from builtins import object
import json
import logging as log


class JSONLoader(object):

    def __init__(self, filename=None):
        self._filename = filename
        self._loaded = False
        self._data = None
        self.load()

    def load(self):
        self._loaded = False
        if self._filename is not None:
            try:
                with open(self._filename) as f:
                    try:
                        self._data = json.load(f)
                    except:
                        log.error("Error loading " + self._filename)
                        self._data = None
                        return
            except IOError:
                self._data = {}
                with open(self._filename, 'w') as f:
                    json.dump({}, f)

            log.info("Loaded " + self._filename)
            self._loaded = True

    def save(self):
        if self._filename is not None:
            with open(self._filename, 'w') as f:
                try:
                    json.dump(self._data, f, indent=2, sort_keys=True)
                except:
                    log.error("Error saving " + self._filename)
                    return

            log.info("Saved " + self._filename)

    def get(self, key, default=None):
        if self._data is None:
            log.warn("No file was loaded!")
        val = self._data.get(key, default)
        return val

    def set(self, key, value):
        self._data[key] = value
