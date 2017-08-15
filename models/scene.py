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

from builtins import range
import os
import math
import logging
import numpy as np
from scipy import spatial

from lib.json_dict import JSONDict
from lib.buffer_utils import BufferUtils
from models.pixelgroup import LinearPixelGroup

log = logging.getLogger("firemix.lib.scene")

class Scene(JSONDict):
    """
    The scene file holds all the data related to pixel positioning and other
    relevant information for designing the scene.

    This class is for managing that file as well as utility methods for getting
    information about pixel groups and their spatial relationships.

    Example minimal scene file:

    {
        "file-type": "scene",
        "file-version": 2,
        "scene-name": "Universe Light Lounge",
        "bounding-box": [800, 800],
        "extents": [800, 800],
        "center": [400, 400],
        "strands": [
            {
                "id": 0,
                "enabled": true,
                "color-mode": "BGR8",
                "length": 240
            }
        ],
        "pixel-groups": [
            {
                "type": "linear",
                "strand": 0,
                "offset": 120,
                "count": 120,
                "start": [100, 100],
                "end": [200, 200]
            }
        ]
    }

    """

    def __init__(self, filepath=None):
        self._reset()
        super(Scene, self).__init__('scene', filepath, False)

    def _reset(self):
        self._fixtures = None
        self._fixture_dict = {}
        self._fixture_hierarchy = None
        self._colliding_fixtures_cache = {}
        self._pixel_neighbors_cache = {}
        self._pixel_locations_cache = {}
        self._pixel_distance_cache = {}
        self._intersection_points = None
        self._all_pixels = None
        self._all_pixel_locations = None
        self._all_pixels_raw = None
        self._strand_settings = None
        self._tree = None
        self._pixel_groups = []

    def set_filepath_and_load(self, path):
        self.filepath = path
        self.load(False)

    def load(self, create_new):
        super(Scene, self).load(create_new)

        if self.get('file-version', 1) < 2:
            self._migrate_v1_to_v2()

        self._reset()
        self._load_pixel_groups()

    def save(self):
        if len(self.pixel_groups) > 0:
            self.data["pixel-groups"] = [pg.to_json() for pg in self.pixel_groups]
        super(Scene, self).save()

    def warmup(self):
        """
        Warms up caches
        """
        log.info("Warming up scene caches...")
        fh = self.fixture_hierarchy()
        for strand in fh:
            for fixture in fh[strand]:
                self.get_colliding_fixtures(strand, fixture)
                for pixel in range(self.fixture(strand, fixture).pixels):
                    index = BufferUtils.logical_to_index((strand, fixture, pixel))
                    neighbors = self.get_pixel_neighbors(index)
                    self.get_pixel_location(index)
                    for neighbor in neighbors:
                        self.get_pixel_distance(index, neighbor)
        self.get_fixture_bounding_box()
        self.get_intersection_points()
        self.get_all_pixels_logical()
        self._tree = spatial.KDTree(self.get_all_pixel_locations())

        locations = self.get_all_pixel_locations()
        self.pixelDistances = np.empty([len(locations), len(locations)])

        for pixel in range(len(locations)):
            cx, cy = locations[pixel]
            x,y = (locations - (cx, cy)).T
            pixel_distances = np.sqrt(np.square(x) + np.square(y))
            self.pixelDistances[pixel] = pixel_distances

        log.info("Done")

    @property
    def extents(self):
        """
        Returns the (x, y) extents of the scene.  Useful for determining
        relative position of fixtures to some reference point.
        """
        return tuple(self.data.get("extents", (0, 0)))

    @extents.setter
    def extents(self, val):
        assert type(val) == tuple and len(val) == 2
        self["extents"] = val
        self.dirty = True

    @property
    def center(self):
        """
        Returns the (x, y) centroid of all fixtures in the scene
        """
        center = self.data.get("center", None)
        if center is None:
            bb = self.get_fixture_bounding_box()
            center = ((bb[0] + bb[2]) / 2.0), ((bb[1] + bb[3]) / 2.0)
            self.data["center"] = center
        else:
            center = tuple(center)
        return center

    @center.setter
    def center(self, val):
        self.data["center"] = val
        self.dirty = True

    @property
    def name(self):
        return self.data.get("scene-name", "")

    @name.setter
    def name(self, name):
        self.data["scene-name"] = name
        self.dirty = True

    @property
    def strands(self):
        return self.data.get("strands")

    @strands.setter
    def strands(self, strands):
        self.data["strands"] = strands
        self.dirty = True

    @property
    def pixel_groups(self):
        return self._pixel_groups

    @pixel_groups.setter
    def pixel_groups(self, pixel_groups):
        self._pixel_groups = pixel_groups
        self.dirty = True

    def get_matrix_extents(self):
        """
        Returns a tuple of (strands, pixels) indicating the maximum extents needed
        to store the pixels in memory (note that we now assume that each strand
        is the same length).
        """
        fh = self.fixture_hierarchy()
        strands = len(fh)
        longest_strand = 0
        for strand in fh:
            strand_len = sum([fh[strand][f].pixels for f in fh[strand]])
            longest_strand = max(strand_len, longest_strand)

        return (strands, longest_strand)

    def get_colliding_fixtures(self, strand, address, loc='start', radius=50):
        """
        Returns a list of (strand, fixture, pixel) tuples containing the addresses of any fixtures that collide with the
        input fixture.  Pixel is set to the closest pixel to the target location (generally either the first or last
        pixel).  The collision bound is a circle given by the radius input, centered on the specified fixture endpoint.

        Location to collide: 'start' == pos1, 'end' == pos2, 'midpoint' == midpoint
        """
        f = self.fixture(strand, address)

        if loc == 'start':
            center = f.pos1
        elif loc == 'end':
            center = f.pos2
        elif loc == 'midpoint':
            center = f.midpoint()
        else:
            raise ValueError("loc must be one of 'start', 'end', 'midpoint'")

        colliding = self._colliding_fixtures_cache.get((strand, address, loc), None)

        if colliding is None:
            colliding = []
            r2 = pow(radius, 2)
            x1, y1 = center
            for tf in self.fixtures():
                # Match start point
                x2, y2 = tf.pos1
                if pow(x2 - x1, 2) + pow(y2 - y1, 2) <= r2:
                    #print tf, "collides with", strand, address
                    colliding.append((tf.strand, tf.address, 0))
                    continue
                    # Match end point
                x2, y2 = tf.pos2
                if pow(x2 - x1, 2) + pow(y2 - y1, 2) <= r2:
                    #print tf, "collides with", strand, address, "backwards"
                    colliding.append((tf.strand, tf.address, tf.pixels - 1))

            self._colliding_fixtures_cache[(strand, address, loc)] = colliding

        return colliding

    def get_pixel_neighbors(self, index):
        """
        Returns a list of pixel addresses that are adjacent to the given address.
        """

        neighbors = self._pixel_neighbors_cache.get(index, None)

        if neighbors is None:
            neighbors = []
            if self._tree:
                neighbors = self._tree.query_ball_point(self.get_pixel_location(index), 3)
                # if len(neighbors) > 4:
                #     print index, neighbors
                self._pixel_neighbors_cache[index] = neighbors

        return neighbors

    def get_pixel_location(self, index):
        """
        Returns a given pixel's location in scene coordinates.
        """
        loc = self._pixel_locations_cache.get(index, None)

        if loc is None:

            strand, address, pixel = BufferUtils.index_to_logical(index)
            f = self.fixture(strand, address)

            if pixel == 0:
                loc = f.pos1
            elif pixel == (f.pixels - 1):
                loc = f.pos2
            else:
                x1, y1 = f.pos1
                x2, y2 = f.pos2
                scale = old_div(float(pixel), f.pixels)
                relx, rely = ((x2 - x1) * scale, (y2 - y1) * scale)
                loc = (x1 + relx, y1 + rely)

            self._pixel_locations_cache[index] = loc

        return loc

    def get_pixel_distance(self, first, second):
        """
        Calculates the distance (in scene coordinate units) between two pixels
        """
        dist = self._pixel_distance_cache.get((first, second), None)
        if dist is None:
            first_loc = self.get_pixel_location(first)
            second_loc = self.get_pixel_location(second)
            dist = self.get_point_distance(first_loc, second_loc)
            self._pixel_distance_cache[(first, second)] = dist
            self._pixel_distance_cache[(second, first)] = dist
        return dist

    def get_point_distance(self, first, second):
        return math.fabs(math.sqrt(math.pow(second[0] - first[0], 2) + math.pow(second[1] - first[1], 2)))

    def get_all_pixels_logical(self):
        """
        Returns all the pixel addresses in the scene (in logical strand, fixture, offset tuples)
        """
        if self._all_pixels is None:
            addresses = []
            for f in self.fixtures():
                for pixel in range(f.pixels):
                    addresses.append((f.strand, f.address, pixel))
            self._all_pixels = addresses
        return self._all_pixels

    def get_pixel_distances(self, pixel):
        return self.pixelDistances[pixel]

    def get_all_pixels(self):
        """
        Returns a list of all pixels in buffer address format (strand, offset)
        """
        if self._all_pixels_raw is None:
            all_pixels = []
            for s, a, p in self.get_all_pixels_logical():
                #pxs.append(BufferUtils.get_buffer_address((s, a, p), scene=self))
                all_pixels.append(BufferUtils.logical_to_index((s, a, p), scene=self))
            all_pixels = sorted(all_pixels)
            self._all_pixels_raw = all_pixels

        return self._all_pixels_raw

    def get_all_pixel_locations(self):
        """
        Returns a numpy array of (x, y) pairs.
        """
        if self._all_pixel_locations is None:
            pixels = self.get_all_pixels()
            pixel_location_list = []
            for pixel in pixels:
                pixel_location_list.append(self.get_pixel_location(pixel))

            self._all_pixel_locations = np.asarray(pixel_location_list)
        return np.copy(self._all_pixel_locations)


    def get_fixture_bounding_box(self):
        """
        Returns the bounding box containing all fixtures in the scene
        Return value is a tuple of (xmin, ymin, xmax, ymax)
        """
        xmin = 999999
        xmax = -999999
        ymin = 999999
        ymax = -999999

        fh = self.fixture_hierarchy()
        for strand in fh:
            for fixture in fh[strand]:
                for pixel in range(self.fixture(strand, fixture).pixels):
                    x, y = self.get_pixel_location(BufferUtils.logical_to_index((strand, fixture, pixel)))
                    if x < xmin:
                        xmin = x
                    if x > xmax:
                        xmax = x
                    if y < ymin:
                        ymin = y
                    if y > ymax:
                        ymax = y

        return (xmin, ymin, xmax, ymax)

    def get_intersection_points(self, threshold=50):
        """
        Returns a list of points in scene coordinates that represent the average location of
        each intersection of two or more fixture endpoints.

        For each fixture endpoint, all other endpoints are compared to see if they fall within a certain distance
        of the given endpoint.  This loop generates a list of groups.  Then, the average location of each
        group is calculated and returned.
        """
        if self._intersection_points is None:

            endpoints = []
            for f in self.fixtures():
                endpoints.append(f.pos1)
                endpoints.append(f.pos2)

            groups = []
            while len(endpoints) > 0:
                endpoint = endpoints.pop()
                group = [endpoint]
                to_remove = []
                for other in endpoints:
                    dx, dy = (other[0] - endpoint[0], other[1] - endpoint[1])
                    dist = math.fabs(math.sqrt(math.pow(dx, 2) + math.pow(dy, 2)))
                    if (dist < threshold):
                        group.append(other)
                        to_remove.append(other)
                endpoints = [e for e in endpoints if e not in to_remove]
                groups.append(group)

            centroids = []
            for group in groups:
                num_points = len(group)
                tx = 0
                ty = 0
                for point in group:
                    tx += point[0]
                    ty += point[1]
                centroids.append((old_div(tx, num_points), old_div(ty, num_points)))
            self._intersection_points = centroids

        return self._intersection_points

    def _migrate_v1_to_v2(self):

        # Add version
        self.data["file-version"] = 2

        # name -> scene-name
        self.data["scene-name"] = self.data["name"]
        self.data.pop("name")

        # Migrate fixtures to pixel groups
        self.data["pixel-groups"] = []
        strand_lengths = {}
        strand_pixel_groups = {}

        for fix in self.data["fixtures"]:
            pg = {
                "type": fix["type"],
                "strand": fix["strand"],
                "offset": fix["address"],  # Will be fixed below
                "count": fix["pixels"],
                "start": fix["pos1"],
                "end": fix["pos2"]
            }
            if strand_pixel_groups.get(fix["strand"], None) is None:
                strand_pixel_groups[fix["strand"]] = [pg,]
                strand_lengths[fix["strand"]] = fix["pixels"]
            else:
                strand_pixel_groups[fix["strand"]].append(pg)
                strand_lengths[fix["strand"]] += fix["pixels"]

        # Convert address to offset
        for strand, groups in strand_pixel_groups.items():
            groups = sorted(groups, key=lambda g: g["offset"])
            offset = groups[0]["count"]
            for group in groups[1:]:
                group["offset"] = offset
                offset += group["count"]
            self.data["pixel-groups"].extend(groups)
        self.data.pop("fixtures")

        # Migrate strand settings
        self.data["strands"] = self.data["strand-settings"]
        for i, strand in enumerate(self.data["strands"]):
            self.data["strands"][i]["length"] = strand_lengths[i]
        self.data.pop("strand-settings")

        # Removed attributes
        try:
            self.data.pop("labels-visible")
            self.data.pop("locked")
        except KeyError:
            pass

        log.info("Migrated scene from v1 to v2 format")

        self.save()

    def _load_pixel_groups(self):
        for pg_data in self["pixel-groups"]:
            if pg_data["type"] == "linear":
                pg = LinearPixelGroup(json=pg_data)
                self._pixel_groups.append(pg)
            else:
                raise NotImplementedError("Unsupported pixel group type!")
