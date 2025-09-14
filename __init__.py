# __init__.py
def classFactory(iface):
    """
    QGIS calls this function to load the plugin.
    'iface' is the QGIS interface instance.
    """
    from .plugin import GreedyClusterPlugin  # ✅ Match the folder + file + class name
    return GreedyClusterPlugin(iface)
