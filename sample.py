import os

from PyQt5.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon

from sample_menu_01 import SampleMenu01
from sample_menu_02 import SampleMenu02

PLUGIN_NAME = "sample"


class Sample:
    def __init__(self, iface):
        self.iface = iface
        self.win = self.iface.mainWindow()
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.menu = PLUGIN_NAME
        self.toolbar = self.iface.addToolBar(PLUGIN_NAME)
        self.toolbar.setObjectName(PLUGIN_NAME)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None,
    ):
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)
        if add_to_toolbar:
            self.toolbar.addAction(action)
        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)
        self.actions.append(action)
        return action

    def initGui(self):
        # メニュー設定
        self.add_action(
            icon_path=None, text="Menu01", callback=self.show_menu_01, parent=self.win
        )
        self.add_action(
            icon_path=None, text="Menu02", callback=self.show_menu_02, parent=self.win
        )

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(PLUGIN_NAME, action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar

    def show_menu_01(self):
        self.sample_menu_01 = SampleMenu01()
        self.sample_menu_01.show()

    def show_menu_02(self):
        self.sample_menu_02 = SampleMenu02()
        self.sample_menu_02.show()
