# from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import (
    pyqtSignal, QObject
)

from moviepy.editor import AudioFileClip
import yt_dlp

from time import time as tmtime
from time import sleep as tmsleep

import sys
import os


from App.Uis.UI_Loader import PLAYLIST


class Downloader(QObject):
    msgSignal = pyqtSignal(dict)

    def __init__(self):
        QObject.__init__(self)
        # VARS

        self.LastDownloadTitle = ""
        self.DL_args = {
            "VideoLink": str(""),
            "NewFileName": str(""),
            "NoPlaylist": bool(True)
        }

        # VARS
        # SINGALS

        # {"Type": str(""), "Value" : int(0),"Msg": str("")}  # EXAMPLE

        # self.msgSignal.connect(self.ChangeHpBarMax) # IN THE UI

        # self.msgSignal.emit({"Type": str(""), "Value" : int(0),"Msg": str("")})  # Here

        # SINGALS

    def GetSongPath(self):
        path = sys.path[0]
        # print(path)
        if "App" in path:
            return f"{path.replace('App','')}User\\Temp"
        else:
            return "\\User\\Temp"

    def my_hook(self, d):
        # print(f"{sys.path[0]}\\userfiles\\songs\\temp\\")
        if d["status"] == "finished":
            self.LastDownloadTitle = d["filename"].replace(f"{sys.path[0]}\\User\\Temp\\", "")
            print("Ended")
            self.msgSignal.emit(
                {"Type": str("Info"), "Msg": str("DL_Ended")})

        if d["status"] == "downloading":
            print(d["_percent_str"])
            self.msgSignal.emit({"Type": str(f"%Update"), "Msg": float(d["_percent_str"].replace('%', '').replace(
                "\x1b[0;94m", "").replace("\x1b[0m", "").replace(" ", ""))})

    # , VideoLink:str(""), NewFileName:str(""), NoPlaylist:bool(True)
    def DownloadHandler(self):
        VideoLink = self.DL_args["VideoLink"]
        NewFileName = self.DL_args["NewFileName"]
        NoPlaylist = self.DL_args["NoPlaylist"]
        print(VideoLink, NewFileName, NoPlaylist)

        Temp_path = sys.path[0]+"\\User\\Temp"

        options = {
            "format": "bestaudio/best",
            'audioformat': "mp3",
            'quiet': True,
            "outtmpl": "{0}/%(title)s".format(Temp_path) + ".mp3",
            "progress_hooks": [self.my_hook],
            "noplaylist": NoPlaylist,
        }

        if VideoLink == "":
            self.msgSignal.emit({"Type": str("Error"), "Msg": str("NoLink")})
            self.msgSignal.emit(
                {"Type": str("Stop"), "Msg": str("Close the thread")})
            return 0

        try:
            self.msgSignal.emit(
                {"Type": str("Info"), "Msg": str("DL_Start")})
            self.Download(options, VideoLink)
            self.msgSignal.emit(
                {"Type": str("Info"), "Msg": str("Conversion_Start")})
            self.Convert2mp3(NewFileName)
            self.msgSignal.emit(
                {"Type": str("Info"), "Msg": str("Conversion_End")})
        except Exception as e:
            self.msgSignal.emit({"Type": str("Error"), "Msg": str(f"{str(e).replace('ERROR', 'Error')}")})
            self.msgSignal.emit(
                {"Type": str("Stop"), "Msg": str("Close the thread")})
            print(e)
            return
        self.msgSignal.emit(
            {"Type": str("Stop"), "Msg": str("Close the thread")})

    def Download(self, options, VideoLink):

        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([VideoLink])

    def Convert2mp3(self, NewFileName):
        PATH_temp = "User\\Temp\\"
        PATH_song = f"User\\{PLAYLIST}\\"
        FileName = self.LastDownloadTitle
        # appliquer une férification au renommage d'un fichier dl par le yt-dl
        # (ici)
        if len(NewFileName) > 65:
            self.msgSignal.emit({"Type": str("Error"), "Msg": f"The lengh of the new name is not acceptable, i'll use the default: \n'{FileName}'"})
            NewFileName = FileName.replace(".mp3", "")

        if NewFileName == "":
            print(f"no name for the new file, i'll use: {FileName}")
            NewFileName = FileName.replace(".mp3", "")

        print(f"1st file name: {FileName}\n2nd file name: {NewFileName}")

        AudioFileClip(os.path.join(PATH_temp, f"{FileName}")).write_audiofile(os.path.join(PATH_song, f"{NewFileName}.mp3"))

        os.remove(f"{PATH_temp}{FileName}")
