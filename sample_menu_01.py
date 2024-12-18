import os

from PyQt5.QtWidgets import QDialog, QMessageBox
from qgis.PyQt import uic


class SampleMenu01(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi(
            os.path.join(os.path.dirname(__file__), "sample_menu_01.ui"), self
        )

        self.ui.pushButton_run.clicked.connect(self.get_and_show_input_text)
        self.ui.pushButton_cancel.clicked.connect(self.close)

    def get_and_show_input_text(self):
        # テキストボックス値取得
        text_value = self.ui.lineEdit.text()
        # テキストボックス値をメッセージ表示
        QMessageBox.information(None, "ウィンドウ名", text_value)
