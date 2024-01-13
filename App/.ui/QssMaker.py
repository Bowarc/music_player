# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'QssMaker.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
import sys


class Ui_QssMakerWindow(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setupUi()
        self.retranslateUi()

    def setupUi(self):
        self.setObjectName("QssMakerWindow")
        self.resize(400, 300)

        self.gridLayoutWidget = QtWidgets.QWidget(self)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(0, 0, 401, 301))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")

        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)

        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.gridLayout.setContentsMargins(5, 0, 0, 0)

        self.Qss = QtWidgets.QTextEdit(self.gridLayoutWidget)
        self.Qss.setEnabled(True)
        self.Qss.setObjectName("Qss")
        self.gridLayout.addWidget(self.Qss, 1, 1, 1, 1)
        self.QssName = QtWidgets.QLabel(self.gridLayoutWidget)

        self.gridLayout.addWidget(self.QssName, 0, 0, 1, 1)
        self.QssNameEdit = QtWidgets.QLineEdit(self.gridLayoutWidget)

        self.gridLayout.addWidget(self.QssNameEdit, 0, 1, 1, 1)
        self.pushButton = QtWidgets.QPushButton(self.gridLayoutWidget)

        self.gridLayout.addWidget(self.pushButton, 2, 1, 1, 1)


        self.setLayout(self.gridLayout)
        


    def retranslateUi(self):

        self.setWindowTitle("QssMaker")
        self.QssName.setText("Qss Name")
        self.pushButton.setText("Make It So !")


if __name__ == "__main__":
    import sys
    MainEvntThred = QtWidgets.QApplication([])

    MainApp = Ui_QssMakerWindow()
    MainApp.show()

    MainEvntThred.exec()
