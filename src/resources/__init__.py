'''A collection of basic objects commonly used in Deity.
Use `from Resources import <object>` when working under top-level directory.
When modules inside Resources require other modules of Resources, use
`from Resources.<module> import <object>`.'''

from resources.iogrid import IOGrid
from resources.loginwindow import LoginDialog
from resources.preferences import Preferences
from resources.promptframe import PromptFrame
from resources.statuslabel import StatusLabel
from resources.table import Table
