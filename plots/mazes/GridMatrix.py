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
        return "(%s, %s, %s, %s)" % (self.x, self.y, self.draw_right,
                                     self.draw_down)


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

    def point_at(self, row, col):
        return self.matrix[row][col]

    def point_set_draws_right(self, row, col, val):
        self.matrix[row][col].draw_right = val

    def point_set_draws_down(self, row, col, val):
        self.matrix[row][col].draw_down = val

    def is_carved(self, row, col):
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

    def draw_lines(self, drawing):
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
    
    def draw_smooth(self, drawing):
        for row_index in range(1, self.get_height() - 2):
            for col_index in range(1, self.get_width() - 2):
                if self.point_at(row_index, col_index).draw_right:
                    (c0, c1, c2, c3) = cr(XYPoint(self.point_at(row_index, col_index-1).x, self.point_at(row_index, col_index-1).y),
                                          XYPoint(self.point_at(row_index, col_index).x, self.point_at(row_index, col_index).y),
                                          XYPoint(self.point_at(row_index, col_index+1).x, self.point_at(row_index, col_index+1).y),
                                          XYPoint(self.point_at(row_index, col_index+2).x, self.point_at(row_index, col_index+2).y)
                                          )
                    drawing.add(Path(["M {},{}".format(c0.x, c0.y),
                                      "C {},{} {},{} {},{}".format(c1.x, c1.y, c2.x, c2.y, c3.x, c3.y)])
                            
                            )
                if self.point_at(row_index, col_index).draw_down:
                    # Compute the Catmull-Rom Spline segment from the current row,col to row+1,col
                    #     Taking special care to correctly compute the edge points via reflection
                    # Convert the Catmull-Rom segment into Cubic Bezier form
                    # Add the Cubic Bezier to the drawing
                    (c0, c1, c2, c3) = cr(XYPoint(self.point_at(row_index-1, col_index).x, self.point_at(row_index-1, col_index).y),
                                          XYPoint(self.point_at(row_index, col_index).x, self.point_at(row_index, col_index).y),
                                          XYPoint(self.point_at(row_index+1, col_index).x, self.point_at(row_index+1, col_index).y),
                                          XYPoint(self.point_at(row_index+2, col_index).x, self.point_at(row_index+2, col_index).y)
                                          )
                    drawing.add(Path(["M {},{}".format(c0.x, c0.y),
                                      "C {},{} {},{} {},{}".format(c1.x, c1.y, c2.x, c2.y, c3.x, c3.y)])
                                )

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
