from collections import namedtuple
import random
from plots.mazes.GridMatrix import GridMatrix

Point = namedtuple('Point', ['row', 'col'])


class GrowingTree(object):

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
