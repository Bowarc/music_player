from PyQt5.QtCore import (
    Qt, QCoreApplication, QRect,
    pyqtSignal, QThread, pyqtSlot,
    QFile, QTextStream, QIODevice,
    QMetaObject, QTimer, QEvent
)
from PyQt5.QtGui import (
    QPixmap, QFont, QColor,
    QPainter, QIcon
)
from PyQt5.QtWidgets import (
    QWidget, QSplashScreen, QLabel,
    QLCDNumber, QTabWidget, QPushButton,
    QSlider, QListWidget, QListView, QTextEdit,
    QLineEdit, QListWidgetItem, QScrollBar, QApplication,
    QFileDialog, QStyle, QSystemTrayIcon, QAction, qApp, QMenu
)

from time import sleep as tmsleep
from time import time as tmtime

import time

from App.Uis.SplashScreens import LoadingSplash as SplshLoad
import App.Libs.HHour as HHour

from random import randint

import sys
import os

# from AppFiles.UI_Loader import Main_UI

PLAYLIST = "songs"


class Main_UI(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        # VARS
        self.setWindowFlags(Qt.Widget | Qt.FramelessWindowHint)
        # self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.clicked = False
        self.DraggableTopBorder = 33
        self.WinWdth = 800
        self.WinHght = 600 + self.DraggableTopBorder

        self.hidded = False

        # VARS
        # OBJECTS

        self.RezPath = None
        self.SettingsHandler = None

        # self.QssHandler = None
        self.Downloader = None
        self.DownloaderThread = None

        self.MusicPlayer = None
        self.MusicPlayerThread = None

        self.misc = None
        self.miscConverterThread = None

        self.settings = None

        self.trayIcon = None
        # OBJECTS
        # FUNCTIONS

        self.InitSplash()

        # self.retranslateUi()

        # FUNCTIONS

    def LoadDependecies(self):
        from App.Utils.Util_Methods import ResourcePath as RezPth
        self.Splash.UpdateLoadingBar()

        self.RezPath = RezPth()
        self.Splash.UpdateLoadingBar()

        self.systemSetup()
        self.Splash.UpdateLoadingBar()

        import App.Utils.Downloader as Dler
        self.Splash.UpdateLoadingBar()

        self.Downloader = Dler.Downloader()
        self.Splash.UpdateLoadingBar()

        self.Downloader.msgSignal.connect(self.DL_ThreadHande)
        self.Splash.UpdateLoadingBar()

        import App.Utils.MusicPlayer as MPlayer
        self.Splash.UpdateLoadingBar()

        self.MusicPlayer = MPlayer.MusicPlayer()
        self.Splash.UpdateLoadingBar()

        self.MusicPlayer.msgSignal.connect(self.Music_ThreadHande)
        self.Splash.UpdateLoadingBar()

        import App.Utils.Miscellaneous as Misc
        self.Splash.UpdateLoadingBar()

        self.misc = Misc.Misc()
        self.Splash.UpdateLoadingBar()

        self.misc.msgSignal.connect(self.misc_TreadHandle)
        self.Splash.UpdateLoadingBar()

        import App.Utils.ParametersHandler as ParamH
        self.Splash.UpdateLoadingBar()

        self.settings = ParamH.settings()
        self.Splash.UpdateLoadingBar()

        self.InitUi()
        self.Splash.UpdateLoadingBar()

        self.setupUI()
        self.Splash.UpdateLoadingBar()

        self.Create_TabWidgets()
        self.Splash.UpdateLoadingBar()

        self.LoadSongs()
        self.Splash.UpdateLoadingBar()

        self.applyQss("MainUI")
        self.Splash.UpdateLoadingBar()

        self.CreateThread("Downloader")
        self.Splash.UpdateLoadingBar()

        self.CreateThread("MusicPlayer")
        self.Splash.UpdateLoadingBar()

        self.CreateThread("Converter")
        self.Splash.UpdateLoadingBar()

        self.Create_timer()
        self.Splash.UpdateLoadingBar()

        self.StartThread("MusicPlayer")
        self.Splash.UpdateLoadingBar()

    def InitSplash(self):
        self.Splash = SplshLoad()
        self.Splash.ShowLoad()

        Time1 = tmtime()
        self.LoadDependecies()
        print(f"Dependecies load took {round(tmtime()-Time1,3)}s")
        self.Splash.DoneSplash(self)

    def InitUi(self):
        self.setFixedSize(self.WinWdth, self.WinHght+3)
        self.move((1920 / 2) - (self.WinWdth / 2),
                  (1080/2) - (self.WinHght / 2))

    def systemSetup(self):
        self.trayIcon = QSystemTrayIcon(self)
        icon = QIcon(self.RezPath.GetImage("appicon.ico"))
        self.trayIcon.setIcon(icon)
        self.setWindowIcon(icon)
        # self.trayIcon.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))

        '''
            Define and add steps to work with the system tray icon
            show - show window
            hide - hide window
            exit - exit from application
        '''

        playPause_action = QAction("Play / Pause", self)
        showHide_action = QAction("Show / Hide", self)
        quit_action = QAction("Exit", self)

        playPause_action.triggered.connect(self.PlayPauseUnpause)
        showHide_action.triggered.connect(self.showhide)
        quit_action.triggered.connect(self.close)

        tray_menu = QMenu()
        tray_menu.setLayoutDirection(Qt.RightToLeft)

        tray_menu.addAction(playPause_action)
        tray_menu.addAction(showHide_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        # self.trayIcon.activated.connect(self.showhide)
        self.trayIcon.setContextMenu(tray_menu)
        self.trayIcon.show()
        tray_menu.setStyleSheet("""
            QMenu{
                color: transparent;
                /*background-color: rgba(20,20,70,1);*/
                background-color: qlineargradient( /*transparent*/
                      x0:1 y0:1,
                      x1:0 y1:1,
                      stop:1 rgba(20,20,70,1),
                      stop:0.55 rgba(20,20,70,1), 
                      stop:0.45 rgba(20,20,70,1), 
                      stop:0 rgba(20,20,40,1));

            }
            QMenu::item{
                color: rgb(50,50,200);
            }
            QMenu::item::selected{
                /*color: rgb(0,0,150);*/
                color: white;
                background-color: transparent;
            }
            QMenu::separator{
                /*width: 5 px;*/
                
            }
            """)

    def setupUI(self):
        self.LCD_Clock = QLCDNumber(self)
        self.LCD_Clock.setSegmentStyle(QLCDNumber.Flat)
        self.LCD_Clock.setDigitCount(6)
        self.LCD_Clock.setGeometry(
            QRect(660, 0, 100, self.DraggableTopBorder-2))
        # self.LCD_Clock.setGeometry(QRect(self.WinWdth-100, self.DraggableTopBorder, 100, self.DraggableTopBorder-2))

        self.Quit_Button = QPushButton(self)
        self.Quit_Button.setGeometry(QRect(self.WinWdth-30, -10, 40, 40))
        self.Quit_Button.setObjectName("Quit_Button")
        self.Quit_Button.clicked.connect(self.showhide)
        # self.Quit_Button.clicked.connect(lambda: self.close())

        self.Quit_Label = QLabel(self)
        self.Quit_Label.setGeometry(QRect(self.WinWdth-19, 4, 15, 15))
        self.Quit_Label.setPixmap(self.CreatePixMap(
            "close2.png", self.Quit_Label.width(), self.Quit_Label.height()))
        self.Quit_Label.setObjectName("Quit_Label")

        # self.BackgroundLabel = QLabel(self)
        # self.BackgroundLabel.setGeometry(QRect(0, self.DraggableTopBorder, 800, 600))
        # # self.BackgroundLabel.setPixmap(self.CreatePixMap("Back-Black",800, 600))
        # self.BackgroundLabel.setObjectName("Background")

    def Create_timer(self):
        self.LCD_Timer = QTimer(self)
        self.LCD_Timer.timeout.connect(lambda: self.LCD_Clock.display((f"{HHour.HeureOnly()}H {HHour.MinutesOnly()}")))
        self.LCD_Timer.start(10)

    def Create_TabWidgets(self):
        self.tabWidget = QTabWidget(self)
        self.tabWidget.setObjectName("Window_TabWidget")

        self.tabWidget.tabBar().setObjectName("Window_TabWidget_TabBar")

        self.tabWidget.setGeometry(
            QRect(0, self.DraggableTopBorder, self.WinWdth, self.WinHght))

        self.CreatePlayerTab()
        self.tabWidget.addTab(self.playerTab, "Player")

        self.createDownloaderTab()
        self.tabWidget.addTab(self.downloaderTab, "Downloader")

        self.createPlaylistCreatorTab()
        self.tabWidget.addTab(self.playlistCreatorTab, "Playlist creator")

        self.createMiscTab()
        self.tabWidget.addTab(self.miscTab, "Miscellaneous")

        self.createSettingsTab()
        self.tabWidget.addTab(self.settingsTab, "Settings")

        self.LCD_Clock.raise_()
        self.Quit_Label.raise_()
        self.Quit_Button.raise_()

        self.tabWidget.setCurrentIndex(0)

    def CreatePlayerTab(self):  # Music Player
        self.playerTab = QWidget()

        self.Start_Stop_Button = QPushButton("Pause", self.playerTab)
        self.Start_Stop_Button.setGeometry(
            QRect(360, 490, self.WinWdth-(360*2), 23))
        self.Start_Stop_Button.clicked.connect(self.PlayPauseUnpause)

        self.Next_button = QPushButton("Next", self.playerTab)
        self.Next_button.setGeometry(
            QRect(360 + self.WinWdth-(360*2) + 15, 490, 30, 23))
        self.Next_button.clicked.connect(lambda: self.PlayNext(How="Button"))

        self.Back_button = QPushButton("Prev.", self.playerTab)
        self.Back_button.setGeometry(QRect(360 - 30 - 15, 490, 30, 23))
        self.Back_button.clicked.connect(self.PlayPrevious)

        self.Music_time_label = QLabel("Label", self.playerTab)
        self.Music_time_label.setGeometry(QRect(320+160+5, 530, 35, 22))

        self.SongTimeSlider = QSlider(self.playerTab)
        self.SongTimeSlider.setGeometry(
            QRect(320, 530, self.WinWdth-(320*2), 22))
        self.SongTimeSlider.setOrientation(Qt.Horizontal)
        self.SongTimeSlider.setEnabled(False)
        self.SongTimeSlider.setObjectName("MusicTimeSlider")

        self.Music_time_played_label = QLabel("0", self.playerTab)
        self.Music_time_played_label.setGeometry(QRect(280, 530, 35, 22))

        self.Play_playlist_label = QLabel(self.playerTab)
        self.Play_playlist_label.setGeometry(QRect(190, 90, 50, 50))
        self.Play_playlist_label.setPixmap(self.CreatePixMap(
            "play.png", self.Play_playlist_label.height(), self.Play_playlist_label.height()))
        self.Play_playlist_button = QPushButton(self.playerTab)
        self.Play_playlist_button.setGeometry(QRect(190, 90, 50, 50))
        self.Play_playlist_button.clicked.connect(self.PlayPauseUnpause)

        self.MusicPlayingTitle = QLabel("Label", self.playerTab)
        self.MusicPlayingTitle.setGeometry(
            QRect(200, 460, self.WinWdth-(200*2), 20))
        self.MusicPlayingTitle.setAlignment(Qt.AlignCenter)

        self.VolumeLabel = QLabel("Volume", self.playerTab)
        self.VolumeLabel.setGeometry(QRect(670, 470, 60, 30))

        self.VolumeValueLabel = QLabel(self.playerTab)  # QLabel
        self.VolumeValueLabel.setGeometry(760, 500, 40, 20)

        self.styleLabel = QLabel(self.playerTab)
        self.styleLabel.setGeometry(QRect(650, 500, 95, 22))
        self.styleLabel.setObjectName("VolumeSlideStyleLabel")

        self.VolumeSlider = QSlider(self.playerTab)
        self.VolumeSlider.setGeometry(QRect(650, 500, 100, 22))
        self.VolumeSlider.setOrientation(Qt.Horizontal)
        self.VolumeSlider.valueChanged.connect(
            lambda: self.MusicPlayer.ChangeVolume(self.VolumeSlider.value()/100))
        self.VolumeSlider.setValue(20)
        self.VolumeSlider.setMinimum(0)
        self.VolumeSlider.setMaximum(100)
        self.VolumeSlider.setObjectName("VolumeSlider")

        self.songListWidget = QListWidget(self.playerTab)
        self.songListWidget.setGeometry(
            QRect(150, 150, self.WinWdth-(150*2), 300))
        self.songListWidget.setMovement(QListView.Static)
        self.songListWidget.setFlow(QListView.TopToBottom)
        self.songListWidget.setViewMode(QListView.ListMode)
        self.songListWidget.setItemAlignment(Qt.AlignLeft)  # AlignCenter
        self.songListWidget.setObjectName("PlayerSongList")
        self.songListWidget.verticalScrollBar().setObjectName(
            "PlayerSongList_VerticalScrollBar")
        self.songListWidget.currentItemChanged.connect(
            self.changePlayPauseLabelPixmap)

    def createDownloaderTab(self):  # Downloader

        self.downloaderTab = QWidget()

        self.Console_text_edit = QTextEdit(self.downloaderTab)
        self.Console_text_edit.setGeometry(QRect(10, 320, 401, 241))
        self.Console_text_edit.setReadOnly(True)
        self.Console_text_edit.setObjectName("DownloaderConsole")
        self.Console_text_edit.verticalScrollBar().setObjectName(
            "DownloaderConsole_VerticalScrollBar")

        self.clearConsoleButton = QPushButton("Clear", self.downloaderTab)
        self.clearConsoleButton.setGeometry(QRect(411, 521, 70, 40))
        self.clearConsoleButton.clicked.connect(
            lambda: self.clearConsole(console="Downloader"))

        self.link_lineEdit = QLineEdit(self.downloaderTab)
        self.link_lineEdit.setGeometry(QRect(70, 240, 271, 20))
        self.link_lineEdit.setObjectName("Downloader_LinkLineEdit")

        self.Link_label = QLabel("Link: ", self.downloaderTab)
        self.Link_label.setGeometry(QRect(15, 240, 35, 20))
        self.Link_label.setObjectName("Downloader_LinkLabel")

        self.NameLineEdit = QLineEdit(self.downloaderTab)
        self.NameLineEdit.setGeometry(QRect(70, 280, 270, 20))

        self.Name_label = QLabel("Title: ", self.downloaderTab)
        self.Name_label.setGeometry(QRect(15, 280, 35, 20))
        self.Name_label.setObjectName("Downloader_NameLabel")

        self.Download_pushButton = QPushButton("Download", self.downloaderTab)
        self.Download_pushButton.setGeometry(QRect(450, 310, 141, 61))
        self.Download_pushButton.clicked.connect(
            lambda: self.StartThread("Downloader"))
        self.Download_pushButton.setObjectName("Downloader_DLButton")

        self.Downloader_title_label = QLabel("Downloader", self.downloaderTab)
        self.Downloader_title_label.setGeometry(QRect(0, 0, self.WinWdth, 200))
        self.Downloader_title_label.setAlignment(Qt.AlignCenter)
        self.Downloader_title_label.setObjectName("Downloader_titleLabel")

    def createPlaylistCreatorTab(self):  # Playlist Creation

        self.playlistCreatorTab = QWidget()

        TodoLabel = QLabel(self.playlistCreatorTab)
        TodoLabel.setGeometry(QRect(0, 0, self.WinWdth, self.WinHght-33-21))
        TodoLabel.setFont(QFont("", 80))
        TodoLabel.setText("Not Done Yet")
        TodoLabel.setAlignment(Qt.AlignCenter)

    def createMiscTab(self):
        self.miscTab = QWidget()

        #            #
        #   RENAME   #
        #            #
        self.renameSectionTitleLabel = QLabel("Rename", self.miscTab)
        self.renameSectionTitleLabel.setGeometry(
            QRect(0, 46, self.WinWdth/2, 40))
        self.renameSectionTitleLabel.setAlignment(Qt.AlignCenter)
        self.renameSectionTitleLabel.setObjectName("misc_RenameTitleLabel")

        self.renameSelectFileLabel = QLabel(". . .", self.miscTab)
        self.renameSelectFileLabel.setGeometry(120, 150, 250, 30)
        self.renameSelectFileLabel.setAlignment(Qt.AlignCenter)

        self.renameSelectFileButton = QPushButton(
            "Select a song", self.miscTab)
        self.renameSelectFileButton.setGeometry(
            QRect(10, 150, self.WinWdth/2 - (150*2), 30))
        self.renameSelectFileButton.clicked.connect(
            lambda: self.misc.selectFilePath(label=self.renameSelectFileLabel))

        self.renameSelectNameLabel = QLabel("New name:", self.miscTab)
        self.renameSelectNameLabel.setGeometry(
            QRect(10, 200, self.WinWdth/2 - (150*2), 30))
        self.renameSelectNameLabel.setAlignment(Qt.AlignCenter)

        self.renameSelectNameLineEdit = QLineEdit(self.miscTab)
        self.renameSelectNameLineEdit.setGeometry(120, 200, 250, 30)
        self.renameSelectNameLineEdit.setAlignment(Qt.AlignCenter)

        self.renamePushButton = QPushButton("Rename", self.miscTab)
        self.renamePushButton.setGeometry(
            QRect(50, 250, self.WinWdth/2 - (50*2), 50))
        self.renamePushButton.clicked.connect(
            lambda: self.misc.RenameFile(self.renameSelectNameLineEdit.text()))

        #             #
        #   CONVERT   #
        #             #

        self.convertSectionTitleLabel = QLabel("Convert", self.miscTab)
        self.convertSectionTitleLabel.setGeometry(
            QRect((self.WinWdth/4)*3 - 50, 46, 100, 40))
        self.convertSectionTitleLabel.setAlignment(Qt.AlignCenter)
        self.convertSectionTitleLabel.setObjectName("misc_ConvertTitleLabel")

        self.converterPushButton = QPushButton("Convert a file", self.miscTab)
        self.converterPushButton.setGeometry(
            QRect((self.WinWdth/4)*3-(200/2), 375/2 - 35, 200, 70))
        self.converterPushButton.clicked.connect(
            lambda: self.StartThread("Converter"))

        #            #
        #   DELETE   #
        #            #

        self.deleteSectionTitleLabel = QLabel("Delete a song", self.miscTab)
        self.deleteSectionTitleLabel.setGeometry(
            QRect((self.WinWdth/4)*1 - (200/2), (580/4)*3-35 - 70, 200, 40))
        self.deleteSectionTitleLabel.setAlignment(Qt.AlignCenter)
        self.deleteSectionTitleLabel.setObjectName("misc_DeleteTitleLabel")

        self.deletePushButton = QPushButton("Delete a song", self.miscTab)
        self.deletePushButton.setGeometry(
            QRect((self.WinWdth/4)*1-(200/2), (580/4)*3-35, 200, 70))
        self.deletePushButton.clicked.connect(lambda: self.misc.DeleteSong())

        #            #
        #   GLOBAL   #
        #            #
        self.miscGlobalConsole = QTextEdit(self.miscTab)
        self.miscGlobalConsole.setGeometry(QRect(
            self.WinWdth/2, (self.WinHght - self.DraggableTopBorder) - 275, self.WinWdth - self.WinWdth/2, 250))
        self.miscGlobalConsole.setReadOnly(True)
        self.miscGlobalConsole.setObjectName("misc_globalConsole")
        self.miscGlobalConsole.verticalScrollBar().setObjectName(
            "misc_globalConsole_verticalScrollBar")

    def createSettingsTab(self):  # Settings
        self.settingsTab = QWidget()

        self.settingsGlobalParamTitleLabel = QLabel(
            "Gobal Settings", self.settingsTab)
        self.settingsGlobalParamTitleLabel.setGeometry(
            QRect(0, 46, self.WinWdth/2, 40))
        self.settingsGlobalParamTitleLabel.setAlignment(Qt.AlignCenter)
        self.settingsGlobalParamTitleLabel.setObjectName(
            "Settings_GlobalParamTitleLabel")

        # TodoLabel = QLabel(self.settingsTab)
        # TodoLabel.setGeometry(QRect(0, 0, self.WinWdth, self.WinHght-33-21))
        # TodoLabel.setFont(QFont("", 80))
        # TodoLabel.setText("Not Done Yet")
        # TodoLabel.setAlignment(Qt.AlignCenter)

    def closeEvent(self, event):
        # print("[INFO] BarWindow CloseEvent Called")
        if self.DownloaderThread.isRunning():
            self.CloseThreads("Downloader")
        if self.MusicPlayerThread.isRunning():
            self.CloseThreads("MusicPlayer")
        if self.MusicPlayerThread.isRunning():
            self.CloseThreads("Converter")
        self.close()

    def showhide(self):
        if not self.hidded:
            self.hide()
            self.hidded = True
        else:
            self.show()
            self.hidded = False

    def paintEvent(self, e):
        q = QPainter(self)  # Painting the line
        # q.begin(self)
        pixmap = self.CreatePixMap("Back-Black", self.WinWdth, self.WinHght)
        q.drawPixmap(self.rect(), pixmap)
        q.setPen(QColor(255, 255, 255))

        q.drawLine(0, self.DraggableTopBorder-2,
                   self.WinWdth, self.DraggableTopBorder-2)
        # print(self.settingsTab.text())
        if self.tabWidget.currentIndex() == self.tabWidget.indexOf(self.settingsTab):
            q.drawLine(self.WinWdth/2, 100, self.WinWdth/2, self.WinHght)
            r = 3
            offset = (self.WinHght-100)/r
            for i in range(r):
                ioffset = offset * (i+1)
                q.drawLine(self.WinWdth/2, 100 + ioffset,
                           self.WinWdth, 100 + ioffset)
        if self.tabWidget.currentIndex() == self.tabWidget.indexOf(self.miscTab):
            q.drawLine(self.WinWdth/2, 100, self.WinWdth /
                       2, self.miscGlobalConsole.y() + 50)
            q.drawLine(0, self.miscGlobalConsole.y() + 50,
                       self.WinWdth/2, self.miscGlobalConsole.y() + 50)
        q.end()

    def CloseThreads(self, Thread=None):
        if Thread == "Downloader":
            T = self.DownloaderThread
            self.consoleAppend(color=(255, 200, 0), fontSize=13, text=f"Closing downloader thread,\nthis may cause a little lag.", console="Downloader")
            print("Close DL Thread")
        elif Thread == "MusicPlayer":
            T = self.MusicPlayerThread
            self.MusicPlayer.Run = False
            print("Close Music Thread")
        elif Thread == "Converter":
            T = self.miscConverterThread
            self.consoleAppend(color=(255, 200, 0), fontSize=13, text=f"Closing converter thread,\nthis may cause a little lag.", console="Misc")
            print("Close Converter Thread")

        if not T:
            return 0

        t1 = tmtime()
        while T.isRunning():
            T.quit()
            T.wait()
            tmsleep(0.2)
            if tmtime()-t1 > 5:
                print(f"Stuck in {Thread} thread stopping method")

        print(f"The {Thread} thread has been stopped")
        # self.Download_pushButton.setEnabled(True)

    def CreateThread(self, Thread):
        if Thread == "Downloader":
            self.DownloaderThread = QThread()
            self.Downloader.moveToThread(self.DownloaderThread)
            self.DownloaderThread.started.connect(
                self.Downloader.DownloadHandler)  # self.Downloader.DownloadHandler
            if self.DownloaderThread:
                self.clearConsole(console="Downloader")

        elif Thread == "MusicPlayer":
            self.MusicPlayerThread = QThread()
            self.MusicPlayer.moveToThread(self.MusicPlayerThread)
            self.MusicPlayerThread.started.connect(
                self.MusicPlayer.WhilePlayingLoop)

        elif Thread == "Converter":
            self.miscConverterThread = QThread()
            self.misc.moveToThread(self.miscConverterThread)
            self.miscConverterThread.started.connect(self.misc.convertFile)

    def StartThread(self, ThreadName):
        if ThreadName == "Downloader" and not self.DownloaderThread.isRunning():
            self.Downloader.DL_args = {
                "VideoLink": str(self.link_lineEdit.text()),
                "NewFileName": str(self.NameLineEdit.text()),
                "NoPlaylist": bool(True)
            }

            # self.Download_pushButton.setEnabled(False)
            print("starting dl thread")
            self.DownloaderThread.start()
            if self.DownloaderThread.isRunning():
                print("Thread started")
            else:
                print("Thread error: failed to start")

        elif ThreadName == "MusicPlayer" and not self.MusicPlayerThread.isRunning():
            song = self.songListWidget.item(0).text()
            self.songListWidget.setCurrentRow(0)
            self.MusicPlayer.PlayingIndex = 0
            self.MusicPlayer.Play(song)
            self.MusicPlayer.Pause()
            self.MusicPlayer.Run = True
            print("Starting Music thread")
            self.MusicPlayerThread.start()
            if self.MusicPlayerThread.isRunning():
                print("Thread started")
            else:
                print("Thread error: failed to start")

        elif ThreadName == "Converter" and not self.miscConverterThread.isRunning():
            self.misc.converTask["filePath"] = self.renameSelectFileLabel.text().replace(
                '/', '\\')
            self.miscConverterThread.start()
            if self.miscConverterThread.isRunning():
                print("Thread started")
            else:
                print("Thread error: failed to start")

    def mousePressEvent(self, event):
        if 0 < event.screenPos().x()-self.pos().x() < self.WinWdth and 0 < event.screenPos().y()-self.pos().y() < self.DraggableTopBorder:
            self.clicked = True
        self.old_pos = event.screenPos()

    def mouseReleaseEvent(self, event):
        self.clicked = False

    def mouseMoveEvent(self, event):
        if self.clicked:
            dx = self.old_pos.x() - event.screenPos().x()
            dy = self.old_pos.y() - event.screenPos().y()
            self.move(self.pos().x() - dx, self.pos().y() - dy)

        self.old_pos = event.screenPos()
        # self.clicked = True
        return QWidget.mouseMoveEvent(self, event)

    def NotifMaker(self):
        pass

    def clearConsole(self, console="Downloader"):
        if console == "Downloader":
            self.Console_text_edit.clear()
            self.consoleAppend(color=(0, 200, 100), fontSize=17, text=f"Connected !", console="Downloader")
        elif console == "Misc":
            self.miscGlobalConsole.clear()

    def LoadSongs(self,):
        f = []
        f2 = []
        for (dirpath, dirnames, filenames) in os.walk(f"{sys.path[0]}/User/{PLAYLIST}"):
            f.extend(filenames)
            break

        for song in f:
            if song.endswith(".mp3"):
                f2.append(song.replace(".mp3", ""))

        self.songListWidget.clear()
        for song in f2:
            item = QListWidgetItem(song)
            item.setTextAlignment(Qt.AlignLeft)
            self.songListWidget.addItem(item)

        return f2

    def changePlayPauseLabelPixmap(self):
        try:
            if self.songListWidget.item(self.songListWidget.row(self.songListWidget.findItems(self.MusicPlayer.songPlaying, Qt.MatchExactly)[0])) == self.songListWidget.currentItem() and not self.MusicPlayer.IsPaused:
                self.Play_playlist_label.setPixmap(self.CreatePixMap(
                    "pause.png", self.Play_playlist_label.height(), self.Play_playlist_label.height()))
                self.Start_Stop_Button.setText("Pause")
            else:
                self.Play_playlist_label.setPixmap(self.CreatePixMap(
                    "play.png", self.Play_playlist_label.height(), self.Play_playlist_label.height()))
                self.Start_Stop_Button.setText("Play")
        except IndexError as e:
            self.Play_playlist_label.setPixmap(self.CreatePixMap(
                "play.png", self.Play_playlist_label.height(), self.Play_playlist_label.height()))
            self.Start_Stop_Button.setText("Play")

    def PlayPauseUnpause(self):
        try:
            if self.songListWidget.item(self.songListWidget.row(self.songListWidget.findItems(self.MusicPlayer.songPlaying, Qt.MatchExactly)[0])) != self.songListWidget.currentItem():
                try:
                    song = self.songListWidget.currentItem().text()
                    self.MusicPlayer.PlayingIndex = self.songListWidget.currentRow()
                except AttributeError as e:
                    song = self.songListWidget.item(0).text()
                    self.MusicPlayer.PlayingIndex = 0
                self.MusicPlayer.Play(song)
                self.MusicPlayer.Unpause()

            elif self.MusicPlayer.IsPaused and self.songListWidget.item(self.songListWidget.row(self.songListWidget.findItems(self.MusicPlayer.songPlaying, Qt.MatchExactly)[0])) == self.songListWidget.currentItem():
                self.MusicPlayer.Unpause()

            elif not self.MusicPlayer.IsPaused:
                self.MusicPlayer.Pause()
        except IndexError as e:
            song = self.songListWidget.item(0).text()
            self.MusicPlayer.PlayingIndex = 0
            self.songListWidget.setCurrentRow(0)
            self.MusicPlayer.Play(song)

    def PlayPrevious(self):
        self.MusicPlayer.Pause()
        if self.MusicPlayer.isbusy():
            self.MusicPlayer.stop()

        self.MusicPlayer.PlayingIndex -= 1

        if self.MusicPlayer.PlayingIndex < 0:
            self.MusicPlayer.PlayingIndex = self.songListWidget.count()-1
        self.songListWidget.setCurrentRow(self.MusicPlayer.PlayingIndex)

        self.MusicPlayer.Play(self.songListWidget.item(
            self.MusicPlayer.PlayingIndex).text())
        print("end of PlayPrevious")
        self.MusicPlayer.Unpause()

    def PlayNext(self, How="Not specified"):
        self.MusicPlayer.Pause()
        if self.MusicPlayer.isbusy():
            self.MusicPlayer.stop()

        self.MusicPlayer.PlayingIndex += 1

        if self.MusicPlayer.PlayingIndex > self.songListWidget.count()-1:
            self.MusicPlayer.PlayingIndex = 0
        self.songListWidget.setCurrentRow(self.MusicPlayer.PlayingIndex)

        self.MusicPlayer.Play(self.songListWidget.item(
            self.MusicPlayer.PlayingIndex).text())

        print("end of PlayNext")
        print(time.time())
        print(self.MusicPlayer.PlayingIndex, self.songListWidget.item(
            self.MusicPlayer.PlayingIndex).text())
        print(How)
        print("-------------------------------------------\n")
        self.MusicPlayer.Unpause()

    def consoleAppend(self, color=(255, 255, 255), fontSize=13, text="", console="Downloader"):
        if console == "Downloader":
            c = self.Console_text_edit
        elif console == "Misc":
            c = self.miscGlobalConsole
        c.setFontPointSize(fontSize)
        c.setTextColor(QColor(color[0], color[1], color[2]))
        # btw, using \n is possible in the text variable
        c.append("> {0}".format(text))

    def applyQss(self, QssFile):
        with open(self.RezPath.GetQss(f"{QssFile}.qss"), "r") as f:
            Content = f.read()

        self.setStyleSheet(Content)
        # QMetaObject.connectSlotsByName(self)
        self.songListWidget.horizontalScrollBar().setEnabled(False)

    def CreatePixMap(self, FileName, x=100, y=100):
        return QPixmap(self.RezPath.GetImage(FileName)).scaled(x, y)

    @pyqtSlot(dict)
    def DL_ThreadHande(self, msg):
        TookCare = False
        if msg["Type"] == "Info":
            if msg["Msg"] == "DL_Start":
                self.consoleAppend(color=(255, 200, 0), fontSize=13, text=f"Starting the download.", console="Downloader")
                TookCare = True
            elif msg["Msg"] == "DL_Ended":
                self.consoleAppend(color=(50, 200, 50), fontSize=13, text=f"Download ended.", console="Downloader")
                TookCare = True
            elif msg["Msg"] == "Conversion_Start":
                self.consoleAppend(color=(255, 200, 0), fontSize=13, text=f"Converting,\n> Please wait . . .", console="Downloader")
                TookCare = True
            elif msg["Msg"] == "Conversion_End":
                self.consoleAppend(color=(50, 200, 50), fontSize=13, text=f"Conversion ended.", console="Downloader")
                self.LoadSongs()
                self.SetPlayingMusicColoration(self.MusicPlayer.songPlaying)
                TookCare = True

        elif msg["Type"] == f"%Update":
            self.consoleAppend(color=(50, 200, 50), fontSize=13, text=f"{msg['Msg']}%", console="Downloader")
            TookCare = True
        elif msg["Type"] == "Error":
            self.consoleAppend(color=(200, 50, 50), fontSize=15, text=f"{msg['Msg']}", console="Downloader")
            TookCare = True
            # self.CloseThreads("Downloader")

        elif msg["Type"] == "Stop":
            self.CloseThreads("Downloader")
            TookCare = True

        # self.consoleAppend(color = (0,255,255), fontSize = 13, text = f"Song downloading, % = {event['Value']}")
    def SetPlayingMusicColoration(self, music):
        for i in range(self.songListWidget.count()):
            self.songListWidget.item(i).setForeground(QColor(255, 255, 255))
            self.songListWidget.item(i).setSelected(False)
        self.songListWidget.item(self.songListWidget.row(self.songListWidget.findItems(
            music, Qt.MatchExactly)[0])).setForeground(QColor(0, 200, 200))

    @pyqtSlot(dict)
    def Music_ThreadHande(self, msg):
        TookCare = False
        # raise ValueError('msg not handled here')
        if msg["Type"] == "MusicStart":

            self.SetPlayingMusicColoration(msg["Msg"])
            self.MusicPlayingTitle.setText(msg["Msg"])
            TookCare = True

        elif msg["Type"] == "MusicEnded":
            self.PlayNext(How="music Ended")
            TookCare = True

        elif msg["Type"] == "MaxUpdate":
            self.Music_time_label.setText(f"{int(msg['Msg'])}")
            self.SongTimeSlider.setMaximum(msg['Msg'])
            TookCare = True

        elif msg["Type"] == "TimeUpdate":
            self.SongTimeSlider.setValue(int(msg["Msg"]))
            # print(f"Max: {Max*100}\nActual: {Pos*100}")
            self.Music_time_played_label.setText(f"{round(msg['Msg'], 3)}")
            TookCare = True

        elif msg["Type"] == "Pause":  # Start_Stop_Button
            self.Play_playlist_label.setPixmap(self.CreatePixMap(
                "play.png", self.Play_playlist_label.height(), self.Play_playlist_label.height()))
            self.Start_Stop_Button.setText("Play")
            TookCare = True

        elif msg["Type"] == "Unpause":  # Start_Stop_Button
            self.Play_playlist_label.setPixmap(self.CreatePixMap(
                "pause.png", self.Play_playlist_label.height(), self.Play_playlist_label.height()))
            self.Start_Stop_Button.setText("Pause")
            TookCare = True

            # print("music text updated",f"Max: {Max*100}  Actual: {Pos*100}")
        elif msg["Type"] == "VolumeChanged":
            self.VolumeValueLabel.setText(str(int(float(msg["Msg"])*100)))
            TookCare = True

        elif msg["Type"] == "Stop":
            if self.MusicPlayerThread.isRunning():
                self.CloseThreads("MusicPlayer")
            TookCare = True

        if not TookCare:
            print(f"This message has not been handled: {msg}")

    @pyqtSlot(dict)
    def misc_TreadHandle(self, msg):
        TookCare = False
        if msg["Type"] == "RInfo":
            if msg["Msg"] == "rename start":
                self.consoleAppend(
                    color=(50, 200, 50), fontSize=15, text="Starting rename", console="Misc")
                TookCare = True
            elif msg["Msg"] == "rename end":
                self.consoleAppend(color=(50, 200, 50), fontSize=15,
                                   text="Rename ended without any error", console="Misc")
                self.LoadSongs()
                self.misc.converTask["newFileName"] = ""
                self.renameSelectFileLabel.setText("")
                self.renameSelectNameLineEdit.setText("")
                TookCare = True
        elif msg["Type"] == "RenameError":
            if str(msg["Msg"].__class__.__name__) == "FileNotFoundError":
                self.consoleAppend(color=(200, 50, 50), fontSize=15,
                                   text="An error occured,\n> Please re-select the file\n> [FileNotFoundError]", console="Misc")
                TookCare = True
            elif str(msg["Msg"]).startswith("[WinError 32]"):
                self.consoleAppend(color=(200, 200, 50), fontSize=15, text=f"Little Error:\nThe selected music was the one playing,\nLet me unload it and re-trying", console="Misc")
                self.MusicPlayer.Mixer.music.unload()
                self.misc.RenameFile(self.renameSelectNameLineEdit.text())
                TookCare = True
            else:
                self.consoleAppend(color=(200, 50, 50),
                                   fontSize=15, text=msg["Msg"], console="Misc")
                TookCare = True

        elif msg["Type"] == "CInfo":
            if msg["Msg"] == "convert start":
                self.consoleAppend(color=(50, 200, 50), fontSize=15,
                                   text="Starting conversion,\nPlease wait a bit.", console="Misc")

            elif msg["Msg"] == "convert end":
                self.consoleAppend(
                    color=(50, 200, 50), fontSize=15, text="Conversion ended.", console="Misc")
                if self.MusicPlayerThread.isRunning():
                    self.CloseThreads("Converter")
                self.LoadSongs()
                TookCare = True
        elif msg["Type"] == "CError":
            self.consoleAppend(color=(200, 50, 50), fontSize=15, text=f"{msg['Msg']}", console="Misc")
            TookCare = True
        elif msg["Type"] == "CStop":
            if self.MusicPlayerThread.isRunning():
                self.CloseThreads("Converter")
            TookCare = True

        elif msg["Type"] == "DInfo":
            if msg["Msg"] == "Starting Delete":
                self.consoleAppend(color=(50, 200, 50), fontSize=15,
                                   text="Starting delete,\nPlease wait a bit.", console="Misc")
            elif msg["Msg"].startswith("removed file "):
                self.consoleAppend(color=(50, 200, 50), fontSize=15, text=f"{msg['Msg']}", console="Misc")
                self.LoadSongs()
            TookCare = True
        elif msg["Type"] == "DError":
            if str(msg["Msg"]).startswith("[WinError 32]"):
                self.consoleAppend(color=(200, 200, 50), fontSize=15, text=f"Error:\nThe selected music was the one playing,\nLet me unload it,\nPlease retry", console="Misc")
                self.MusicPlayer.Mixer.music.unload()
            else:
                self.consoleAppend(color=(200, 50, 50), fontSize=15, text=f"{msg['Msg']}", console="Misc")
            TookCare = True

        if not TookCare:
            print(f"This message has not been handled: {msg}")


# TODO
#  Add a button to clear download console: self.Console_text_edit.clear()
# USE QSIGNAL FOR & INTERACTIONS

# MAKE IT PRETTY AND USEABLE, MAYBE SOME HARD CODED WINDOW SIZES


# IDEAS

# use the site: https://www.flaticon.com/

# to dl some sprite and use them on buttons, with the following line:

# button.setStyleSheet("""&ground-image : url(image.png);""")


# DARK CYAN(around this #008BEA) DESING FOR TEXTS,
# INTERATIVE STYLE SHEETS BUT NOT TOO MUCH

# IN Settings, ADD A WAY TO SWITCH STYLESHEETS
