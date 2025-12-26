import numpy as np
from shapely.geometry import MultiPoint, LineString

def min_area_trapezoid(segments):
    # Step 1: Collect all endpoints
    points = []
    for seg in segments:
        points.append(seg[0])
        points.append(seg[1])

    # Step 2: Convex hull
    multipoint = MultiPoint(points)
    hull = multipoint.convex_hull
    if hull.geom_type == 'Point' or hull.geom_type == 'LineString':
        # Degenerate case
        return None

    hull_coords = np.array(hull.exterior.coords[:-1])  # ignore repeated last point

    min_area = float('inf')
    best_trapezoid = None

    # Step 3: Rotate calipers
    n = len(hull_coords)
    for i in range(n):
        # Edge i
        p1 = hull_coords[i]
        p2 = hull_coords[(i+1) % n]
        edge_vec = p2 - p1
        angle = -np.arctan2(edge_vec[1], edge_vec[0])  # rotate edge to horizontal

        # Rotation matrix
        R = np.array([[np.cos(angle), -np.sin(angle)],
                      [np.sin(angle),  np.cos(angle)]])
        rotated = np.dot(hull_coords, R.T)

        # Step 4: Top and bottom
        y_min, y_max = np.min(rotated[:,1]), np.max(rotated[:,1])
        h = y_max - y_min

        # Step 5: Left and right sides
        top_line_y = y_max
        bottom_line_y = y_min
        x_top_min = np.min(rotated[rotated[:,1]==top_line_y][:,0])
        x_top_max = np.max(rotated[rotated[:,1]==top_line_y][:,0])
        x_bottom_min = np.min(rotated[rotated[:,1]==bottom_line_y][:,0])
        x_bottom_max = np.max(rotated[rotated[:,1]==bottom_line_y][:,0])

        # Approximate trapezoid width using extreme top/bottom x
        w_top = x_top_max - x_top_min
        w_bottom = x_bottom_max - x_bottom_min
        area = h * (w_top + w_bottom) / 2

        if area < min_area:
            min_area = area
            best_trapezoid = {
                'top_y': top_line_y,
                'bottom_y': bottom_line_y,
                'x_top_min': x_top_min,
                'x_top_max': x_top_max,
                'x_bottom_min': x_bottom_min,
                'x_bottom_max': x_bottom_max,
                'rotation_angle': angle
            }

    # Step 6: Rotate trapezoid back to original coordinates
    angle = -best_trapezoid['rotation_angle']
    R_inv = np.array([[np.cos(angle), -np.sin(angle)],
                      [np.sin(angle),  np.cos(angle)]])

    # Trapezoid corners in rotated frame
    corners_rot = np.array([
        [best_trapezoid['x_bottom_min'], best_trapezoid['bottom_y']],
        [best_trapezoid['x_bottom_max'], best_trapezoid['bottom_y']],
        [best_trapezoid['x_top_max'], best_trapezoid['top_y']],
        [best_trapezoid['x_top_min'], best_trapezoid['top_y']]
    ])

    # Rotate back
    corners_orig = np.dot(corners_rot, R_inv.T)
    return corners_orig, min_area


# Example usage
segments = [
    ((0,0), (1,2)),
    ((2,1), (3,3)),
    ((1,4), (4,2))
]

trapezoid, area = min_area_trapezoid(segments)
print("Trapezoid corners:\n", trapezoid)
print("Area:", area)
