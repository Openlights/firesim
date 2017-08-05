import json
import numpy as np

from lib.dtypes import pixel_color, pixel_location
from lib.geometry import distance, distance_point_to_line, inflate_rect

__all__ = [
    "PixelGroup", "LinearPixelGroup", "RectangularPixelGroup",
    "CircularPixelGroup"
]


class PixelGroup:
    """
    A PixelGroup is a set of pixels that have some internal geometric ordering.
    For example, a linear array (LED strip), square array, or circular array.
    This class gets subclassed to define the shape-specific details.

    PixelGroups are each a single entity in the scene model (i.e. stored in the
    scene file) and a single widget to interact with in the canvas.

    Any scene can have zero or more PixelGroups, each with one or more pixels.

    PixelGroups are used for WYSIWYG editing/layout of scenes, but could also be
    used in the future as another piece of data for pattern generation.

    All locations are stored in scene coordinate space.
    LED addresses are (strand, offset) tuples.
    """

    def __init__(self, count, address=None):
        self.count = count
        self.pixel_locations = np.zeros(count, dtype=pixel_location)
        self.pixel_colors = np.zeros(count, dtype=pixel_color)
        self.address = address

        # GUI-related
        self.selected = False
        self.draw_bb = False

    def __repr__(self):
        return "PixelGroup address (%d, %d)" % (self.address[0],
                                                self.address[1])

    def bounding_box(self):
        """
        Returns a bounding box that encompasses the pixels in the group
        (x, y, width, height) where (x, y) are the upper-left coordinates.
        """
        raise NotImplementedError("Please override bounding_box()!")

    def hit_test(self, pos):
        """
        Returns True if pos is inside the graphical bounds of the group.
        The graphical bounds may be smaller (but not larger) than the bounding
        box.
        """
        raise NotImplementedError("Please override hit_test()!")


class LinearPixelGroup(PixelGroup):
    """
    Represents a linear array (strip) of evenly-spaced pixels.

    Defined by pixel count and start / end points (in scene-space units).
    The first pixel will overlap with the
    """

    def __init__(self, start, end, count, address=None):
        super(LinearPixelGroup, self).__init__(count, address)
        self.start = start
        self.end = end
        self._bounding_box = None

        ox = (end[0] - start[0]) / count
        oy = (end[1] - start[1]) / count
        px, py = start[0], start[1]
        for i in range(count):
            self.pixel_locations[i] = (px, py)
            px += ox
            py += oy

    def __repr__(self):
        return ("LinearPixelGroup address (%s) start (%s) end (%s) count %d" %
                (self.address, self.start, self.end, self.count))

    def bounding_box(self):
        if self._bounding_box is None:
            x1, y1 = self.start
            x2, y2 = self.end
            x, y = (min(x1, x2), min(y1, y2))
            self._bounding_box = (x, y, abs(x2 - x1), abs(y2 - y1))
            self._bounding_box = inflate_rect(self._bounding_box, 50)
        return self._bounding_box

    def hit_test(self, pos, epsilon=10):
        dist = distance_point_to_line(self.start, self.end, pos)
        #print(repr(self), "pos", pos, "e", epsilon, "distance", dist)
        return 0 if (dist > epsilon) else dist


class RectangularPixelGroup(PixelGroup):
    """
    Represents a rectanglar grid of evenly-spaced pixels.

    Defined by corners (start, end) and pixel count (rows, cols)
    """

    def __init__(self, start, end, rows, cols, address=None):
        super(RectangularPixelGroup, self).__init__(rows * cols, address)
        self.start = start
        self.end = end


class CircularPixelGroup(PixelGroup):
    """
    Represents a circular array of evenly-spaced pixels.

    Defined by pixel count, radius, start angle, and end angle (meaning that it
    can define either a circle or an arc).  For a circle, start and end angle
    should be the same.  For an arc, the pixels will be placed clockwise from
    the start angle to the end angle.  Spacing will be calculated based on the
    other parameters.
    """

    def __init__(self, center, count, radius,
                 start_angle, end_angle, address=None):
        super(CircularPixelGroup, self).__init__(count, address)
        self.radius = radius
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.center = center


class ArbitraryPixelGroup(PixelGroup):
    """
    Represents an arbitrary set of pixels that should be logically grouped
    together even if they don't form a regular geometric shape.

    Until there is a GUI for forming AribtraryPixelGroups out of individual
    pixels, these must be loaded in from a file.
    """

    def __init__(self, count, address=None):
        super(ArbitraryPixelGroup, self).__init__(count, address)
