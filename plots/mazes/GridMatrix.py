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
