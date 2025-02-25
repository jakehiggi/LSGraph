from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QFileDialog, QAction
from PyQt5.QtWidgets import QMdiSubWindow, QTableWidget, QTableWidgetItem, QLabel, QPushButton, QMessageBox, QMdiArea
from PyQt5.QtWidgets import QGridLayout, QVBoxLayout, QSplitter, QTreeWidget, QTreeWidgetItem, QListWidget, QStackedWidget, QListWidgetItem
from PyQt5.QtWidgets import QItemDelegate, QFileSystemModel, qApp, QAbstractItemView
import PyQt5.QtWidgets as qw
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt, QFileInfo, QSettings, QDataStream, QIODevice, QByteArray
from PyQt5.QtGui import QIcon, QDrag
from PyQt5 import QtCore, QtGui
import os
import sys
import csv
# from PyQt5 import QDir


class CustomTree(QTreeWidget):
    dropped = QtCore.pyqtSignal(list)
    customMimeType = "application/x-customTreeWidgetdata"
    def __init__(self, parent=None):
        super().__init__(parent)
        # self.setAcceptDrops(True)
        # self.resize(600, 600)
        # self.setHeaderLabels(['Name', 'Size', 'Upload Status'])
        
        

        # model = QFileSystemModel()
        # model.setRootPath(QDir.currentPath())
        # model.setReadOnly(False)

        self.setSelectionMode(self.SingleSelection)
        # self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        

    def mimeTypes(self):
        mimetypes = QTreeWidget.mimeTypes(self)
        mimetypes.append(CustomTree.customMimeType)
        return mimetypes
    
    def startDrag(self, supportedActions):
        drag = QDrag(self)
        mimedata = self.model().mimeData(self.selectedIndexes())

        encoded = QByteArray()
        stream = QDataStream(encoded, QIODevice.WriteOnly)
        self.encodeData(self.selectedItems(), stream)
        mimedata.setData(CustomTree.customMimeType, encoded)

        drag.setMimeData(mimedata)
        drag.exec_(supportedActions)
    
   
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        # if event.mimeData().hasUrls():
        event.setDropAction(Qt.MoveAction)
        event.accept()
        # else:
        #     event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()

            links = []
            links2 = []
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    links.append(str(url.toLocalFile()))
                else:
                    links.append(str(url.toString()))
            
            
            self.dropped.emit(links)
        else:
            event.ignore()
    
    def fillItem(self, inItem, outItem):
        for col in range(inItem.columnCount()):
            for key in range(Qt.UserRole):
                role = Qt.ItemDataRole(key)
                outItem.setData(col, role, inItem.data(col, role))

    def fillItems(self, itFrom, itTo):
        for ix in range(itFrom.childCount()):
            it = QTreeWidgetItem(itTo)
            ch = itFrom.child(ix)
            self.fillItem(ch, it)
            self.fillItems(ch, it)
    
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
    
    # def dragLeaveEvent(self, event):
    #     if event.mimeData().hasFormat(CustomTree.customMimeType):
    #         encoded = event.mimeData().data(CustomTree.customMimeType)
    #         parent = self.itemAt(event.pos())
    #         items = self.decodeData(encoded, event.source())
    #         for it in items:
    #             item = QTreeWidgetItem(parent)
    #             self.fillItem(it, item)
    #             self.fillItems(it, item)
    #         event.acceptProposedAction()
    #         print(items)
        
        
