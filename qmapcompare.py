import os

from PyQt5.QtWidgets import QAction
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon

from .qmapcompare_dockwidget import QMapCompareDockWidget

PLUGIN_NAME = "QMapCompare"


class QMapCompare:
    def __init__(self, iface):
        self.iface = iface
        self.win = self.iface.mainWindow()
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.icon_path = os.path.join(self.plugin_dir, "icon", "icon.png")
        self.menu = PLUGIN_NAME

        try:
            self.toolbar = self.iface.addToolBar(PLUGIN_NAME)
            self.toolbar.setObjectName(PLUGIN_NAME)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize toolbar : {str(e)}")

        self.dockwidget = None

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
        # Add icon to menu
        self.add_action(
            self.icon_path,
            text="Toggle QMapCompare Panel",
            callback=self.toggle_widget,
            parent=self.win,
        )

        # Add UI to panel
        self.dockwidget = QMapCompareDockWidget()
        self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockwidget)
        # Populate layers in UI
        self.dockwidget.process_node()

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(PLUGIN_NAME, action)
            self.iface.removeToolBarIcon(action)
        self.iface.removeDockWidget(self.dockwidget)
        self.dockwidget = None
        del self.toolbar

    def toggle_widget(self):
        if self.dockwidget is None:
            return

        # Handle switching widget visibility when click on icon
        if self.dockwidget.isVisible():
            self.dockwidget.hide()
        else:
            self.dockwidget.show()
            self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockwidget)
            self.dockwidget.process_node()
