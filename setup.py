from setuptools import setup, find_packages

setup(
    name="Plotter Art",
    version="0.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'svgwrite'
    ],
    entry_points='''
        [console_scripts]
        mazes=plots.scripts.mazes:cli
    ''',
)
