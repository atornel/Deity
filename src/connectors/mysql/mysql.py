from threading import Thread
import time
import gi
import mysql.connector as mc

gi.require_versions({"Gtk": "3.0", "GtkSource": "3.0"})
from gi.repository import GObject, Gtk

from resources import StatusLabel, Table


class Connector(GObject.GObject):

    __gsignals__ = {
        "query-status": (GObject.SignalFlags.RUN_LAST, None, (int,)),
        "query-waiting": (GObject.SignalFlags.RUN_LAST, None, (int,)),
        "request": (GObject.SignalFlags.RUN_LAST, None, (str,))
    }

    def __init__(self, **conn_params):

        super().__init__()

        self.username = conn_params["username"]

        try:
            self.connector = mc.connect(**conn_params)
        except Exception as error:
            raise ConnectionError(error)

        self.cursor = self.connector.cursor()
        self.cursor_busy = False
        self.waiting_queries = []
        self.results = []

    def execute(self, idx, query):

        if not self.cursor_busy:
            self.cursor_busy = True
            status = StatusLabel("Query running", True)
            self.make_thread(idx, query, status)
            return status
        else:
            status = StatusLabel("Query waiting", True)
            self.waiting_queries.append((idx, query, status))
            self.emit("query-waiting", len(self.waiting_queries))
            return status

    def execute_next_query(self):

        idx, query, status = self.waiting_queries.pop(0)
        self.emit("query-waiting", len(self.waiting_queries))
        self.make_thread(idx, query, status)

    def get_language(self):

        from gi.repository import GtkSource

        lm = GtkSource.LanguageManager.get_default()
        language = lm.get_language("sql")
        return language

    def make_thread(self, idx, query, status):

        thread = Thread(target=self.thread_execute, args=(idx, query, status))
        thread.start()

    def prepare_message(self, lag):

        rows = self.cursor.rowcount
        warns = self.cursor.fetchwarnings()
        warns_count = 0 if not warns else len(warns)

        return f"{rows} rows changed. ({round(lag, 3)} seconds; {warns_count} warnings)"

    def request_quit(self):

        dialog = Gtk.MessageDialog(
            name="application-quit_dialog",
            text="Do you want to quit?",
            secondary_text="The connection will be terminated after you quit.\nPlease rollback or commit do undo or save the changes.",
            message_type=2,
        )
        dialog.add_buttons(
            "Cancel", 0, "Commit and Quit", 1, "Rollback and Quit", 2, "Simply Quit", 3
        )
        rcode = dialog.run()
        dialog.destroy()
        del dialog
        return rcode

    def get_menu_items(self):

        pass

    def get_results(self, num=0):

        idx, query, headers, result = self.results.pop(num)
        if not result:
            return None

        view = self.get_treeview(headers, result)

        return f"Query {idx} ", view

    def get_table(self, headers, result):

        table = Table(headers, result)
        return table.get_table()

    def get_treeview(self, headers, result):

        liststore = Gtk.ListStore(*(len(headers) * (str,)))

        for row in result:
            m_row = [str(data) for data in row]
            liststore.append(m_row)

        treeview = Gtk.TreeView(model=liststore)

        for i, header in enumerate(headers):
            cell = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(header, cell, text=i)
            treeview.append_column(column)
        return treeview

    def quit(self, rcode):

        if rcode == 1:
            self.connector.commit()
        if rcode == 2:
            self.connector.rollback()
        if rcode == 3:
            pass
        self.cursor.close()
        self.connector.close()

    def thread_execute(self, idx, query, status):

        i = time.time()
        try:
            error = None
            self.cursor.execute(query)
        except Exception as err:
            error = err
        f = time.time()

        if error:
            message = f"Error: {error}"
            status.set_name("promptframe-statuslabel_error")
        else:
            message = self.prepare_message(f - i)
        status.set_text(message)
        status.stop_spin()

        try:
            (headers, results) = (self.cursor.column_names, self.cursor.fetchall())
        except mc.InterfaceError as e:
            headers, results = (), ()
        except Exception as e:
            print(e)

        self.results.append((idx, query, headers, results))
        self.emit("query-status", len(results))

        if self.waiting_queries:
            self.execute_next_query()
        else:
            self.cursor_busy = False
