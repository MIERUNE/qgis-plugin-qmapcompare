import os

from qgis.PyQt.QtCore import QT_VERSION_STR, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from .qmapcompare_dockwidget import QMapCompareDockWidget

QT_VERSION_INT = int(QT_VERSION_STR.split(".")[0])

if QT_VERSION_INT <= 5:
    left_dock_widget_area = Qt.LeftDockWidgetArea
else:
    left_dock_widget_area = Qt.DockWidgetArea.LeftDockWidgetArea

PLUGIN_NAME = "QMapCompare"


class QMapCompare:
    def __init__(self, iface):
        self.iface = iface
        self.win = self.iface.mainWindow()
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.icon_path = os.path.join(self.plugin_dir, "icon", "icon.png")
        self.menu = PLUGIN_NAME

        self.dockwidget = None

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_plugin_toolbar=True,
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
        if add_to_plugin_toolbar:
            self.iface.addToolBarIcon(action)
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
        self.iface.addDockWidget(left_dock_widget_area, self.dockwidget)
        # Populate layers in UI
        self.dockwidget.process_node()

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(PLUGIN_NAME, action)
            self.iface.removeToolBarIcon(action)
        self.iface.removeDockWidget(self.dockwidget)
        self.dockwidget = None

    def toggle_widget(self):
        if self.dockwidget is None:
            return

        # Handle switching widget visibility when click on icon
        if self.dockwidget.isVisible():
            # Stop any ongoing comparison
            self.dockwidget._on_pushbutton_stopcompare_clicked()
            self.dockwidget.hide()
        else:
            self.dockwidget.show()
            self.iface.addDockWidget(left_dock_widget_area, self.dockwidget)
            self.dockwidget.process_node()
