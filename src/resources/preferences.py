import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class Preferences(Gtk.ApplicationWindow):

    def __init__(self, **kwargs):
        
        super().__init__(**kwargs)
        self.stack = Gtk.Stack(name="preferences-stack")
        self.sidebar = Gtk.StackSidebar(name="preferences-sidebar",
                                        stack=self.Stack)
        panel = Gtk.Paned(name="preferences-paned")
        panel.add1(self.sidebar)
        panel.add2(self.stack)
        self.add(panel)
        self.connect("delete-event", lambda *args: self.hide())
    
    def add_page(self, child, name, title):
        
        wid = Gtk.ScrolledWindow(name="preferences-scrolled")
        wid.add(child)
        self.stack.add_titled(wid, name, title)
