from PyQt5.QtCore import (
    QObject
)

class settings(QObject):
    def __init__(self):
        self.Global = {

        }
        self.Player = {
            "RandomPlay": False,
            "RandomPlayAntiReplay": True,
        }

        self.Downloader = {
            "NotifyOnDLEndIfMinimized": False,
        }

    def LoadSettingsFile(self, file):
        pass

    def SaveSettingsOnFile(self, file):
        pass

    def ToggleSetting(self, setting, sType):
        # setting = -setting  ???
        pass