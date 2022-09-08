from collections import namedtuple
import random
import svgwrite
from svgwrite.shapes import Line


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

    def __init__(self, width: int, height: int, scale):

        self.matrix = []
        self.width: int = width
        self.height: int = height
        self.scale = scale
        for row in range(height):
            self.matrix.append([])
            for col in range(width):
                self.matrix[row].append(LaticePoint(col * scale, row * scale))
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


Point = namedtuple('Point', ['row', 'col'])


class GrowingTreeMaze(object):

    """Store and display growing tree mazes"""

    def __init__(self, width, height, scale):
        """Initialize the "empty" map matrix, growing parameters

        :param height: Display height of the finished maze
        :param width: Display width of the finished maze

        """
        self._width = width
        self._height = height
        self._matrix = GridMatrix(width, height, scale)

    def get_uncarved_neighbors(self, point):
        """Return a list of directions (suitable for input into carve) of
        cells neighboring the given point that have not been carved.
        """
        neighbors = []
        cases = (
                ('U', Point(point.row - 1, point.col)),
                ('D', Point(point.row + 1, point.col)),
                ('L', Point(point.row, point.col - 1)),
                ('R', Point(point.row, point.col + 1)),
        )
        for direction, neighbor in cases:
            if not self._matrix.is_carved(neighbor.row, neighbor.col):
                neighbors.append((direction, neighbor))
        return neighbors

    # TODO: this probably belongs on GridMatrix
    def carve(self, point, direction):
        if direction == 'U':
            if point.row == 0:
                raise IndexError
            self._matrix.point_set_draws_right(point.row, point.col, False)
        elif direction == 'D':
            if point.row == self._height:
                raise IndexError
            self._matrix.point_set_draws_right(point.row + 1, point.col, False)
        elif direction == 'L':
            if point.col == 0:
                raise IndexError
            self._matrix.point_set_draws_down(point.row, point.col, False)
        elif direction == 'R':
            if point.col == self._width:
                raise IndexError
            self._matrix.point_set_draws_down(point.row, point.col + 1, False)
        else:
            raise ValueError("Unknown direction %s" % str(direction))

    def generate(self):
        """Generate the maze
        """
        start_col = int(random.randrange(0, self._width))
        start_row = int(random.randrange(0, self._height))
        to_carve_list = [Point(start_row, start_col)]
        while to_carve_list:
            point = random.choice(to_carve_list)
            neighbors = self.get_uncarved_neighbors(point)
            if len(neighbors) == 0:
                to_carve_list.remove(point)
                continue
            direction, next_point = random.choice(neighbors)
            self.carve(point, direction)
            to_carve_list.append(next_point)

    def get_grid(self) -> GridMatrix:
        return self._matrix

    def __str__(self):
        return str(self._matrix)


def draw() -> None:
    drawing = svgwrite.Drawing(filename='test.svg')
    gtree = GrowingTreeMaze(40, 58, 5)
    gtree.generate()
    matrix = gtree.get_grid()
    for row_index in range(matrix.get_height()):
        for col_index in range(matrix.get_width()):
            if matrix.point_at(row_index, col_index).draw_right:
                drawing.add(
                        Line(
                            (matrix.point_at(row_index, col_index).x,
                             matrix.point_at(row_index, col_index).y),
                            (matrix.point_at(row_index, col_index + 1).x,
                             matrix.point_at(row_index, col_index + 1).y),
                            stroke="black",
                            stroke_width="1"
                            ),
                        )
            if matrix.point_at(row_index, col_index).draw_down:
                drawing.add(
                        Line(
                            (matrix.point_at(row_index, col_index).x,
                             matrix.point_at(row_index, col_index).y),
                            (matrix.point_at(row_index + 1, col_index).x,
                             matrix.point_at(row_index + 1, col_index).y),
                            stroke="black",
                            stroke_width="1"
                            )
                        )
    drawing.save(pretty=True)


if __name__ == "__main__":
    draw()
