import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class Table:
    def __init__(self, headers, data, selectable=True):

        self.__grid = Gtk.Grid(
            name="output-table_grid", margin_left=4, margin_right=4, margin_top=4
        )
        self.__headers = tuple(headers)
        self.__data = tuple(data)
        self.__selectable = selectable

    def get_cell(self, text, title=False):

        if title:
            label = Gtk.Label(label=f"<b>{text}</b>", use_markup=True, halign=1)
        else:
            label = Gtk.Label(label=text, selectable=self.__selectable, halign=1)
        return label

    def get_table(self):

        r_idx = 0
        c_idx = 0

        for header in self.__headers:
            title_label = self.get_cell(header, title=True)
            self.__grid.attach(title_label, c_idx, r_idx, 1, 1)
            c_idx += 1
        else:
            r_idx += 1
            c_idx = 0

        for row in self.__data:
            for col in row:
                label = self.get_cell(col)
                self.__grid.attach(label, c_idx, r_idx, 1, 1)
                c_idx += 1
            r_idx += 1
            c_idx = 0

        return self.__grid

    def get_headers(self):

        return self.__headers

    def get_data(self):

        return self.__data
