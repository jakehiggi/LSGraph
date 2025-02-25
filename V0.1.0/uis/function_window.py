from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(451, 502)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.frame)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.addFunction = QtWidgets.QPushButton(self.frame)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../icons/add_29356.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.addFunction.setIcon(icon)
        self.addFunction.setIconSize(QtCore.QSize(15, 15))
        self.addFunction.setObjectName("addFunction")
        self.gridLayout_2.addWidget(self.addFunction, 1, 2, 1, 1)
        self.stackedWidget = QtWidgets.QStackedWidget(self.frame)
        self.stackedWidget.setMinimumSize(QtCore.QSize(275, 0))
        self.stackedWidget.setObjectName("stackedWidget")
        self.hnPage = QtWidgets.QWidget()
        self.hnPage.setObjectName("hnPage")
        self.hnBrowser = QtWidgets.QTextBrowser(self.hnPage)
        self.hnBrowser.setGeometry(QtCore.QRect(0, 0, 271, 391))
        self.hnBrowser.setObjectName("hnBrowser")
        self.stackedWidget.addWidget(self.hnPage)
        self.conPage = QtWidgets.QWidget()
        self.conPage.setObjectName("conPage")
        self.conBrowser = QtWidgets.QTextBrowser(self.conPage)
        self.conBrowser.setGeometry(QtCore.QRect(0, 0, 271, 391))
        self.conBrowser.setObjectName("conBrowser")
        self.stackedWidget.addWidget(self.conPage)
        self.arrheniusPage = QtWidgets.QWidget()
        self.arrheniusPage.setObjectName("arrheniusPage")
        self.arrheniusBrowser = QtWidgets.QTextBrowser(self.arrheniusPage)
        self.arrheniusBrowser.setGeometry(QtCore.QRect(0, 0, 271, 391))
        self.arrheniusBrowser.setObjectName("arrheniusBrowser")
        self.stackedWidget.addWidget(self.arrheniusPage)
        self.VFTPage = QtWidgets.QWidget()
        self.VFTPage.setObjectName("VFTPage")
        self.VFTBrowser = QtWidgets.QTextBrowser(self.VFTPage)
        self.VFTBrowser.setGeometry(QtCore.QRect(0, 0, 271, 391))
        self.VFTBrowser.setObjectName("VFTBrowser")
        self.stackedWidget.addWidget(self.VFTPage)
        self.gridLayout_2.addWidget(self.stackedWidget, 0, 1, 1, 2)
        self.funcList = QtWidgets.QListWidget(self.frame)
        self.funcList.setAlternatingRowColors(True)
        self.funcList.setObjectName("funcList")
        item = QtWidgets.QListWidgetItem()
        self.funcList.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.funcList.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.funcList.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.funcList.addItem(item)
        self.gridLayout_2.addWidget(self.funcList, 0, 0, 1, 1)
        self.horizontalLayout.addWidget(self.frame)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionAdd_Function = QtWidgets.QAction(MainWindow)
        self.actionAdd_Function.setIcon(icon)
        self.actionAdd_Function.setObjectName("actionAdd_Function")

        self.retranslateUi(MainWindow)
        self.stackedWidget.setCurrentIndex(3)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.addFunction.setText(_translate("MainWindow", "Add Function"))
        self.hnBrowser.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt; font-weight:600; color:#ff0000;\">Havriliak-Negami</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<table border=\"0\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px;\" cellspacing=\"2\" cellpadding=\"0\">\n"
"<tr>\n"
"<td style=\" vertical-align:top;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'KaTeX_Math\'; font-size:12pt; font-style:italic; color:#000000;\">ε</span><span style=\" font-family:\'Arial,Helvetica,sans-serif\'; font-size:12pt; color:#000000; vertical-align:bottom;\">∗</span><span style=\" font-family:\'Arial,Helvetica,sans-serif\'; font-size:12pt; color:#000000;\">=</span><span style=\" font-family:\'KaTeX_Math\'; font-size:12pt; font-style:italic; color:#000000;\">ε</span><span style=\" font-family:\'Arial,Helvetica,sans-serif\'; font-size:12pt; color:#000000; vertical-align:sub;\">∞</span><span style=\" font-family:\'Arial,Helvetica,sans-serif\'; font-size:12pt; color:#000000; vertical-align:bottom;\">​</span><span style=\" font-family:\'Arial,Helvetica,sans-serif\'; font-size:12pt; color:#000000;\">+</span><span style=\" font-family:\'Arial,Helvetica,sans-serif\'; font-size:12pt; color:#000000; vertical-align:bottom;\">Δ</span><span style=\" font-family:\'KaTeX_Math\'; font-size:12pt; font-style:italic; color:#000000; vertical-align:bottom;\">ε/</span><span style=\" font-family:\'Arial,Helvetica,sans-serif\'; font-size:12pt; color:#000000; vertical-align:bottom;\">​((1+</span><span style=\" font-family:\'KaTeX_Math\'; font-size:12pt; font-style:italic; color:#000000; vertical-align:bottom;\">iωτ</span><span style=\" font-family:\'Arial,Helvetica,sans-serif\'; font-size:12pt; color:#000000; vertical-align:bottom;\">)</span><span style=\" font-family:\'KaTeX_Math\'; font-size:12pt; font-style:italic; color:#000000; vertical-align:super;\">a</span><span style=\" font-family:\'Arial,Helvetica,sans-serif\'; font-size:12pt; color:#000000; vertical-align:bottom;\">)</span><span style=\" font-family:\'KaTeX_Math\'; font-size:12pt; font-style:italic; color:#000000; vertical-align:super;\">b</span><span style=\" font-family:\'Arial,Helvetica,sans-serif\'; font-size:12pt; color:#000000; vertical-align:bottom;\">​</span></p></td></tr></table>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'KaTeX_Math\'; font-size:10pt; font-style:italic; color:#000000; vertical-align:top;\">ε</span><span style=\" font-family:\'Arial,Helvetica,sans-serif\'; font-size:10pt; color:#000000; vertical-align:bottom;\">∗ - dielectric</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Arial,Helvetica,sans-serif\'; font-size:12pt; color:#000000; vertical-align:bottom;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p></body></html>"))
        self.conBrowser.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt; font-weight:600; color:#ff0000;\">Conductivity</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">For graphs of Epsilon\'\' vs Frequency.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.arrheniusBrowser.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt; font-weight:600; color:#ff0000;\">Arrhenius</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.VFTBrowser.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt; font-weight:600; color:#ff0000;\">Vogel-Fulcher-Tammann</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:10pt; font-weight:600; color:#ff0000;\"><br /></p></body></html>"))
        __sortingEnabled = self.funcList.isSortingEnabled()
        self.funcList.setSortingEnabled(False)
        item = self.funcList.item(0)
        item.setText(_translate("MainWindow", "Havriliak -Negami"))
        item = self.funcList.item(1)
        item.setText(_translate("MainWindow", "Conductivity"))
        item = self.funcList.item(2)
        item.setText(_translate("MainWindow", "Arrhenius"))
        item = self.funcList.item(3)
        item.setText(_translate("MainWindow", "VFT"))
        self.funcList.setSortingEnabled(__sortingEnabled)
        self.actionAdd_Function.setText(_translate("MainWindow", "Add Function"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
