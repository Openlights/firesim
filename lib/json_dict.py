# This file is part of Firemix.
#
# Copyright 2013-2016 Jonathan Evans <jon@craftyjon.com>
#
# Firemix is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Firemix is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Firemix.  If not, see <http://www.gnu.org/licenses/>.

from builtins import str
from builtins import map
from past.builtins import basestring
from collections.abc import Mapping, MutableMapping, Iterable
import json
import os

from PyQt5.QtCore import QObject
from abc import ABCMeta

class JSONDictMeta(type(QObject), ABCMeta):
    pass


class JSONDict(MutableMapping, QObject, metaclass=JSONDictMeta):
    """
    Represents a dictionary backed by a JSON file.  The dictionary must contain
    at least one entry, with the key 'file-type' and the value a string passed to __init__().
    This file-type is used for subclasses as a validation step.
    """

    def __init__(self, filetype, filepath, create_new):
        QObject.__init__(self)

        self.data = dict()
        self.filetype = filetype
        self.filepath = filepath

        self._dirty = False

        if self.filepath != "":
            self.load(create_new)

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    @property
    def dirty(self):
        return self._dirty

    @dirty.setter
    def dirty(self, val):
        self._dirty = self._dirty or val

    @property
    def filepath(self):
        return self._filepath

    @filepath.setter
    def filepath(self, path):
        self._filepath = path

    def generate_new_data(self):
        """
        Generates a "new file" containing whatever defaults necessary
        (override in child classes)
        """
        self.data.clear()
        self.data['file-type'] = self.filetype

    def load(self, create_new):

        if self.filepath is None or not os.path.exists(self.filepath):
            if create_new:
                self.generate_new_data()
                if self.filepath is not None:
                    self.save()
            else:
                raise ValueError("File %s does not exist." % self.filepath)
        else:
            with open(self.filepath, 'r') as f:
                try:
                    self.data = self._unicode_to_str(json.load(f))
                    if self.data.get('file-type', None) != self.filetype:
                        raise ValueError("Error loading settings from %s: file-type mismatch." % self.filepath)
                except json.JSONDecodeError as err:
                    raise ValueError("Parse error in JSON file: %s at line %s" % (err.msg, err.lineno))

    def save(self):
        if self.filepath is None or self.filepath == "":
            return False

        with open(self.filepath, 'w') as f:
            json.dump(self.data, f, indent=4, sort_keys=True)
            self._dirty = False

    def _unicode_to_str(self, data):
        if isinstance(data, basestring):
            return str(data)
        elif isinstance(data, Mapping):
            return dict(list(map(self._unicode_to_str, iter(data.items()))))
        elif isinstance(data, Iterable):
            return type(data)(list(map(self._unicode_to_str, data)))
        else:
            return data
