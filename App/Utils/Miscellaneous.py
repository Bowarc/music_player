from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QFileDialog

import os
import sys

from moviepy.editor import AudioFileClip

from App.Uis.UI_Loader import PLAYLIST


class Misc(QObject):
    msgSignal = pyqtSignal(dict)

    def __init__(self):
        QObject.__init__(self)
        self.songPath = sys.path[0]+f"\\User\\{PLAYLIST}"

        self.converTask = {
            "fileName": "",
        }

    def RenameFile(self, newFileName):
        fileName = self.converTask["fileName"]
        if not fileName.endswith(".mp3"):
            self.msgSignal.emit(
                {"Type": str("RenameError"), "Msg": "Please select a music file"})
            return
        if len(newFileName) < 1:
            self.msgSignal.emit({"Type": str(
                "RenameError"), "Msg": "Please select a new name for the selected file"})
            return
        if not newFileName.endswith(".mp3"):
            newFileName += ".mp3"
        self.msgSignal.emit({"Type": str("RInfo"), "Msg": str("rename start")})
        try:
            os.rename(f"{self.songPath}\\{fileName}", f"{self.songPath}\\{newFileName}")
        except Exception as e:
            self.msgSignal.emit({"Type": str("RenameError"), "Msg": e})
            return
        self.msgSignal.emit({"Type": str("RInfo"), "Msg": str("rename end")})

    def convertFile(self):
        filePath = QFileDialog.getOpenFileName(
            None, "Open a file", self.songPath)[0]
        FileName = ""
        index = 0
        for i in reversed(filePath):
            index += 1
            if i == "/":
                _fileName = filePath[-index+1:]
                break

        self.msgSignal.emit(
            {"Type": str("CInfo"), "Msg": str("convert start")})
        try:
            AudioFileClip(os.path.join(f"{filePath}")).write_audiofile(os.path.join(f"{self.songPath}\\", f"{_fileName}"))
        except Exception as e:
            self.msgSignal.emit({"Type": str("CError"), "Msg": str(f"{str(e).replace('ERROR', 'Error')}")})
            self.msgSignal.emit(
                {"Type": str("CStop"), "Msg": str("Close the thread")})
            print(e)
            return
        self.msgSignal.emit({"Type": str("CInfo"), "Msg": str("convert end")})

    def DeleteSong(self):
        path = QFileDialog.getOpenFileName(
            None, "Open a file", self.songPath)[0]
        self.msgSignal.emit({"Type": str("DInfo"), "Msg": "Starting Delete"})
        if ".mp3" in path:
            pass
        else:
            self.msgSignal.emit(
                {"Type": str("DError"), "Msg": "Please select a song."})
            return
        if self.songPath in path.replace("/", "\\"):
            pass
        else:
            self.msgSignal.emit(
                {"Type": str("DError"), "Msg": "Please select a song from app"})
            return
        try:
            os.remove(path)
        except Exception as e:
            self.msgSignal.emit({"Type": str("DError"), "Msg": e})
            return

        self.msgSignal.emit({"Type": str("DInfo"), "Msg": f"removed file {path}"})

    def selectFilePath(self, label=None):
        path = QFileDialog.getOpenFileName(
            None, "Open a file", self.songPath)[0]
        _path = ""
        _fileName = ""

        print(path)
        index = 0
        for i in reversed(path):
            index += 1
            if i == "/":
                _fileName = path[-index+1:]
                break

        print(_fileName)
        self.converTask["fileName"] = _fileName
        folderList = []
        temp = ""
        for letter in path:
            if letter == "/":
                temp += "/"
            else:
                temp += letter
            if letter == "/":
                folderList.append(temp)
                temp = ""

        if label:
            label.setText(str(_fileName).replace(".mp3", ""))
