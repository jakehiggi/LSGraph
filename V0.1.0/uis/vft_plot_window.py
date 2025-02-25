from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(457, 493)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setMinimumSize(QtCore.QSize(4, 37))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.frame)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout.addWidget(self.frame, 2, 0, 1, 1)
        self.yTreeWidget = QtWidgets.QTreeWidget(self.centralwidget)
        self.yTreeWidget.setObjectName("yTreeWidget")
        self.yTreeWidget.header().setVisible(False)
        self.gridLayout.addWidget(self.yTreeWidget, 1, 1, 1, 1)
        self.xTreeWidget = QtWidgets.QTreeWidget(self.centralwidget)
        self.xTreeWidget.setAlternatingRowColors(True)
        self.xTreeWidget.setObjectName("xTreeWidget")
        self.xTreeWidget.header().setVisible(False)
        self.gridLayout.addWidget(self.xTreeWidget, 1, 0, 1, 1)
        self.plotButton = QtWidgets.QPushButton(self.centralwidget)
        self.plotButton.setObjectName("plotButton")
        self.gridLayout.addWidget(self.plotButton, 2, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "X Data:"))
        self.plotButton.setText(_translate("MainWindow", "Plot"))
        self.label_2.setText(_translate("MainWindow", "Y Data:"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
