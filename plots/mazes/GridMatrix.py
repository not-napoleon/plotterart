from collections import namedtuple
import random
from svgwrite.shapes import Line
from svgwrite.path import Path


XYPoint = namedtuple("XYPoint", ["x", "y"])

class LaticePoint:
    """Rerpresents a point on the grid.  Can be distorted."""
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y
        self.draw_down = True
        self.draw_right = True

    def __str__(self) -> str:
        return "LaticePoint({:3.2f}, {:3.2f}, {}, {})".format(self.x, self.y, self.draw_right, self.draw_down)

    def getXYPoint(self) -> XYPoint:
        return XYPoint(self.x, self.y)


class GridMatrix:

    def __init__(self, width: int, height: int, scale: int):

        self.matrix = []
        self.width: int = width
        self.height: int = height
        self.scale = scale
        for row in range(height):
            self.matrix.append([])
            for col in range(width):
                col_jitter = random.uniform(-0.4 * scale, 0.4 * scale)
                row_jitter = random.uniform(-0.4 * scale, 0.4 * scale)

                self.matrix[row].append(LaticePoint((col * scale) + col_jitter, (row * scale) + row_jitter))
                if row == height - 1:
                    self.matrix[row][col].draw_down = False
                if col == width - 1:
                    self.matrix[row][col].draw_right = False

    def get_width(self) -> int:
        return self.width

    def get_height(self) -> int:
        return self.height

    def point_at(self, row, col) -> LaticePoint:
        return self.matrix[row][col]

    def point_set_draws_right(self, row, col, val) -> None:
        self.matrix[row][col].draw_right = val

    def point_set_draws_down(self, row, col, val) -> None:
        self.matrix[row][col].draw_down = val

    def is_carved(self, row, col) -> bool:
        """
        This is confusing, sorry future me.  GirdMatrix is organized by points,
        not boxes. This method cares about boxes.  We adopt the convention that
        a point refers to the top left corner of a box.  Furthermore, this
        method inverts the meaning of true and false - True indicates that a
        wall has been carved, while True on a LaticePoint indicates it should
        be drawn, which is the opposite of carved
        """
        return (
                # up
                self.matrix[row][col].draw_right is False or
                # left
                self.matrix[row][col].draw_down is False or
                # down
                self.matrix[row + 1][col].draw_right is False or
                # right
                self.matrix[row][col + 1].draw_down is False
            )

    def draw_lines(self, drawing) -> None:
        for row_index in range(self.get_height()):
            for col_index in range(self.get_width()):
                if self.point_at(row_index, col_index).draw_right:
                    drawing.add(
                            Line(
                                (self.point_at(row_index, col_index).x,
                                 self.point_at(row_index, col_index).y),
                                (self.point_at(row_index, col_index + 1).x,
                                 self.point_at(row_index, col_index + 1).y),
                                stroke="black",
                                stroke_width="1"
                                ),
                            )
                if self.point_at(row_index, col_index).draw_down:
                    drawing.add(
                            Line(
                                (self.point_at(row_index, col_index).x,
                                 self.point_at(row_index, col_index).y),
                                (self.point_at(row_index + 1, col_index).x,
                                 self.point_at(row_index + 1, col_index).y),
                                stroke="black",
                                stroke_width="1"
                                )
                            )
    
    def draw_smooth(self, drawing) -> None:
        for row_index in range(0, self.get_height()):
            points = []
            for col_index in range(0, self.get_width()):
                # This is dumb.  I bet NumPy has a way to slice rows and columns out of a matrix.
                points.append(self.point_at(row_index, col_index))
            drawing.add(Path(catmull_rom(points, False), stroke="black", stroke_width="5", fill="none"))

        for col_index in range(0, self.get_width()):
            points = []
            for row_index in range(0, self.get_height()):
                points.append(self.point_at(row_index, col_index))
            drawing.add(Path(catmull_rom(points, True), stroke="black", stroke_width="5", fill="none"))


# Spline Stuff
# TODO: pull this into a different file
def catmull_rom(points, draw_down):
    """
    Compute the Catmull-Rom spline passing through all of the provided control points
    
    Returns an array of path commands
    """
    path_components = []
    path_components.append("M {},{}".format(points[0].x, points[0].y))
    # TODO: do anything useful with the end points
    for i in range(0, len(points) - 1):

        # p1 and p2 will always exist. For edge cases, compute p0 or p3 in terms 
        # of p2 or p1, respectively, so we should set those values first
        p1 = points[i]
        p2 = points[i + 1]

        if i == 0:
            # for the first point, reflect p2 across p1
            p0 = LaticePoint(
                    p1.x-(p2.x - p1.x),
                    p1.y-(p2.y - p1.y)
                    )
        else: 
            p0 = points[i-1]

        if i == len(points) - 2:
            # for the last point, reflect p1 across p2
            p3 = LaticePoint(
                    p2.x-(p1.x - p2.x),
                    p2.y-(p1.y - p2.y)
                    )
        else:
            p3 = points[i + 2]

        if draw_down:
            draw = p1.draw_down
        else:
            draw = p1.draw_right
        if draw:
            # Compute the Catmull-Rom Spline segment from the current row,col to row+1,col
            #     Taking special care to correctly compute the edge points via reflection
            # Convert the Catmull-Rom segment into Cubic Bezier form
            # Add the Cubic Bezier to the drawing
            (c0, c1, c2, c3) = cr(p0.getXYPoint(),
                                  p1.getXYPoint(),
                                  p2.getXYPoint(),
                                  p3.getXYPoint()
                                  )
            # c0 should be the current point, so we don't need to specify it
            path_components.append("C {},{} {},{} {},{}".format(c1.x, c1.y, c2.x, c2.y, c3.x, c3.y))
        else:
            # otherwise just move the pen to the next point
            path_components.append("M {},{}".format(p2.x, p2.y))
    return path_components


def cr(p0, p1, p2, p3):
    """
    Compute the Catmull-Rom Spline segment from p2 to p3, using p1 and p4 as
    the bordering control points.  Return the results as a quad of Bezier
    control points for the resulting curve.
    """
    b0 = p1
    # find the vector between p0 and p2, scale it down by a factor of 3, and apply it to p1
    # 1/6 is a slightly magic number here.  That's the 1/2 scale factor of the Catmull-Rom
    # times the 1/3 conversion factor from a Hermite vector to a Bezier control point
    vec_x = (p2.x - p0.x)/6
    vec_y = (p2.y - p0.y)/6
    b1 = XYPoint(p1.x + vec_x, p1.y + vec_y)

    # Same thing, but for p1 and p4
    vec_x = (p1.x - p3.x)/6
    vec_y = (p1.y - p3.y)/6
    b2 = XYPoint(p2.x + vec_x, p2.y + vec_y)

    b3 = p2

    return (b0, b1, b2, b3)
