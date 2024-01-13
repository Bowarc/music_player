from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSignal, QObject

from mutagen.mp3 import MP3
import pygame
import pygame._sdl2 as sdl2

from time import time as tmtime
from time import sleep as tmsleep

import sys
import os

from App.Uis.UI_Loader import PLAYLIST


DEFAULT_AUDIO_OUTPUT = "SteelSeries Sonar - Media (SteelSeries Sonar Virtual Audio Device)"


def print_audio_devices():
    is_capture = 0  # zero to request playback devices, non-zero to request recording devices
    num = sdl2.get_num_audio_devices(is_capture)
    names = [str(sdl2.get_audio_device_name(i, is_capture),
                 encoding="utf-8") for i in range(num)]
    print("\n".join(names))


class MusicPlayer(QObject):
    msgSignal = pyqtSignal(dict)

    def __init__(self):
        QObject.__init__(self)
        pygame.init()

        # VARS
        self.PlayingIndex = 0
        self.songPlaying = ""

        self.IsPaused = True
        self.Run = True

        # VARS
        # OBJECTS

        self.Mixer = pygame.mixer
        self.Mixer.init()
        print_audio_devices()

        pygame.mixer.pre_init(devicename=DEFAULT_AUDIO_OUTPUT)
        self.Mixer.init()

        # OBJECTS

        # FUNCTIONS
        # {"Thread": "Music_player", "Type": str(""), "Msg":str("")}

    def Play(self, file):
        self.msgSignal.emit({"Type": str("MusicStart"), "Msg": str(f"{file}")})
        # self.Mixer.music.load(f"{sys.path[0]}\\User\\Songs\\{file}.mp3")
        self.Mixer.music.load(f"{sys.path[0]}\\User\\{PLAYLIST}\\{file}.mp3")
        self.Mixer.music.play()
        self.IsPaused = False

        # self.ui.ThreadEventList.append({"Thread": "Music_player", "Type": "Music_Change", "Msg":f"{file}"})
        # self.ui.ThreadEventList.append({"Thread": "Music_player", "Type": "ChangeSelectedSong", "Msg": f"{file}"})
        # print("Music player, play func is playing:",file)

        self.songPlaying = file
        self.msgSignal.emit(
            {"Type": str("MaxUpdate"), "Msg": self.GetActualSongLength(file)})

        # print((songLength - pygame.mixer.music.get_pos())*-1)

    def PauseUnpause(self):
        if not self.IsPaused:
            self.Pause()
        else:
            self.Unpause()

    def Pause(self):
        self.Mixer.music.pause()
        self.IsPaused = True
        self.msgSignal.emit({"Type": str("Pause"), "Msg": ""})

    def Unpause(self):
        self.Mixer.music.unpause()
        self.IsPaused = False
        self.msgSignal.emit({"Type": str("Unpause"), "Msg": ""})

    def ChangeVolume(self, volume):
        self.Mixer.music.set_volume(volume)
        self.msgSignal.emit({"Type": str("VolumeChanged"), "Msg": f"{volume}"})

    def isbusy(self):
        return self.Mixer.music.get_busy()

    def getPos(self):
        # print(a,len(str(a)),str(a))
        return self.Mixer.music.get_pos()

    def GetActualSongLength(self, song):
        # ms
        return int(MP3(f"{sys.path[0]}\\User\\{PLAYLIST}\\{song}.mp3").info.length)

    def WhilePlayingLoop(self):
        # for i in range(10):
        #     print(f"Music thread run {i}")
        #     tmsleep(0.3)

        lastTime = tmtime()
        while self.Run:
            self.msgSignal.emit(
                {"Type": str("TimeUpdate"), "Msg": self.getPos()/1000})
            # print(str(self.getPos()/1000))
            # CAN AND WILL BE REFORGE TO AN AUTO DETECTION VIA THE MUSIC TIME QSLIDER REACHING 100%
            if str(self.getPos()) == "-1" and not self.IsPaused:
                lastTime = tmtime()
                self.msgSignal.emit({"Type": str("MusicEnded"), "Msg": ""})
            tmsleep(0.01)
        self.msgSignal.emit(
            {"Type": str("Stop"), "Value": int(0), "Msg": str("Close the thread")})
        self.stop()

    def stop(self):
        self.Mixer.music.stop()
