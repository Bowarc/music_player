from PyQt5.QtCore    import (
    Qt, QCoreApplication,
    QTimer, QRect
)
from PyQt5.QtGui     import (
    QPixmap
)
from PyQt5.QtWidgets import (
    QSplashScreen, QLabel, QProgressBar
)

from App.Utils.Util_Methods import ResourcePath as RezPth

class LoadingSplash(QSplashScreen):
    def __init__(self):
        QSplashScreen.__init__(self)
        self.clicked = False
        self.RezPath = RezPth()
        ImagePath = self.RezPath.GetImage('Back-Black.jpg')
        
        SplashPix = QPixmap(ImagePath)
        SplashPix = SplashPix.scaled(300, 100)
        self.Splash = QSplashScreen(SplashPix) # Qt.WindowStaysOnTopHint
        # self.Splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.Splash.setEnabled(True)

        self.lMax = 24
        self.lState = 0

        self.pg = QProgressBar(self.Splash)
        self.pg.setGeometry(QRect(50,70,200,20))
        self.pg.setValue(0)
        self.pg.setMaximum(self.lMax)

        with open(self.RezPath.GetQss("Splash.qss"), "r") as f:
            Content = f.read()
        self.Splash.setStyleSheet(Content)

    def ShowLoad(self):
        self.Splash.show()
        self.Splash.showMessage("<h1><font color='white'>Loading . . .</font></h1>", (Qt.AlignHCenter | Qt.AlignVCenter))
        QCoreApplication.processEvents()

    def DoneSplash(self, NextWindow):
        self.Splash.finish(NextWindow)

    def UpdateLoadingBar(self):
        self.lState += 1
        self.pg.setValue(self.lState)
        QCoreApplication.processEvents()
        print(f"Loading: {int((self.lState / self.lMax) *100)}%")


