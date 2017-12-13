"""Helpful geometry functions."""
from math import sin, cos, radians, degrees, sqrt, atan2


def angle_to_unit_x_y(angle):
    """Return unit length (0 to 1) x y components of angle."""
    angle = radians(angle)  # convert to radians

    # times -1 for y because of pygame coordinates
    return sin(angle), -1 * cos(angle)


def angle_to_x_y(angle, magnitude):
    """Return x y components (multiplied by magnitude) of angle."""
    angle = radians(angle)  # convert to radians

    # times -1 for y because of pygame coordinates
    return sin(angle) * magnitude, -1 * cos(angle) * magnitude


def dot(origin, p1_end, p2_end):
    """Return dot product of (origin, p1_end) and (origin, p2_end)."""
    ux, uy = (p1_end[0] - origin[0], p1_end[1] - origin[1])
    vx, vy = (p2_end[0] - origin[0], p2_end[1] - origin[1])
    return ux * vx + uy * vy


def mag(start, end):
    """Return magnitude of (start, end) vector."""
    return sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)


def angle_between(origin, p1_end, p2_end):
    """Return angle between (origin, p1_end) and (origin, p2_end).

    Normalized to -180 to 180 range."""
    ux, uy = (p1_end[0] - origin[0], p1_end[1] - origin[1])
    vx, vy = (p2_end[0] - origin[0], p2_end[1] - origin[1])

    angle = degrees(atan2(vy, vx) - atan2(uy, ux))  # 0 to -360
    if angle < -180:
        angle %= 360  # normalize to -180 to 180
    return angle


def get_line(start, end):
    """Bresenham's Line Algorithm for pixel-wise line approximation.

    Produces a list of line points from start to end such as:
    [(0, 0), (1, 1), (1, 2), (2, 3), (3, 4)]"""
    # Setup initial conditions
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1

    # Determine how steep the line is
    is_steep = abs(dy) > abs(dx)

    # Rotate line
    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    # Swap start and end points if necessary and store swap state
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True

    # Recalculate differentials
    dx = x2 - x1
    dy = y2 - y1

    # Calculate error
    error = int(dx / 2.0)
    y_step = 1 if y1 < y2 else -1

    # Iterate over bounding box generating points between start and end
    y = y1
    points = []
    for x in range(x1, x2 + 1):
        coord = (y, x) if is_steep else (x, y)
        points.append(coord)

        error -= abs(dy)
        if error < 0:
            y += y_step
            error += dx

    # Reverse the list if the coordinates were swapped
    if swapped:
        points.reverse()

    return points
