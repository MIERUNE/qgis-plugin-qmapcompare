import os

from PyQt5.QtWidgets import QDockWidget, QMessageBox
from qgis.PyQt import uic


class QMapCompareDockWidget(QDockWidget):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi(
            os.path.join(os.path.dirname(__file__), "qmapcompare_dockwidget.ui"), self
        )

        self.ui.pushButton_mirror.clicked.connect(self._on_pushbutton_mirror_clicked)
        self.ui.pushButton_swipe.clicked.connect(self._on_pushbutton_swipe_clicked)
        self.ui.pushButton_lens.clicked.connect(self._on_pushbutton_lens_clicked)
        self.ui.pushButton_stopcompare.clicked.connect(self._on_pushbutton_stopcompare_clicked)
        # self.ui.pushButton_cancel.clicked.connect(self.close)

    # TODO: implement
    def _on_pushbutton_mirror_clicked(self):
        QMessageBox.information(None, "Message", "Mirror")
    
    # TODO: implement
    def _on_pushbutton_swipe_clicked(self):
        QMessageBox.information(None, "Message", "Swipe")
    
    # TODO: implement
    def _on_pushbutton_lens_clicked(self):
        QMessageBox.information(None, "Message", "Lens")
    
    # TODO: implement
    def _on_pushbutton_stopcompare_clicked(self):
        QMessageBox.information(None, "Message", "Stop!")
