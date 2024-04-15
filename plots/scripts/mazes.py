import click
import svgwrite
from svgwrite.shapes import Line
from plots.mazes.GrowingTree import GrowingTree
from plots.mazes.GridMatrix import GridMatrix


@click.group()
def cli():
    """Entry point for drawing mazes"""


@cli.command()
def hello():
    click.echo("hello world")


@cli.command()
def draw() -> None:
    drawing = svgwrite.Drawing(filename='test.svg')
    gtree = GrowingTree(40, 58, 20)
    gtree.generate()
    gtree.get_grid().draw_smooth(drawing)
    drawing.save(pretty=True)

@cli.command()
def grid() -> None:
    drawing = svgwrite.Drawing(filename='test.svg')
    matrix = GridMatrix(40, 58, 20)
    matrix.draw_smooth(drawing)
    drawing.save(pretty=True)
