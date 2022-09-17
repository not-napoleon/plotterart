import click
import svgwrite
from svgwrite.shapes import Line
from plots.mazes.GrowingTree import GrowingTree


@click.group()
def cli():
    """Entry point for drawing mazes"""


@cli.command()
def hello():
    click.echo("hello world")


@cli.command()
def draw() -> None:
    drawing = svgwrite.Drawing(filename='test.svg')
    gtree = GrowingTree(40, 58, 5)
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
