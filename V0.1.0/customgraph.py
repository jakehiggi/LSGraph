from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QFileDialog, QAction
from PyQt5.QtWidgets import QMdiSubWindow, QTableWidget, QTableWidgetItem, QLabel, QPushButton, QMessageBox, QMdiArea
from PyQt5.QtWidgets import QGridLayout, QVBoxLayout, QSplitter, QTreeWidget, QTreeWidgetItem, QListWidget, QStackedWidget, QListWidgetItem
from PyQt5.QtWidgets import QItemDelegate, QFileSystemModel, qApp, QAbstractItemView
import PyQt5.QtWidgets as qw
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt, QFileInfo, QSettings, QDataStream, QIODevice
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore, QtGui
import pyqtgraph as pg
import os
import sys
import csv
from pyqtgraph import PlotWidget, PlotItem
from customtree import CustomTree

class CustomGraph(PlotWidget):
    graphDropped = QtCore.pyqtSignal(list)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        event.accept()
        # else:
        #     event.ignore()
            
    def dragMoveEvent(self, event):
        # if event.mimeData().hasUrls():
        event.setDropAction(Qt.MoveAction)
        event.accept()
    
    def dropEvent(self, event):
        if event.mimeData().hasFormat(CustomTree.customMimeType):
            encoded = event.mimeData().data(CustomTree.customMimeType)
            items = self.decodeData(encoded, event.source())
            sheets = []
            for item in items:
                sheets.append(item.text(0))              
            event.acceptProposedAction()
            self.graphDropped.emit(sheets)
            
    def encodeData(self, items, stream):
        stream.writeInt32(len(items))
        for item in items:
            p = item
            rows = []
            while p is not None:
                rows.append(self.indexFromItem(p).row())
                p = p.parent()
            stream.writeInt32(len(rows))
            for row in reversed(rows):
                stream.writeInt32(row)
        return stream
    
    def decodeData(self, encoded, tree):
        items = []
        rows = []
        stream = QDataStream(encoded, QIODevice.ReadOnly)
        while not stream.atEnd():
            nItems = stream.readInt32()
            for i in range(nItems):
                path = stream.readInt32()
                row = []
                for j in range(path):
                    row.append(stream.readInt32())
                rows.append(row)
    
        for row in rows:
            it = tree.topLevelItem(row[0])
            for ix in row[1:]:
                it = it.child(ix)
            items.append(it)
        return items
        
    