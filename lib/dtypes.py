# This file is part of Firemix.
#
# Copyright 2013-2017 Zev Benjamin <zev@strangersgate.com>
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

import numpy as np

rgb888_color = np.dtype({'names': ['r', 'g', 'b'],
                         'formats': [np.uint8, np.uint8, np.uint8],
                         'titles': ['red', 'green', 'blue']})

rgb_color = np.dtype({'names': ['r', 'g', 'b'],
                      'formats': [float, float, float],
                      'titles': ['red', 'green', 'blue']})

hls_color = np.dtype({'names': ['hue', 'light', 'sat'],
                      'formats': [float, float, float],
                      'titles': [None, 'lightness', 'saturation']})

pixel_color = hls_color

pixel_location = np.dtype({'names': ['x', 'y'],
                           'formats': [float, float]})
