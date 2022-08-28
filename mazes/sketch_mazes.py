import vsketch


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


class MazesSketch(vsketch.SketchClass):
    # Sketch parameters:
    # radius = vsketch.Param(2.0)

    def initMatrix(self, width, height, scale):

        matrix = []
        for row in range(height):
            matrix.append([])
            for col in range(width):
                matrix[row].append(LaticePoint(col * scale, row * scale))
                if row == height - 1:
                    matrix[row][col].draw_down = False
                if col == width - 1:
                    matrix[row][col].draw_right = False
        return matrix

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=False)
        vsk.scale("mm")

        print("width: %s" % vsk.width)
        print("height: %s" % vsk.height)
        matrix = self.initMatrix(40, 58, 5)
        for row_index in range(len(matrix)):
            for col_index in range(len(matrix[row_index])):
                if matrix[row_index][col_index].draw_right:
                    vsk.line(
                            matrix[row_index][col_index].x,
                            matrix[row_index][col_index].y,
                            matrix[row_index][col_index + 1].x,
                            matrix[row_index][col_index + 1].y
                            )
                if matrix[row_index][col_index].draw_down:
                    vsk.line(
                            matrix[row_index][col_index].x,
                            matrix[row_index][col_index].y,
                            matrix[row_index + 1][col_index].x,
                            matrix[row_index + 1][col_index].y
                            )

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    MazesSketch.display()
