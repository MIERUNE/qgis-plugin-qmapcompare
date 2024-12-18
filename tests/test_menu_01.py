import unittest

from sample_menu_01 import SampleMenu01

from .utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class TestMenu1(unittest.TestCase):
    def test_menu(self):
        menu = SampleMenu01()

        assert menu.isVisible() is False
        menu.show()
        assert menu.isVisible() is True
        menu.hide()
        assert menu.isVisible() is False


if __name__ == "__main__":
    unittest.main()
