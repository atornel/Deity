import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk

from resources.application import Application


class LoginDialog:
    def __init__(self):

        self.dialog = Gtk.Window(
            name="login-dialog", title="Welcome", height_request=300, width_request=500
        )
        self.connectors_combobox = Gtk.ComboBoxText(name="login-connectors_combobox")
        self.connector_specs = {}
        self.data = {}
        self.entry_grid = Gtk.Grid(
            name="login-entry_grid", row_spacing=2, column_spacing=2
        )
        self.error_label = Gtk.Label(name="login-error_label", use_markup=True)

        self.fetch_connectors()
        self.connectors_combobox.connect("changed", self.show_prompts)
        self.do_startup()

        Gtk.main()

    def apply_css(self):

        provider = Gtk.CssProvider()
        provider.load_from_path("themes/default/default.css")
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def connect(self, wid):

        import importlib

        data = {
            keyname: ent.get_text() for (keyname, ent) in self.data["arguments"].items()
        }

        spec = self.connector_specs[self.data["name"]]
        path = spec["path"]
        connector_mod = importlib.import_module(path)
        try:
            connector = connector_mod.Connector(**data)
            self.start_application(connector)
        except ConnectionError as err:
            self.error_label.set_text(str(err))

    def do_startup(self):

        scrolled = Gtk.ScrolledWindow(
            name="login-scrolled",
            margin_left=5,
            margin_right=5,
            margin_top=5,
            margin_bottom=5,
        )

        parent_grid = Gtk.Grid(name="login-dialog-parent_grid", row_spacing=2, valign=3)

        main_grid = Gtk.Grid(
            name="login-dialog-main_grid", row_spacing=2, column_spacing=2, halign=3
        )

        connect_button = Gtk.Button(name="login-dialog-connect", label="Connect")
        connect_button.connect("clicked", self.connect)

        main_grid.attach(self.connectors_combobox, 0, 0, 1, 1)
        main_grid.attach(self.entry_grid, 0, 1, 1, 1)
        main_grid.attach(connect_button, 0, 2, 1, 1)

        scrolled_label = Gtk.ScrolledWindow(name="login-error_scrolled", hexpand=True)
        scrolled_label.add(self.error_label)

        parent_grid.attach(main_grid, 0, 0, 1, 1)
        parent_grid.attach(scrolled_label, 0, 1, 1, 1)

        scrolled.add(parent_grid)

        self.dialog.add(scrolled)

        self.apply_css()
        self.dialog.connect("destroy", Gtk.main_quit)
        self.dialog.show_all()

    def fetch_connectors(self):

        import os, json

        try:
            parent, connector_folders = next(os.walk("connectors"))[:2]
            for folder in connector_folders:
                spec = open(f"{parent}/{folder}/ConnectorInfo")
                spec_dict = json.load(spec)
                self.connector_specs[spec_dict["display-name"]] = spec_dict
                spec.close()
        except FileNotFoundError:
            pass
        except IndexError:
            return 0
        except json.JSONDecodeError:
            print(spec)

        for spec in self.connector_specs:
            self.connectors_combobox.append_text(
                self.connector_specs[spec]["display-name"]
            )
        self.connectors_combobox.set_active(0)
        self.show_prompts(self.connectors_combobox)

    def show_prompts(self, combobox):

        name = combobox.get_active_text()

        for child in self.entry_grid.get_children():
            self.entry_grid.remove(child)
            child.destroy()

        self.data.clear()
        temp = {}
        self.data["name"] = name

        spec = self.connector_specs[name]
        required = spec.get("required")
        optional = spec.get("optional", ())

        idx = 0

        for entry_data in required:
            label = Gtk.Label(
                name="login-label_{entry_data['entry-keyname']}",
                label=entry_data["entry-name"],
                halign=1,
            )
            entry = Gtk.Entry(
                name=f"login-entry_{entry_data['entry-keyname']}",
                text=entry_data["entry-default"],
                input_purpose=entry_data.get("input_purpose", 0),
                visibility=entry_data.get("visible", True),
                halign=0,
            )
            self.entry_grid.attach(label, 0, idx, 1, 1)
            self.entry_grid.attach(entry, 0, idx + 1, 1, 1)
            idx = idx + 2

            temp[entry_data["entry-keyname"]] = entry

        if optional:
            expander = Gtk.Expander(name="login-expander", label="Advanced")
            adv_grid = Gtk.Grid(name="login-advaced_grid")
            self.entry_grid.attach(expander, 0, idx, 1, 1)
            idx = 0
            for entry_data in optional:

                label = Gtk.Label(
                    name="flogin-label_{entry_data['entry-keyname']}",
                    label=entry_data["entry-name"],
                    halign=1,
                )
                entry = Gtk.Entry(
                    name=f"login-entry_{entry_data['entry-keyname']}",
                    text=entry_data["entry-default"],
                    input_purpose=entry_data.get("input_purpose", 0),
                    visibility=entry_data.get("visible", True),
                    halign=0,
                )
                adv_grid.attach(label, 0, idx, 1, 1)
                adv_grid.attach(entry, 0, idx + 1, 1, 1)
                idx = idx + 2

                temp[entry_data["entry-keyname"]] = entry

            expander.add(adv_grid)

        self.data["arguments"] = temp
        self.entry_grid.show_all()

    def start_application(self, connector):

        self.dialog.hide()
        self.dialog.destroy()
        Gtk.main_quit()

        App = Application(connector)
        App.run()
