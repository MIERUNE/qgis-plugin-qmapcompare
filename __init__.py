import sys
import os

# to import modules as non-relative
sys.path.append(os.path.dirname(__file__))


def classFactory(iface):
    from qmapcompare import QMapCompare

    return QMapCompare(iface)
