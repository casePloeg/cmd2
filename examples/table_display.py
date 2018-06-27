#!/usr/bin/env python
# coding=utf-8
"""A simple example demonstrating the following:
    1) How to display tabular data
    2) How to display output using a pager

NOTE: IF the table does not entirely fit within the screen of your terminal, then it will be displayed using a pager.
You can use the arrow keys (left, right, up, and down) to scroll around the table as well as the PageUp/PageDown keys.
You can quit out of the pager by typing "q".  You can also search for text within the pager using "/".

WARNING: This example requires the tableformatter module: https://github.com/python-tableformatter/tableformatter
- pip install tableformatter
"""
import argparse

import cmd2
import tableformatter as tf

# Configure colors for when users chooses the "-c" flag to enable color in the table output
try:
    from colored import bg
    BACK_PRI = bg(4)
    BACK_ALT = bg(2)
except ImportError:
    try:
        from colorama import Back
        BACK_PRI = Back.LIGHTBLUE_EX
        BACK_ALT = Back.LIGHTYELLOW_EX
    except ImportError:
        BACK_PRI = ''
        BACK_ALT = ''


# Formatter functions
def no_dec(num: float) -> str:
    """Format a floating point number with no decimal places."""
    return "{}".format(round(num))


def two_dec(num: float) -> str:
    """Format a floating point number with 2 decimal places."""
    return "{0:.2f}".format(num)


# Population data from Wikipedia: https://en.wikipedia.org/wiki/List_of_cities_proper_by_population

# ############ Table data formatted as an iterable of iterable fields ############
EXAMPLE_ITERABLE_DATA = [['Shanghai (上海)', 'Shanghai', 'China', 'Asia', 24183300, 6340.5],
                         ['Beijing (北京市)', 'Hebei', 'China', 'Asia', 20794000, 1749.57],
                         ['Karachi (کراچی)', 'Sindh', 'Pakistan', 'Asia', 14910352, 615.58],
                         ['Shenzen (深圳市)', 'Guangdong', 'China', 'Asia', 13723000, 1493.32],
                         ['Guangzho (广州市)', 'Guangdong', 'China', 'Asia', 13081000, 1347.81],
                         ['Mumbai (मुंबई)', 'Maharashtra', 'India', 'Asia', 12442373, 465.78],
                         ['Istanbul (İstanbuld)', 'Istanbul', 'Turkey', 'Eurasia', 12661000, 620.29],
                        ]

# Calculate population density
for row in EXAMPLE_ITERABLE_DATA:
    row.append(row[-2]/row[-1])


# Column headers plus optional formatting info for each column
COLUMNS = [tf.Column('City', width=11, header_halign=tf.ColumnAlignment.AlignCenter),
           tf.Column('Province', header_halign=tf.ColumnAlignment.AlignCenter),
           'Country',  # NOTE: If you don't need any special effects, you can just pass a string
           tf.Column('Continent', cell_halign=tf.ColumnAlignment.AlignCenter),
           tf.Column('Population', cell_halign=tf.ColumnAlignment.AlignRight, formatter=tf.FormatCommas()),
           tf.Column('Area (km²)', width=7, header_halign=tf.ColumnAlignment.AlignCenter,
                     cell_halign=tf.ColumnAlignment.AlignRight, formatter=two_dec),
           tf.Column('Pop. Density (/km²)', width=12, header_halign=tf.ColumnAlignment.AlignCenter,
                     cell_halign=tf.ColumnAlignment.AlignRight, formatter=no_dec),
          ]


# ######## Table data formatted as an iterable of python objects #########

class CityInfo(object):
    """City information container"""
    def __init__(self, city: str, province: str, country: str, continent: str, population: int, area: float):
        self.city = city
        self.province = province
        self.country = country
        self.continent = continent
        self._population = population
        self._area = area

    def get_population(self):
        """Population of the city"""
        return self._population

    def get_area(self):
        """Area of city in km²"""
        return self._area


def pop_density(data: CityInfo):
    """Calculate the population density from the data entry"""
    if isinstance(data, CityInfo):
        return no_dec(data.get_population() / data.get_area())

    return ''


# Convert the Iterable of Iterables data to an Iterable of non-iterable objects for demonstration purposes
EXAMPLE_OBJECT_DATA = []
for city_data in EXAMPLE_ITERABLE_DATA:
    # Pass all city data other than population density to construct CityInfo
    EXAMPLE_OBJECT_DATA.append(CityInfo(*city_data[:-1]))

# If table entries are python objects, all columns must be defined with the object attribute to query for each field
#   - attributes can be fields or functions. If a function is provided, the formatter will automatically call
#     the function to retrieve the value
OBJ_COLS = [tf.Column('City', attrib='city', header_halign=tf.ColumnAlignment.AlignCenter),
            tf.Column('Province', attrib='province', header_halign=tf.ColumnAlignment.AlignCenter),
            tf.Column('Country', attrib='country'),
            tf.Column('Continent', attrib='continent', cell_halign=tf.ColumnAlignment.AlignCenter),
            tf.Column('Population', attrib='get_population', cell_halign=tf.ColumnAlignment.AlignRight,
                      formatter=tf.FormatCommas()),
            tf.Column('Area (km²)', attrib='get_area', width=7, header_halign=tf.ColumnAlignment.AlignCenter,
                      cell_halign=tf.ColumnAlignment.AlignRight, formatter=two_dec),
            tf.Column('Pop. Density (/km²)', width=12, header_halign=tf.ColumnAlignment.AlignCenter,
                      cell_halign=tf.ColumnAlignment.AlignRight, obj_formatter=pop_density),
           ]

# TODO: Color row text foreground based on population density


class TableDisplay(cmd2.Cmd):
    """Example cmd2 application showing how you can display tabular data."""

    def __init__(self):
        super().__init__()

    def ptable(self, rows, columns, grid_args):
        """Format tabular data for pretty-printing as a fixed-width table and then display it using a pager.

        :param rows: required argument - can be a list-of-lists (or another iterable of iterables), a two-dimensional
                             NumPy array, or an Iterable of non-iterable objects
        :param columns: column headers and formatting options per column
        :param grid_args: argparse arguments for formatting the grid
        """
        if grid_args.color:
            grid = tf.AlternatingRowGrid(BACK_PRI, BACK_ALT)
        elif grid_args.fancy:
            grid = tf.FancyGrid()
        elif grid_args.sparse:
            grid = tf.SparseGrid()
        else:
            grid = None

        formatted_table = tf.generate_table(rows=rows, columns=columns, grid_style=grid)
        self.ppaged(formatted_table, chop=True)

    table_parser = argparse.ArgumentParser()
    table_item_group = table_parser.add_mutually_exclusive_group()
    table_item_group.add_argument('-c', '--color', action='store_true', help='Enable color')
    table_item_group.add_argument('-f', '--fancy', action='store_true', help='Fancy Grid')
    table_item_group.add_argument('-s', '--sparse', action='store_true', help='Sparse Grid')

    @cmd2.with_argparser(table_parser)
    def do_table(self, args):
        """Display data in iterable form on the Earth's most populated cities in a table."""
        self.ptable(EXAMPLE_ITERABLE_DATA, COLUMNS, args)

    @cmd2.with_argparser(table_parser)
    def do_object_table(self, args):
        """Display data in object form on the Earth's most populated cities in a table."""
        self.ptable(EXAMPLE_OBJECT_DATA, OBJ_COLS, args)


if __name__ == '__main__':
    app = TableDisplay()
    app.debug = True
    app.cmdloop()
