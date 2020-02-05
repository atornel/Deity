import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class StatusLabel:
    def __init__(self, text, show_progress):

        self.label = Gtk.Label(
            name="promptframe-statuslabel",
            selectable=True,
            halign=1,
            hexpand=False,
            xalign=0,
            label=text,
            width_chars=60,
            use_markup=True,
            wrap=True,
        )
        self.spin = Gtk.Spinner()
        if show_progress:
            self.spin.start()
        self.grid = Gtk.Grid(halign=1, hexpand=False, column_spacing=2)
        self.grid.attach(self.label, 0, 0, 1, 1)
        self.grid.attach(self.spin, 1, 0, 1, 1)

    def set_text(self, label):

        self.label.set_text(label)

    def set_name(self, name):

        self.label.set_name(name)

    def start_spin(self):

        self.spin.start()

    def stop_spin(self):

        self.spin.stop()

    def get_widget(self):

        return self.grid
