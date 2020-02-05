import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from resources.promptframe import PromptFrame


class IOGrid:
    def __init__(self, language):

        self.__scrollwin = Gtk.ScrolledWindow(
            name="iogrid-scrolled_window",
            hexpand=True,
            vexpand=True,
            valign=0,
            hscrollbar_policy=2,
        )
        self.__grid = Gtk.Grid(name="iogrid-grid")
        self.__grid.connect("size-allocate", self.scroll_down)
        self.__scrollwin.add(self.__grid)
        self.__language = language

        self.__prompt = 0
        self.__idx = 0

    def get_widget(self):

        return self.__scrollwin

    def add_prompt(self, number=0):

        if not number:
            number = self.__prompt
            self.__prompt += 1
        elif number == -1:
            number = self.__prompt - 1 if self.__prompt != 0 else self.__prompt
        prompt = PromptFrame(number, self.__language)
        self.__grid.attach(prompt, 0, self.__idx, 1, 1)
        self.__idx += 1
        prompt.show_all()
        return prompt
    
    def scroll_down(self, wid, rect):
        
        adj = self.__scrollwin.get_vadjustment()
        adj.set_value(adj.get_upper() - adj.get_page_size())
