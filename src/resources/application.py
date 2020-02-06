"""The application interface for Deity. Its better to import and run the
Application after Login window."""

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Gtk

from resources.iogrid import IOGrid
from resources.preferences import Preferences

class Application(Gtk.Application):
    
    __gsignals__ = {"request": (GObject.SignalFlags.RUN_LAST, None, (str,))}
    
    def __init__(self, connector):

        """Creates a Deity application. Requires a valid Connector for handling
        input and output.

        Multiple instances of Deity is not allowed; so at a time only one Deity
        exists and further starts are ignored."""

        super().__init__(application_id="org.ourdbms.deity", flags=0)

        self.window = Gtk.Window(gravity=5,
                                 height_request=500,
                                 name="input-window",
                                 width_request=750,
                                 window_position=0)  # Main window for input

        self.output_window = Gtk.Window(deletable=False,
                                        gravity=5,
                                        height_request=500,
                                        name="output-window",
                                        title="Output",
                                        width_request=500,
                                        window_position=0)  # Secondary window for output

        self.history = []  # Stores the queries of current session
        self.iogrid = IOGrid(connector.get_language())
        self.notebook = Gtk.Notebook(name="output-notebook",
                                     enable_popup=True,
                                     scrollable=True)
        self.other = {}
        self.statuslabel = Gtk.Label(halign=1,
                                     height_request=25,
                                     label="Queries on hold : 0",
                                     margin_end=5,
                                     name="input-statusbar")
        self.connector = connector
        self.current_prompt = None  # The current `PromptFrame` object
        self.prompt_cursor = 0
        # Stores index of the query while scrolling across history.

    def apply_css(self, path):

        """Applies the CSS for the entire application. The default CSS is
        `Default.css`."""

        provider = Gtk.CssProvider()
        provider.load_from_path(path)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def apply_settings(self, settings):
        
        self.apply_css(settings.get("theme", "themes/default/default.css"))

    def delete_page(self, wid, child):

        """Deletes the page of a `self.notebook`. When there are no pages to
        display, it shows a placeholder image."""

        page_num = self.notebook.page_num(child)
        self.notebook.remove_page(page_num)
        if not self.notebook.get_n_pages():
            self.output_window.remove(self.notebook)
            placeholder = self.get_placeholder_image()
            self.output_window.add(placeholder)
            placeholder.show_all()

    def do_activate(self):

        """Activates the application by displaying both console and output 
        window. This process is done everytime when user launches the 
        application, as Deity allows one instance of itself to be available."""

        Gtk.Application.do_activate(self)
        self.initiate_plugins()
        self.other["menu_button"].set_menu_model(self.prepare_menu())
        self.output_window.show_all()
        self.window.show_all()

    def do_startup(self):

        """Packs the widgets into parents, fetches addons and other essential.
        This is done only once; during start-up and further launches are
        forwarded to `self.do_activate`"""
        
        import json

        GLib.set_application_name("Deity")
        Gtk.Application.do_startup(self)
        
        settings = self.get_settings()

        menub = Gtk.MenuButton(name="input-menu_button",
                               use_popover=True)

        headerbar = Gtk.HeaderBar(name="input-headerbar",
                                  show_close_button=True,
                                  title="Deity")

        main_grid = Gtk.Grid(name="input-main_grid")

        statusbar = Gtk.Box(name="input-statusbar",
                            orientation=0,
                            spacing=2)
        statusbar.pack_start(self.statuslabel, 1, 1, 1)

        self.connector.connect("query-status", self.show_output)
        self.connector.connect("query-waiting",
                               lambda wid, count: self.statuslabel.set_text(
                                   f"Queries on hold : {count}"))
        self.connector.connect("request", print)

        headerbar.pack_end(menub)

        main_grid.attach(self.iogrid.get_widget(), 0, 0, 1, 1)
        main_grid.attach(statusbar, 0, 1, 1, 1)

        self.output_window.add(self.get_placeholder_image())

        self.window.set_titlebar(headerbar)
        self.window.set_default_icon_from_file("artwork/Logo.png")
        self.window.add(main_grid)

        self.window.connect("key-press-event", self.parse_keypress)
        self.window.connect("delete-event", self.request_quit)
        
        self.other["connector"] = self.connector
        self.other["headerbar"] = headerbar
        self.other["history"] = self.history
        self.other["input-window"] = self.window
        self.other["iogrid"] = self.iogrid
        self.other["plugins"] = self.get_plugins(settings["enabled-plugins"])
        self.other["statusbar"] = statusbar
        self.other["statuslabel"] = self.statuslabel
        self.other["output-notebook"] = self.notebook
        self.other["output-window"] = self.output_window
        self.other["main-grid"] = main_grid
        self.other["menu_button"] = menub
        
        self.apply_settings(settings)
        self.current_prompt = self.iogrid.add_prompt()

        self.window.set_application(self)
        self.output_window.set_application(self)

        self.output_window.move(800, 150)
        self.window.move(75, 160)

    def execute_query(self, num, text):

        """Executes the query by passing it to the connector. Returns a widget
        that shows the status of given query.
        `num` is a unique index of the query with `text` being the query
        itself"""

        output_status = self.connector.execute(num, text)
        return output_status.get_widget()

    def get_about(self, *args):

        """Shows an `About` dialog."""
        comment = "An opensource, modern database querying, editing application"
        license = "Freedom to use, edit, modify and distribute with attribution"
        about_dialog = Gtk.AboutDialog(authors=["J Arun Mani", "Jide Guru"],
                                       artists=["Nika Akin (from Pexels; for photo on logo)"],
                                       comments=comment,
                                       copyright="© 2020-Forever 😏",
                                       license=license,
                                       license_type=1,
                                       name="input-about_dialog",
                                       program_name="Deity",
                                       version="Version Alpha",
                                       wrap_license=True)
        about_dialog.run()
        about_dialog.destroy()

    def get_input(self):

        """Returns the unique index of query along with the query."""

        in_text = self.current_prompt.get_text()
        num = self.current_prompt.get_number()
        if not in_text.strip():
            return num, ""  # Input is just empty text, do nothing.
        self.history.append(in_text)
        self.prompt_cursor = 0
        return num, in_text

    def get_output(self):

        """This function is called when the user requests execution of query.
        First we get the proper input using `self.get_input`. If the text is 
        not all white-space, we execute the query otherwise we add another 
        prompt with same index."""

        num, in_text = self.get_input()

        if not in_text:
            self.current_prompt.freeze(in_text="", show_output=False)
            # Makes the prompt un-editable.
            self.current_prompt = self.iogrid.add_prompt(number=-1)
        else:
            output = self.execute_query(num, in_text)
            self.current_prompt.freeze(in_text=in_text, output=output)
            self.current_prompt = self.iogrid.add_prompt()

    def get_placeholder_image(self):

        """Placeholder images are useful when there is no output to show. 
        This function makes one and return it."""

        grid = Gtk.Grid(name="output-placeholder_grid", halign=3, valign=3)
        label = Gtk.Label(name="output-placeholder_label",
                          label="<b> Query to show outputs </b>",
                          use_markup=True)
        image = Gtk.Image.new_from_icon_name("help-about", 6)
        image.set_name("output-placeholder_image")
        grid.attach(image, 0, 0, 1, 1)
        grid.attach(label, 0, 1, 1, 1)
        return grid

    def get_plugins(self, enabled_plugins=()):

        """Fetches the enabled plugins for Deity."""

        from importlib import import_module
        plugins = []
        for plugin_name, path in enabled_plugins:
            plugin_mod = import_module(path)
            plugins.append(plugin_mod.Plugin)
        return plugins

    def get_prepacked_menu_items(self):

        """Returns default menu items like 'About', 'Quit' etc."""

        items = [Gio.MenuItem.new("About Deity", "app.about"),
                 Gio.MenuItem.new("Preferences", "app.preferences")]
        actions = [Gio.SimpleAction(name="about"),
                   Gio.SimpleAction(name="preferences")]
        funcs = [(self.get_about, self.show_preferences)]
        for action, func in zip(actions, funcs):
            action.connect("activate", *func)
        return items, actions

    def get_settings(self):
        
        import json
        
        with open("configurations/main_configuration") as config:
            settings = json.load(config)
        return settings

    def get_tab_label(self, title, child):

        """Returns a widget with a title and close button. `child` is the widget
         added to the notebook and on clicking the `close` button, this child is
         removed from notebook."""

        button = Gtk.Button(name="output-tab_label-button",
                            relief=2)
        grid = Gtk.Grid(name="output-tab_label-grid")
        image = Gtk.Image.new_from_icon_name("dialog-close", 1)
        image.set_name("output-tab_label-image")
        label = Gtk.Label(name="output-tab_label-label", label=title)
        grid.attach(label, 0, 0, 1, 1)
        grid.attach(button, 1, 0, 1, 1)
        button.add(image)
        button.connect("clicked", self.delete_page, child)
        return grid

    def initiate_plugins(self):
        
        activated_plugins = {}
        for plugin in self.other["plugins"]:
            active_plugin = plugin(self)
            active_plugin.connect("request", print)
            activated_plugins[active_plugin.get_name()] = active_plugin
        
        for plugin in activated_plugins.values():
            general_deps, plugin_deps = plugin.get_dependency()
            general_feed = {dep:self.other.get(dep, None) for dep in general_deps}
            plugin_feed = {dep:activated_plugins.get(dep, None) for dep in plugin_deps}
            general_feed.update(plugin_feed)
            plugin.supply_dependency(general_feed)
        self.other["plugins"] = tuple(activated_plugins.values())

    def parse_keypress(self, wid, event):

        """Validates the input by user and calls the required function."""

        keyname = Gdk.keyval_name(event.keyval)
        if keyname == "Control_R":  # Key for query
            self.get_output()
        elif keyname == "Page_Up":  # Goes to previous query
            tot = len(self.history)
            if -(self.prompt_cursor) != tot:
                self.prompt_cursor -= 1
            text = self.history[self.prompt_cursor]
            self.current_prompt.set_text(text)

        elif keyname == "Page_Down":  # Drops to next query
            if (self.prompt_cursor) != -1:
                self.prompt_cursor += 1
            text = self.history[self.prompt_cursor]
            self.current_prompt.set_text(text)

    def prepare_menu(self):

        """Returns the menu for application. If an addon wishes to give a menu,
        it must be a list of menu items with action groups."""

        plugins = self.other["plugins"] + (self.connector,)

        menu = Gio.Menu()
        items, actions = self.get_prepacked_menu_items()
        for plugin in plugins:
            menuitems_group = plugin.get_menu_items()
            if menuitems_group:
                items.extend(menuitems_group[0])
                actions.extend(menuitems_group[1])

        for item in items:
            menu.append_item(item)
        for action in actions:
            self.add_action(action)
        return menu

    def request_quit(self, *args):

        """Informs every plugin that the user has requested quit. The
        applications asks the plugin to see if they are in a state to close the
        application. For example, a connector may confirm with the user that
        they haven't saved the changes made and if they wish to quit.
        
        Based on the user's response `rcode` is given by the plugin. If the
        `rcode` is 0, then it means that the plugin cannot exit and other plugin
        are not asked to quit.
        
        Plugins actually do not quit, when the `rcode` is non-zero, who knows
        user might have changed their mind when other plugins confirms them for
        quit, so the plugins actually terminate themselves when none of the
        addons return zero."""

        addons = (self.connector,) + self.other["plugins"]

        rcodes = {}

        for addon in addons:
            rcode = addon.request_quit()
            rcodes[addon] = rcode
            if not rcode: # A plugin gave zero, stop asking others.
                return True # To prevent destruction of window
        for addon, rcode in rcodes.items():
            addon.quit(rcode)  # Here only plugin are closed.
        self.quit()  # No plugin gave 0

    def set_settings(self, settings):
        
        import json
        
        with open("configurations/main_configuration", "w") as config:
            json.dump(config, settings)

    def show_output(self, conn, rcode):

        """Shows the output to user. This function is called when the connector
        emits `'query-status'` signal. `conn` is the connector and `rcode` is a 
        number. If `rcode` is a non-zero value, it means there is some output 
        to show to the user, so it fetches the output. In the other case, the 
        result is an empty set and no output is shown, but the queued output is
        pushed out."""

        if rcode:
            title, results = self.connector.get_results(0)
            scrolled = Gtk.ScrolledWindow()
            scrolled.add(results)
            tab_label = self.get_tab_label(title, scrolled)
            self.notebook.append_page(scrolled, tab_label)

            if not self.notebook.get_parent():
                child = self.output_window.get_children()[0]
                self.output_window.remove(child)
                self.output_window.add(self.notebook)
                self.notebook.show_all()
                del child

            tab_label.show_all()
            scrolled.show_all()
        else:
            self.connector.get_results(0)

    def show_preferences(self):
        
        settings = self.get_settings()
        

    def quit(self):

        """Quits the application"""

        Gtk.Application.quit(self)
