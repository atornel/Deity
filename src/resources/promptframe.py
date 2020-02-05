import gi

gi.require_versions({"Gtk": "3.0", "GtkSource": "3.0"})
from gi.repository import Gtk, GtkSource


class PromptFrame(Gtk.Bin):
    def __init__(self, number, language):
        super().__init__()
        self.__parent = Gtk.Grid(
            name="promptframe-parent", margin=4, column_spacing=2, row_spacing=2
        )
        self.__buf = GtkSource.Buffer(
            language=language, highlight_syntax=True, highlight_matching_brackets=True
        )
        self.__editor = GtkSource.View(
            name="promptframe-editor",
            hexpand=True,
            halign=0,
            monospace=True,
            buffer=self.__buf,
            wrap_mode=3,
        )
        self.__number = number
        self.make_prompt()

    def make_prompt(self):

        prompt_in = Gtk.Label(
            use_markup=True,
            label=str(f"In [{self.__number}]:\t"),
            name="promptframe-input_prompt",
            valign=1,
        )
        self.__parent.attach(prompt_in, 0, 0, 1, 1)
        self.__parent.attach(self.__editor, 1, 0, 1, 1)
        self.add(self.__parent)
        self.show_all()

    def freeze(self, in_text, output=Gtk.Label(), show_input=True, show_output=True):

        if show_input:
            self.__buf.set_text(in_text, len(in_text))
            self.__editor.set_editable(False)

        if show_output:
            prompt_out = Gtk.Label(
                use_markup=True,
                label=str(f"Out[{self.__number}]:\t"),
                name="promptframe-output_prompt",
                valign=1,
            )
            self.__parent.attach(prompt_out, 0, 1, 1, 1)
            self.__parent.attach(output, 1, 1, 1, 1)

        self.__parent.show_all()

    def get_text(self):

        return self.__buf.get_text(*self.__buf.get_bounds(), False)

    def get_number(self):

        return self.__number

    def set_text(self, text):

        self.__buf.set_text(text)
