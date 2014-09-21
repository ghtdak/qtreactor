__author__ = 'ght'

qt_preset = "PyQt4"

class _config(object):
    def __init__(self):
        self.qtname = qt_preset
        if self.qtname != "":
            self.preset = True

_instance = _config()

def set_qt_name(name):
    if _instance.preset == True and name != _instance.qtname:
        raise Exception("Qt Static Configuration")

    _instance.qtname = name

def get_qt_name():
    return _instance.qtname
