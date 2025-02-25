from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QFileDialog, QAction
from PyQt5.QtWidgets import QMdiSubWindow, QTableWidget, QTableWidgetItem, QLabel, QPushButton, QMessageBox, QMdiArea
from PyQt5.QtWidgets import QGridLayout, QVBoxLayout, QSplitter, QTreeWidget, QTreeWidgetItem, QListWidget, QStackedWidget, QListWidgetItem
from PyQt5.QtWidgets import QItemDelegate, QFileSystemModel
import csv

class ReloadTable(QTableWidget):
    path = ''
    def __init__(self, r, c):
        super().__init__(r, c)
        self.check_change = True
        self.init_ui()

    def init_ui(self):
        self.cellChanged.connect(self.c_current)
        self.show()

    def c_current(self):
        if self.check_change:
            row = self.currentRow()
            col = self.currentColumn()
            value = self.item(row, col)
            value = value.text()
            print("The current cell is ", row, ", ", col)
            print("In this cell we have: ", value)

    def open_sheet(self, path):

        self.check_change = False
        with open(path, newline='') as csv_file:
            self.setRowCount(0)
            self.setColumnCount(10)
            my_file = csv.reader(csv_file, delimiter=',', quotechar='|')
            for row_data in my_file:
                row = self.rowCount()
                self.insertRow(row)
                if len(row_data) > 10:
                    self.setColumnCount(len(row_data))
                for column, stuff in enumerate(row_data):
                    item = QTableWidgetItem(stuff)
                    self.setItem(row, column, item)
        self.check_change = True

def table_widget_parents(dictionary):
    keys = list(dictionary.keys())
    holding = []
    for i in keys:
        holding.append([i])
    parent_items = []
    for i in holding:
        parent_items.append(QTreeWidgetItem(i))
    return parent_items

def table_widget_children(dictionary):
    keys = list(dictionary.keys())
    inner_keys = []
    for key in keys:
        a = list(dictionary[key].keys())
        for item in a:
            if item not in inner_keys:
                inner_keys.append(item)

    nested_keys = []
    for item in inner_keys:
        nested_keys.append([item])

    children_items = []
    for i in nested_keys:
        children_items.append(QTreeWidgetItem(i))

    return children_items
