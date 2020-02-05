import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gio, GObject, Gtk

class Plugin(GObject.Object):

    __gsignals__ = {"request": (GObject.SignalFlags.RUN_LAST, None, (str,))}

    def __init__(self, application):
        super().__init__()
        application.connect("request", print)
        self.status = Gtk.Label(label="Started plugin")
        self.connector = None
    
    def get_dependency(self):
        
        return ("statusbar", "connector"), ()

    def get_menu_items(self):
        
        items = [Gio.MenuItem.new("Say A", "app.say_A"),
                 Gio.MenuItem.new("Say B", "app.say_B")]
        actions = [Gio.SimpleAction(name="say_A"),
                   Gio.SimpleAction(name="say_B")]
        funcs = [(self.say_hello, "A"), (self.say_hello, "B")]
        for action, func in zip(actions, funcs):
            action.connect("activate", *func)
        return items, actions

    def get_name(self):
        
        return "Plugin"
    
    def say_hello(self, wid, idx, msg=""):

        msg = idx if not msg else msg
        self.status.set_text(f"Hello {msg}")
    
    def supply_dependency(self, deps):
        
        statusbar = deps["statusbar"]
        self.connector = deps["connector"]
        
        statusbar.pack_end(self.status, 1, 1, 1)
        self.connector.connect("query-status", self.say_hello) #{"enabled-plugins":[["Plugin", "Extensions.Plugin.Plugin"]],
    
    def request_quit(self):
        
        dialog = Gtk.MessageDialog(
            name="plugin-quit_dialog",
            text="You clicked quit",
            secondary_text="Are you sure about your choice?",
            message_type=2,
        )
        dialog.add_buttons(
            "Nope cancel", 0, "Yes quit", 1
        )
        rcode = dialog.run()
        dialog.destroy()
        del dialog
        return rcode

    def quit(self, rcode):
        
        print("Bye with", rcode)
