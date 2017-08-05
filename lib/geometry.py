import math


def distance(p1, p2):
    return math.sqrt(math.pow(p2[0] - p1[0], 2) + math.pow(p2[1] - p1[1], 2))


def hit_test_rect(rect, pos):
    """
    Tests if pos is inside rect (or on the edge)
    rect is defined as (x, y, width, height)
    """
    return ((pos[0] >= rect[0]) and
            (pos[0] <= rect[0] + rect[2]) and
            (pos[1] >= rect[1]) and
            (pos[1] <= rect[1] + rect[3]))


def inflate_rect(rect, delta):
    """
    Returns a new (x, y, w, h) rect with delta added on all sides
    """
    d = delta / 2
    return (rect[0] - d, rect[1] - d, rect[2] + delta, rect[3] + delta)


def distance_point_to_line(start, end, point):
    """
    Returns the shortest distance from point (an x, y tuple) to the line
    defined by start and end (both x, y tuples).
    """
    return (abs( (end[0] - start[0]) * (start[1] - point[1]) -
                 (start[0] - point[0]) * (end[1] - start[1]) ) /
            distance(start, end))