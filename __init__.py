# Plugin entry point
def classFactory(iface):
    from .qmapcompare import QMapCompare

    return QMapCompare(iface)
