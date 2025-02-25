from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QFileDialog, QAction
from PyQt5.QtWidgets import QMdiSubWindow, QTableWidget, QTableWidgetItem, QLabel, QPushButton, QMessageBox, QMdiArea
from PyQt5.QtWidgets import QGridLayout, QVBoxLayout, QSplitter, QTreeWidget, QTreeWidgetItem, QListWidget, QStackedWidget, QListWidgetItem
from PyQt5.QtWidgets import QItemDelegate, QFileSystemModel, qApp, QShortcut, QComboBox
import PyQt5.QtWidgets as qw
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt, QFileInfo, QSettings, pyqtSlot
from PyQt5.QtGui import QKeySequence
from PyQt5 import QtCore, QtGui
import os
import sys
import csv
import pickle
from txt_csv import txt_to_csv

from FunctionClasses import ReloadTable, table_widget_parents, table_widget_children

import numpy as np
import scipy as sp
from lmfit import Model
import pyqtgraph as pg
from customgraph import CustomGraph
from customtree import CustomTree

#type 6, schjksd, css, javascript, telwin, react, vanila extract


global x_plot_key
global x_plot_inner_key
global selected_line


ui_path = str(os.path.join(os.getcwd(), 'uis\\'))

current_dir = os.getcwd()
if 'temp' in os.listdir():
    print('temp exists...')

else:
    print('creating temp...')
    os.mkdir('temp')
temp_bin = (str(os.path.join(os.getcwd(), 'temp\\')))

for file in os.listdir(os.path.join(os.getcwd(), 'temp')):
    os.remove(os.path.join(os.getcwd(), 'temp\\') + file)

symbols = ['o', 's', 't', 'star', '+', 'x']
drop_symbols = ['o', 's', 't', 'd', 't1']*10
line_colours = [None,(0,0,0), (128,128,128), (128,0,0),
                (255,0,0), (255,165,0), (210,210,0),
                (128,128,0), (0,128,0), (0,255,0),
                (0,128,128), (0,255,255), (0,0,128),
                (0,0,255), (128,0,128), (255,0,255),
                (220,20,60)]*10
line_colours_Q = [None,QtGui.QColor(0,0,0), QtGui.QColor(128,128,128), QtGui.QColor(128,0,0),
                QtGui.QColor(255,0,0), QtGui.QColor(255,165,0), QtGui.QColor(210,210,0),
                QtGui.QColor(128,128,0), QtGui.QColor(0,128,0), QtGui.QColor(0,255,0),
                QtGui.QColor(0,128,128), QtGui.QColor(0,255,255), QtGui.QColor(0,0,128),
                QtGui.QColor(0,0,255), QtGui.QColor(128,0,128), QtGui.QColor(255,0,255),
                QtGui.QColor(220,20,60)]*10
colours_rgb = [(0,0,0), (228,19,47),(61,19,228),(13,148,8),(253,8,253),(8,237,253),(253,172,8)]
hn_colours_rgb = [None, (228,19,47), (13,148,8), (8,237,253)]
con_colours_rgb = [None, (61,19,228), (253,8,253), (253,172,8)]
con_children = None
hn_children = None
arrhenius_children = None
vft_children = None
tail = None
selected_line = None
sheet_path = None
low_region = 0
high_region = np.inf

vft_values = {}
file_dict = {}
data_dict = {}
window_dict = {}
vft_dict = {}
vft_lines = {}
lines_dict= {'data':{}, 'fits': {}, 'temp':{}, 'hidden':{}}



def HN_function(x,amp,tau,alpha,beta):
        hn = np.zeros((len(x)),dtype = 'complex')
        for i,freq in enumerate(x):
                hn[i] = (amp/(((1+(1j*2*np.pi*freq*tau)**alpha)**beta)))

        return -1*np.imag(hn)

def cond_function(x,amp,exp, imag = 1, real = 1):
        cond = np.zeros((len(x)), dtype = 'complex')
        for i,freq in enumerate(x):
            cond[i] = (amp*np.power((1j*2*np.pi*freq),exp))
        return -1*np.imag(cond)

def arrhenius_function(x, const, ea):
    arrhenius = np.zeros((len(x)))
    for i,temp in enumerate(x):
        arrhenius[i] = (const*np.exp(-ea/(sp.constants.R * temp)))
    return arrhenius

def VFT_function(x, tau_nort, D, T_nort):
    vft = np.zeros((len(x)), dtype = 'complex')
    for i,temp in enumerate(x):
        vft[i] = (tau_nort * np.exp((-D*T_nort)/(temp-T_nort)))
    return -1*np.imag(vft)

class MainWindow(QMainWindow):
    sheet_count = 0
    graph_count = 0
    def __init__(self, parent=None):
        super(MainWindow, self).__init__()
        loadUi(ui_path + "main_window.ui", self)
        self.child = None
        self.graphChild = None
        self.fitValuesChild = None
        self.resize(1300,800)
        self.mdi = self.findChild(QMdiArea, 'mdiArea')

        self.fileMake_CSV = self.findChild(QAction, "actionMake_CSV")
        self.fileSheet = self.findChild(QAction, "actionSheet")
        self.graphGraph = self.findChild(QAction, "actionGraph")

        self.fileTree = self.findChild(CustomTree, 'CustomTree')
        self.treeProject = self.fileTree.topLevelItem(0)
        self.treeSheet = self.treeProject.child(0)
        self.treeGraph = self.treeProject.child(1)
        self.treeFitValues = self.treeProject.child(2)
        self.treeProject.setExpanded(True)
        self.treeSheet.setExpanded(True)
        self.treeGraph.setExpanded(True)
        self.treeFitValues.setExpanded(True)
        self.fileTree.dropped.connect(self.dropHandler)

        self.fileSheet.triggered.connect(self.sheet_window)
        self.fileMake_CSV.triggered.connect(self.load_file)
        self.graphGraph.triggered.connect(self.New_Graph)
        self.fileTree.itemDoubleClicked.connect(self.treeDoubleClicked)

        self.black.clicked.connect(lambda: self.colour_change(1))
        self.gray.clicked.connect(lambda: self.colour_change(2))
        self.maroon.clicked.connect(lambda: self.colour_change(3))
        self.red.clicked.connect(lambda: self.colour_change(4))
        self.orange.clicked.connect(lambda: self.colour_change(5))
        self.yellow.clicked.connect(lambda: self.colour_change(6))
        self.olive.clicked.connect(lambda: self.colour_change(7))
        self.green.clicked.connect(lambda: self.colour_change(8))
        self.lime.clicked.connect(lambda: self.colour_change(9))
        self.teal.clicked.connect(lambda: self.colour_change(10))
        self.aqua.clicked.connect(lambda: self.colour_change(11))
        self.navy.clicked.connect(lambda: self.colour_change(12))
        self.blue.clicked.connect(lambda: self.colour_change(13))
        self.purple.clicked.connect(lambda: self.colour_change(14))
        self.pink.clicked.connect(lambda: self.colour_change(15))
        self.crimson.clicked.connect(lambda: self.colour_change(16))
        self.blackShortcut = QShortcut(QKeySequence("Ctrl+B"), self)
        self.blackShortcut.activated.connect(lambda: self.colour_change(1))
        self.comboBox.currentTextChanged.connect(self.symbol_change)
        self.spinBox.valueChanged.connect(self.symbol_size)

        self.delete = QShortcut(QKeySequence("Del"), self)
        self.delete.activated.connect(self.delete_tree_item)

        self.titleLineEdit.textEdited.connect(self.set_graph_title)
        self.xAxisLineEdit.textEdited.connect(self.set_x_title)
        self.yAxisLineEdit.textEdited.connect(self.set_y_title)
        self.titleSpinBox.valueChanged.connect(self.set_graph_title)
        self.titleSpinBox.valueChanged.connect(self.set_graph_title)
        self.xAxisSpinBox.valueChanged.connect(self.set_x_title)
        self.yAxisSpinBox.valueChanged.connect(self.set_y_title)
        self.xAxisComboBox.currentTextChanged.connect(self.x_axis_scale_change)
        self.yAxisComboBox.currentTextChanged.connect(self.y_axis_scale_change)

        self.actionSort_Sheets.triggered.connect(self.sort_sheets)

        self.actionSave_VFT_Dict_As.triggered.connect(self.save_vft_dict_as)
        self.actionOpen_VFT_Dict.triggered.connect(self.open_vft_dict)

        self.fileTree.itemDoubleClicked.connect(self.fitted_value_name_change)
        self.fileTree.itemChanged.connect(self.change_keys)

        self.added_dictionaries = 0
        self.actionAdd_Dictionary.triggered.connect(self.add_dictionary)
        
        self.symbolCheckBox.stateChanged.connect(self.show_symbols)
        self.lineSpinBox.valueChanged.connect(self.change_line_width)

    def change_line_width(self):
        if self.graphChild != None:
            for i in range(len(self.graphChild.plotItem.listDataItems())):
                lines = self.graphChild.plotItem.listDataItems()
                lines[i].setPen(color=line_colours[i+1], width=self.lineSpinBox.value())

    def show_symbols(self):
        if self.symbolCheckBox.checkState() == Qt.Unchecked:
            for line in self.graphChild.plotItem.listDataItems():
                line.setSymbolSize(0)
        if self.symbolCheckBox.checkState() == Qt.Checked:
            for line in self.graphChild.plotItem.listDataItems():
                line.setSymbolSize(4)

    
    def delete_tree_item(self):
        items_to_delete = self.fileTree.selectedItems()
        print(items_to_delete)
        for item in items_to_delete:
            parent = item.parent()
            if parent.text(0) == 'fit values':
                vft_dict.pop(item.text(0))
                self.treeFitValues.removeChild(item)


    def add_dictionary(self):
        self.added_dictionaries += 1
        name = 'new_dict_' + str(self.added_dictionaries)
        vft_dict[name] = {}
        child = QTreeWidgetItem([name])
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/fit_values.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.treeFitValues.insertChild(0, child)
        self.treeFitValues.child(0).setIcon(0, icon)
        self.treeFitValues.child(0).setFlags(child.flags() | Qt.ItemIsEditable)



    def fitted_value_name_change(self, item, column):
        if item.parent().text(0) == 'fit values':
            global old_name
            old_name = item.text(column)
        else:
            pass

    def change_keys(self, item, column):
        if item.parent().text(column) == 'fit values':
            try:
                new_name = item.text(column)
                vft_dict[new_name] = vft_dict.pop(old_name)
            except:
                pass

    def save_vft_dict_as(self):
        filename = QFileDialog.getSaveFileName(self, 'Save Values', os.getenv('HOME'), 'VFT(*.vft)')

        # selected_sets = self.fileTree.selectedItems()
        # selected = [i.text(0) for i in selected_sets]
        # print(selected)
        with open(filename[0], 'wb') as file:
            pickle.dump(vft_dict, file, protocol=pickle.HIGHEST_PROTOCOL)

    def open_vft_dict(self):
        # filename = QFileDialog.getOpenFileName(self, 'Open Values', os.getenv('HOME'), 'VFT(*.vft)')
        dialogue = QFileDialog(self)
        dialogue.setFileMode(QFileDialog.ExistingFiles)
        dialogue.setNameFilter('VFT(*.vft)')
        filenames = dialogue.getOpenFileNames(self, "Open files", os.getenv('HOME'), 'VFT(*.vft)')
        for filename in filenames[0]:
            with open(filename, 'rb') as file:
                global vft_dict
                holding_dict = pickle.load(file)
            keys = list(holding_dict.keys())
            vft_dict = vft_dict | holding_dict
            # self.treeFitValues.takeChildren()
            head, tail = os.path.split(filename[0])
            tail = tail[0:-4]
            for key in keys:
                child = QTreeWidgetItem([key])
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap("icons/fit_values.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                self.treeFitValues.insertChild(0, child)
                self.treeFitValues.child(0).setIcon(0, icon)
                self.treeFitValues.child(0).setFlags(child.flags() | Qt.ItemIsEditable)
        
        
        for key in list(vft_dict.keys()):
            thousand_over_temp = []
            temperature = []
            tau = []
            natural_log_tau = []
            amp = []
            alpha = []
            beta = []
            AlphaBeta = []
            for temps in list(sorted(vft_dict[key].keys())):
                if vft_dict[key][temps] != None:
                    thousand_over_temp.append(1000/float(temps))
                    temperature.append(float(temps))
                    tau.append(float(vft_dict[key][temps][0]))
                    natural_log_tau.append(np.log(float(vft_dict[key][temps][0])))
                    amp.append(float(vft_dict[key][temps][1]))
                    alpha.append(float(vft_dict[key][temps][2]))
                    beta.append(float(vft_dict[key][temps][3]))
                    AlphaBeta.append(float(vft_dict[key][temps][2])*float(vft_dict[key][temps][3]))
                    vft_values[key] = thousand_over_temp, natural_log_tau, tau, temperature, amp, alpha, beta, AlphaBeta

    def x_axis_scale_change(self):
        if self.graphChild != None:
            current = self.xAxisComboBox.currentText()
            if current == 'log10':
                self.graphChild.graphArea.setLogMode(True, None)
            if current == 'no scaling':
                self.graphChild.graphArea.setLogMode(False, None)

    def y_axis_scale_change(self):
        if self.graphChild != None:
            current = self.yAxisComboBox.currentText()
            if current == 'log10':
                self.graphChild.graphArea.setLogMode(None, True)
            if current == 'no scaling':
                self.graphChild.graphArea.setLogMode(None, False)

    def sort_sheets(self):
        self.treeSheet.sortChildren(0, Qt.AscendingOrder)
        self.treeFitValues.sortChildren(0, Qt.AscendingOrder)

    def set_graph_title(self):
        if self.graphChild != None:
            size = str(self.titleSpinBox.value()) + 'pt'
            self.graphChild.plotItem.setTitle(self.titleLineEdit.text(), color='black', size=size)

    def set_x_title(self):
        if self.graphChild != None:
            size = str(self.xAxisSpinBox.value()) + 'pt'
            axis = self.graphChild.plotItem.getAxis('bottom')
            labelStyle = {'color': 'black', 'font-size': size}
            axis.setLabel(self.xAxisLineEdit.text(), units=None, unitPrefix=None, **labelStyle)

            
    def set_y_title(self):
        if self.graphChild != None:
            size = str(self.yAxisSpinBox.value()) + 'pt'
            axis = self.graphChild.plotItem.getAxis('left')
            labelStyle = {'color': 'black', 'font-size': size}
            axis.setLabel(self.yAxisLineEdit.text(), units=None, unitPrefix=None, **labelStyle)

    def colour_change(self, int):
        if selected_line.startswith('hn') == False and selected_line.startswith('con') == False:
            if selected_line in lines_dict['data']:
                lines_dict['data'][selected_line][2].setPen(line_colours[int])
                lines_dict['data'][selected_line][2].setSymbolPen(line_colours[int])
                lines_dict['data'][selected_line][2].setSymbolBrush(line_colours[int])
                self.graphChild.listWidget.currentItem().setForeground(line_colours_Q[int])
            elif selected_line in vft_lines:
                pen = pg.mkPen(color=line_colours[int], width=3)
                vft_lines[selected_line].setPen(pen)
                vft_lines[selected_line].setSymbolPen(line_colours[int])
                vft_lines[selected_line].setSymbolBrush(line_colours[int])
                self.graphChild.listWidget.currentItem().setForeground(line_colours_Q[int])
        else:
            if lines_dict['fits'] != {}:
                lines_dict['fits'][selected_line][0].setPen(line_colours[int])
                lines_dict['fits'][selected_line][0].setSymbolPen(line_colours[int])
                lines_dict['fits'][selected_line][0].setSymbolBrush(line_colours[int])
                self.graphChild.listWidget.currentItem().setForeground(line_colours_Q[int])

    def symbol_change(self):
        if lines_dict['data'] != {}:
            current = self.comboBox.currentText()
            if current == 'Circle':
                lines_dict['data'][selected_line][2].setSymbol(symbols[0])
            if current == 'Square':
                lines_dict['data'][selected_line][2].setSymbol(symbols[1])
            if current == 'Triangle':
                lines_dict['data'][selected_line][2].setSymbol(symbols[2])
            if current == 'Star':
                lines_dict['data'][selected_line][2].setSymbol(symbols[3])
            if current == '+':
                lines_dict['data'][selected_line][2].setSymbol(symbols[4])
            if current == 'x':
                lines_dict['data'][selected_line][2].setSymbol(symbols[5])

    def symbol_size(self):
        number = self.spinBox.value()
        if lines_dict['data'] != {}:
            lines_dict['data'][selected_line][2].setSymbolSize(number)

    def dropHandler(self, links):
        for file in links:
            if file.lower().endswith('.txt'):
                txt_to_csv(file, path=temp_bin)

                head, tail = os.path.split(str(file))
                tail = tail[0:-4]
                new_path = str(temp_bin + tail + '.csv')
                self.seperate_data(new_path, tail)
                self.update_fileTree_sheet(new_path, tail)
            elif file.lower().endswith('.csv'):
                head, tail = os.path.split(str(file))
                tail = tail[0:-4]
                self.seperate_data(file, tail)
                self.update_fileTree_sheet(file, tail)

    @QtCore.pyqtSlot(QTreeWidgetItem, int)
    def treeDoubleClicked(self, item, column):
        parent = item.parent()
        if item.text(column) == 'sheets':
            pass
        elif item.text(column) == 'project':
            pass
        elif item.text(column) == 'graphs':
            pass
        elif parent.text(column) == 'sheets':
            file_key = item.text(column)
            sub = ReloadTable(10, 10)
            # self.setCentralWidget(self.form_widget)
            col_headers = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
            sub.setHorizontalHeaderLabels(col_headers)
            sub.open_sheet(file_dict[file_key])
            sub.setWindowTitle(file_key)

            self.mdi.addSubWindow(sub)
            sub.show()
        elif parent.text(column) == 'graphs':
            if window_dict[item.text(column)] in self.mdiArea.subWindowList():
                sub_list = self.mdiArea.subWindowList()
                win_index = sub_list.index(window_dict[item.text(column)])
                sub_list[win_index].show()

        elif parent.text(column) == 'fit values':
            self.fitValuesChild = FitValuesDisplay(self, item.text(column))
            self.mdiArea.addSubWindow(self.fitValuesChild)
            self.fitValuesChild.show()

            self.fitValuesChild.populate_table()

    def load_file(self):
        fname = QFileDialog.getOpenFileName(self, "Open File", "", "txt (*.txt);; csv (*.csv);; All files (*)")
        path = str(fname[0])
        print(path)
        txt_to_csv(path)

        msg = QMessageBox()
        msg.setWindowTitle(" ")
        msg.setText("CSV created succesfully")
        msg.setIcon(QMessageBox.Information)
        msg.exec_()

    def open_data(self):
        self.form_widget = MyTable(10, 10)
        self.setCentralWidget(self.form_widget)
        col_headers = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        self.form_widget.setHorizontalHeaderLabels(col_headers)

        self.form_widget.open_sheet()

    def New_Graph(self):
        global graph_sub
        GraphWindow.graph_count += 1

        self.graphChild = GraphWindow(self)
        self.mdi.addSubWindow(self.graphChild)
        self.graphChild.show()
        self.update_fileTree_graph()
        window_dict['graph_' + str(GraphWindow.graph_count)] = self.mdiArea.subWindowList()[-1]
        self.mdiArea.subWindowList()[-1].resize(600, 400)

    def sheet_window(self):
        MainWindow.sheet_count = MainWindow.sheet_count + 1
        sheet_sub = Sheet()
        sheet_sub.setWindowTitle(tail)
        sheet_sub.setWindowIcon(QtGui.QIcon("icons/new_sheet.png"))
        self.mdi.addSubWindow(sheet_sub)
        sheet_sub.show()

        self.seperate_data(sheet_path, tail)
        self.update_fileTree_sheet(sheet_path, tail)

    def seperate_data(self, sheet_path, tail):
        with open(sheet_path, 'r') as data_file:
            csv_object = csv.DictReader(data_file)
            frq = []
            eps_prime = []
            eps_db_prime = []
            run_info = []
            temp = []
            data_dict[tail] = {}
            for column in csv_object:
                frq.append(column['Freq.[Hz]'])
                eps_prime.append(column['Eps\''])
                eps_db_prime.append(column['Eps\'\''])
                run_info.append(column['run_info'])
                temp.append(column['temp'])
            data_dict[tail]['frq'] = frq

            data_dict[tail]['eps_prime'] = eps_prime

            data_dict[tail]['eps_db_prime'] = eps_db_prime
            data_dict[tail]['run_info'] = run_info
            data_dict[tail]['temp'] = temp


            global material_name_only
            split_name = tail.split('_')
            holder = []
            for i in range(len(split_name)-1):
                holder.append(split_name[i])
            material_name_only = '_'.join(holder)
            if material_name_only not in vft_dict.keys():
                vft_dict[material_name_only] = {}
                vft_dict[material_name_only][temp[0]] = None
            else:
                vft_dict[material_name_only][temp[0]] = None

            pop = self.treeFitValues.childCount()
            holding = []
            for i in range(pop):
                holding.append(self.treeFitValues.child(i).text(0))
            if material_name_only not in holding:
                child = QTreeWidgetItem([material_name_only])
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap("icons/fit_values.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                self.treeFitValues.insertChild(0, child)
                self.treeFitValues.child(0).setIcon(0, icon)
                self.treeFitValues.child(0).setFlags(child.flags() | Qt.ItemIsEditable)

    def update_fileTree_sheet(self, sheet_path, tail):
        item_to_add = QTreeWidgetItem([tail])
        self.treeSheet.insertChild(0, item_to_add)
        self.treeSheet_child = self.treeSheet.child(0)
        file_dict[tail] = sheet_path
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("icons/document_29383.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.treeSheet_child.setIcon(0, icon1)

    def update_fileTree_graph(self):
        item_to_add = QTreeWidgetItem(["graph_" + str(GraphWindow.graph_count)])
        self.treeGraph.insertChild(0, item_to_add)
        self.treeGraph_child = self.treeGraph.child(0)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("icons/icons8-graph-64.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.treeGraph_child.setIcon(0, icon2)


class MyTable(QTableWidget):
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

    def open_sheet(self):
        global tail
        global sheet_path
        self.check_change = False
        path = QFileDialog.getOpenFileName(self, 'Open CSV', os.getenv('HOME'), 'CSV(*.csv)')
        sheet_path = path[0]
        head, tail = os.path.split(str(path[0]))
        tail = tail[0:-4]
        MyTable.path = MyTable.path + tail

        if path[0] != '':
            with open(path[0], newline='') as csv_file:
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

class Sheet(QMainWindow):
    def __init__(self):
        super().__init__()
        self.form_widget = MyTable(10, 10)
        self.setCentralWidget(self.form_widget)
        col_headers = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        self.form_widget.setHorizontalHeaderLabels(col_headers)

        self.form_widget.open_sheet()

        self.show()

class FitValuesDisplay(QMainWindow):
    def __init__(self, parent=None, data_name=None):
        super(FitValuesDisplay, self).__init__(parent)
        loadUi(ui_path + "fit_values_display.ui", self)
        self.parent = parent
        self.data_name = data_name
        self.setWindowTitle(self.data_name)


    def populate_table(self):
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setRowCount(40)
        self.tableWidget.setItem(0,0, QTableWidgetItem('temp'))
        self.tableWidget.setItem(0,1, QTableWidgetItem('tau'))
        self.tableWidget.setItem(0,2, QTableWidgetItem('amp'))
        self.tableWidget.setItem(0,3, QTableWidgetItem('alpha'))
        self.tableWidget.setItem(0,4, QTableWidgetItem('beta'))
        keys = list(sorted(vft_dict[self.data_name].keys()))
        temp_items = [QTableWidgetItem(i) for i in list(sorted(vft_dict[self.data_name].keys()))]
        # tau_items = [QTableWidgetItem(i) for i in list(vft_dict[self.data_name].values())]
        tau_items = []
        amp_items = []
        alpha_items = []
        beta_items = []
        for key in keys:
            if vft_dict[self.data_name][key] == None:
                tau_items.append(QTableWidgetItem(''))
            else:
                tau_items.append(QTableWidgetItem(vft_dict[self.data_name][key][0]))
                amp_items.append(QTableWidgetItem(vft_dict[self.data_name][key][1]))
                alpha_items.append(QTableWidgetItem(vft_dict[self.data_name][key][2]))
                beta_items.append(QTableWidgetItem(vft_dict[self.data_name][key][3]))
        # row_counter_temp = 1
        # row_counter_tau = 1
        row_counter = 1
        # for item in temp_items:
        #     self.tableWidget.setItem(row_counter_temp, 0, item)
        #     row_counter_temp += 1
        # for item in tau_items:
        #     self.tableWidget.setItem(row_counter_tau, 1, item)
        #     row_counter_tau += 1
        for i in range(len(temp_items)):
            self.tableWidget.setItem(row_counter, 0, temp_items[i])
            self.tableWidget.setItem(row_counter, 1, tau_items[i])
            self.tableWidget.setItem(row_counter, 2, amp_items[i])
            self.tableWidget.setItem(row_counter, 3, alpha_items[i])
            self.tableWidget.setItem(row_counter, 4, beta_items[i])
            row_counter += 1

class GraphWindow(QMainWindow):
    graph_count = 0
    def __init__(self, parent=None):
        super(GraphWindow, self).__init__()
        loadUi(ui_path + "graph_window.ui", self)
        self.parent = parent
        self.fitChild = None
        self.child = None

        self.plotChild = None
        self.line_count = 0
        self.setWindowTitle("graph_" + str(GraphWindow.graph_count))
        self.resize(350, 350)

        self.plot = self.findChild(QAction, "actionPlot")
        self.fit = self.findChild(QAction, "actionFit")
        self.form = self.findChild(QAction, "actionForm")
        self.listWidget = self.findChild(QListWidget, "listWidget")
        self.graphArea = self.findChild(CustomGraph, "graphArea")

        self.plot.triggered.connect(self.plot_widget)
        self.fit.triggered.connect(self.fit_widget)
        self.actionVFT_Plot.triggered.connect(self.vft_plot_widget)

        self.listWidget.itemClicked.connect(self.onListItemClicked)
        self.listWidget.itemSelectionChanged.connect(self.itemChanged)
        self.actionLimiter.changed.connect(self.toggle_limiter)
        self.actionClipper.changed.connect(self.toggle_clipper)
        self.actionClip.triggered.connect(self.clip)
        self.actionClear.triggered.connect(self.clear_graph)
        self.actionSelected_Only.changed.connect(self.viewMode_selected_only)
        self.actionDefault.changed.connect(self.viewMode_default)
        self.actionAll_Black.triggered.connect(self.all_black)

        self.graphArea.setLogMode(True, True)
        self.plotItem = self.graphArea.getPlotItem()
        self.plotLines = self.plotItem.listDataItems()
        self.listWidget.installEventFilter(self)

        self.graph_setup()
        self.graphArea.graphDropped.connect(self.graphDroppedHandler)
        self.lg = pg.LinearRegionItem(values=(0, 1), orientation='vertical',
                                 brush=(238,238,238), pen=(255,0,0))
        self.lg.sigRegionChanged.connect(self.regionUpdated)

        roi_pen = pg.mkPen(color = 'red', width=2)
        self.roi = pg.InfiniteLine(pos=0, angle=90, pen=roi_pen,
                                   movable=True, label='ClipAbove')

        self.legend = pg.LegendItem(offset=(-1,1), horSpacing=20, verSpacing=-1, labelTextColor=(0,0,0),
                                    labelTextSize='8pt', colCount=3)
        self.legend.setParentItem(self.plotItem)
        self.legend.setPos(1,1)
        
        self.xAxis = self.plotItem.getAxis('bottom')
        self.yAxis = self.plotItem.getAxis('left')
        
        font=QtGui.QFont()
        font.setPixelSize(16)
        self.xAxis.setTickFont(font)
        self.yAxis.setTickFont(font)
        pen = pg.mkPen('black')
        self.xAxis.setTextPen(pen)
        self.yAxis.setTextPen(pen)
        self.xAxis.enableAutoSIPrefix(enable=False)
        self.yAxis.enableAutoSIPrefix(enable=False)

    def all_black(self):
        for line in lines_dict['data']:
            lines_dict['data'][line][2].setPen('black')
            lines_dict['data'][line][2].setSymbolPen('black')
            lines_dict['data'][line][2].setSymbolBrush('black')
        for i in range(self.listWidget.count()):
            self.listWidget.item(i).setForeground(line_colours_Q[1])

    def graphDroppedHandler(self, sheets):
        for sheet in sheets:
            print('recieved')
            self.update_graph_from_drop(sheet)
            self.update_list(sheet, line_colours_Q[self.line_count])
            global last_added
            last_added = sheet

    def pointClicker(self, item, points):
        print(points)

    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.ContextMenu and source is self.listWidget):
            menu = QtWidgets.QMenu()
            show = QAction("Show")
            showOnly = QAction("Show Only")
            hide = QAction("Hide")
            menu.addAction(show)
            menu.addAction(showOnly)
            menu.addAction(hide)
            menu_click = menu.exec(event.globalPos())

            # try:
            #     item = source.itemAt(event.pos())
            # except Exception as e:
            #     print(f"No item selected {e}")

            if menu_click == show:
                if selected_line in lines_dict['data'] or selected_line in lines_dict['fits']:
                    pass
                elif selected_line in lines_dict['hidden']:
                    pass

            if menu_click == showOnly :
                    print("Opening Window 2...")

            return super(QListWidget, self.listWidget).eventFilter(source, event)
        return super(QListWidget, self.listWidget).eventFilter(source, event)

    def graph_setup(self):
        self.graphArea.showGrid(x=True, y=True, alpha = 0.6)
        pg.setConfigOption('background', 'w')
        self.plotItem.enableAutoRange(enable=True)

    def regionUpdated(self):
        global low_region
        global high_region
        low_region,high_region = self.lg.getRegion()
        if self.parent.xAxisComboBox.currentText() == 'log10':
            low_region = 10 ** low_region
            high_region = 10 ** high_region

    def toggle_limiter(self):
        if self.actionLimiter.isChecked() == True:
            try:
                self.plotItem.addItem(self.lg)
                a = self.plotItem.listDataItems()
                a[-1].setZValue(100)

            except:
                pass
        if self.actionLimiter.isChecked() == False:
            try:
                self.plotItem.removeItem(self.lg)
            except:
                pass

    def toggle_clipper(self):
        if self.actionClipper.isChecked() == True:
            try:
                self.plotItem.addItem(self.roi)
            except:
                pass
        if self.actionClipper.isChecked() == False:
            try:
                self.plotItem.removeItem(self.roi)
            except:
                pass

    def clip(self):
        value = 10 ** self.roi.value()
        print(value)

        a= self.plotItem.listDataItems()
        print(list(a))

    def update_graph1(self):
        global x_frq
        global y_eps
        self.line_count += 1
        x = data_dict[x_plot_key][x_plot_inner_key]
        y = data_dict[y_plot_key][y_plot_inner_key]
        x_frq = []
        y_eps = []
        for i in x:
            x_frq.append(float(i))
        for i in y:
            y_eps.append(float(i))
        pen = pg.mkPen(color=line_colours[self.line_count], width=2)
        main = self.graphArea.plot(x_frq, y_eps,
                                   pen=pen, symbol='o',
                                   symbolPen = line_colours[self.line_count],
                                   symbolBrush = line_colours[self.line_count],
                                   symbolSize = 5)

        main.setCurveClickable(state=True, width=None)
        main.setZValue(10)
        self.update_lines()
        # self.plotLines[-1].setCurveClickable(True, width=2)
        # self.plotLines[-1].sigClicked.connect(self.tester)
        self.plotLines[-1].sigPointsClicked.connect(self.pointClicker)
        lines_dict['data'][name_of_material] = [x_frq,y_eps, self.plotLines[-1]]

    def update_graph_from_drop(self, data_name):
        global x_frq
        global y_eps

        if data_name in data_dict:
            self.line_count += 1
            colour = line_colours[self.line_count]
            if colour == None:
                colour = 'black'
            x = data_dict[data_name]['frq']
            y = data_dict[data_name]['eps_db_prime']
            x_frq = []
            y_eps = []
            for i in x:
                x_frq.append(float(i))
            for i in y:
                y_eps.append(float(i))
            pen = pg.mkPen(color=line_colours[self.line_count], width=2)
            main = self.graphArea.plot(x_frq, y_eps,
                                       pen=pen, symbol='o',
                                       symbolPen = colour,
                                       symbolBrush = colour,
                                       symbolSize = 8)

            main.setCurveClickable(state=True, width=None)
            self.update_lines()
            self.runInfo.setText(data_dict[data_name]['run_info'][0])
            self.tempLabel.setText(str(float(data_dict[data_name]['temp'][0]))+'K')
            self.plotLines[-1].sigPointsClicked.connect(self.pointClicker)
            lines_dict['data'][data_name] = [x_frq,y_eps, self.plotLines[-1]]
            self.legend.addItem(self.plotLines[-1], (str(float(data_dict[data_name]['temp'][0]))+'K'))
            
        elif data_name in list(vft_values.keys()):
            self.line_count += 1
            colour = line_colours[self.line_count]
            if colour == None:
                colour = 'black'
            x = vft_values[data_name][0]
            y = vft_values[data_name][2]
            x_frq = []
            y_eps = []
            for i in x:
                x_frq.append(float(i))
            for i in y:
                y_eps.append(float(i))
            pen = pg.mkPen(color=line_colours[self.line_count], width=2)
            vft_plot_item = self.graphArea.plot(x, y,
                                       pen=pen, symbol='circle',
                                       symbolPen = colour,
                                       symbolBrush = colour,
                                       symbolSize = 4)

            vft_lines[data_name] = vft_plot_item
            self.update_lines()
            self.update_list(data_name, line_colours_Q[self.line_count])
            self.legend.addItem(self.plotLines[-1], data_name)
    

    def tester(self):
        print(self)

    def update_list(self, material, colour):
        list_pop = self.listWidget.count()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/plot_line_icon.png"))
        self.listWidget.insertItem(list_pop+1, QListWidgetItem(material))
        self.listWidget.item(list_pop).setIcon(icon)
        if colour != None:
            self.listWidget.item(list_pop).setForeground(colour)
        else:
            self.listWidget.item(list_pop).setForeground(QtGui.QColor(0,0,0))

    def update_list_fits(self, name, colour):
        list_pop = self.listWidget.count()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/fit_line_icon.png"))
        self.listWidget.insertItem(list_pop+1, QListWidgetItem(name))
        self.listWidget.item(list_pop).setForeground(colour)
        self.listWidget.item(list_pop).setIcon(icon)

    def update_info(self, selected_line):
        pass

    def clear_graph(self):
        self.plotItem.clear()
        self.listWidget.clear()
        self.line_count = 0
        if self.fitChild != None:
            self.fitChild.funcTree.clear()

    def viewMode_selected_only(self):
        list_pop = self.listWidget.count()
        if self.actionSelected_Only.isChecked() == True:
            self.actionDefault.setChecked(False)
            if selected_line in lines_dict['data']:
                self.plotItem.clear()
                self.plotItem.addItem(lines_dict['data'][selected_line][2])
            elif selected_line == None and list_pop != 0:
                line = self.listWidget.item(0).text()
                self.plotItem.clear()
                self.plotItem.addItem(lines_dict['data'][line][2])
        if self.actionSelected_Only.isChecked() == False:
            self.actionDefault.setChecked(True)
            self.viewMode_default()

    def viewMode_default(self):
        if self.actionDefault.isChecked() == True:
            self.actionSelected_Only.setChecked(False)
        self.plotItem.clear()
        for key in lines_dict['data']:
            self.plotItem.addItem(lines_dict['data'][key][2])
        if lines_dict['fits'] != None:
            for item in lines_dict['fits']:
                self.plotItem.addItem(item[0])

    @QtCore.pyqtSlot(QtWidgets.QListWidgetItem)
    def onListItemClicked(self, item):
        global selected_line
        selected_line = item.text()
        if selected_line in data_dict:
            self.runInfo.setText(data_dict[selected_line]['run_info'][0])
            self.tempLabel.setText(str(float(data_dict[selected_line]['temp'][0]))+'K')

    def itemChanged(self):
        item = self.listWidget.currentItem()
        global selected_line
        selected_line = item.text()
        if selected_line in data_dict:
            self.runInfo.setText(data_dict[selected_line]['run_info'][0])
            self.tempLabel.setText(data_dict[selected_line]['temp'][0])
            if self.actionSelected_Only.isChecked() == True:
                if item.text() in lines_dict['data']:
                    self.plotItem.clear()
                    plot = lines_dict['data'][item.text()][2]
                    # plot.setPen(color='black')
                    # plot.setSymbolBrush(color='black')
                    # plot.setSymbolPen(color='black')
                    self.plotItem.addItem(plot)
                elif item.text() in lines_dict['fits']:
                    self.plotItem.clear()
                    self.plotItem.addItem(lines_dict['fits'][item.text()][0])

    def update_lines(self):
        self.plotItem = self.graphArea.getPlotItem()
        self.plotLines = self.plotItem.listDataItems()

    def plot_widget(self):
        self.child = PlotDialogue(self)
        self.child.show()

    def vft_plot_widget(self):
        self.child = VFTPlotDialogue(self)
        self.child.show()

    def fit_widget(self):
        if self.fitChild == None:
            self.fitChild = FitDialogue(self)
            self.fitChild.show()
        self.fitChild.show()
        self.fitChild.update_fit()

    def closeEvent(self, event):
        event.ignore()
        win = self.parent.mdiArea.activeSubWindow()
        win.hide()

class PlotDialogue(QMainWindow):
    def __init__(self, parent=None):
        super(PlotDialogue, self).__init__(parent)
        loadUi(ui_path + "plot_window.ui", self)
        self.parent = parent
        self.setWindowTitle("Plot Dialogue")


        self.plotButton = self.findChild(QPushButton, "pushPlot")

        ############### TREE SETUP ##################
        self.XTree = self.findChild(QTreeWidget, "XTree")
        self.YTree = self.findChild(QTreeWidget, "YTree")



        self.XTree.setHeaderLabels(['Data Sets'])
        self.XTree.setAlternatingRowColors(True)
        self.XTree.setColumnCount(1)
        self.YTree.setHeaderLabels(['Data Sets'])
        self.YTree.setAlternatingRowColors(True)
        self.YTree.setColumnCount(1)

        parent_items_x = table_widget_parents(data_dict)
        parent_items_y = table_widget_parents(data_dict)
        self.YTree.addTopLevelItems(parent_items_x)
        self.XTree.addTopLevelItems(parent_items_y)

        for i in range(len(parent_items_x)):
            items_x = table_widget_children(data_dict)
            items_y = table_widget_children(data_dict)
            parent_items_x[i].addChildren(items_x)
            parent_items_y[i].addChildren(items_y)
        ##############################################

        self.XTree.itemClicked.connect(self.onItemClicked_x)
        self.YTree.itemClicked.connect(self.onItemClicked_y)
        self.plotButton.clicked.connect(self.update_graph)

    @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, int)
    def onItemClicked_x(self, item, column):
        global x_plot_key
        global x_plot_inner_key
        if QTreeWidgetItem.parent(item) == None:
            None
        else:
            x_plot_inner_key = item.text(column)
            x_plot_key = QTreeWidgetItem.parent(item).text(column)

    @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, int)
    def onItemClicked_y(self, item, column):
        global y_plot_key
        global y_plot_inner_key
        global name_of_material
        if QTreeWidgetItem.parent(item) == None:
            None
        else:
            name_of_material = QTreeWidgetItem.parent(item).text(column)
            y_plot_inner_key = item.text(column)
            y_plot_key = QTreeWidgetItem.parent(item).text(column)

    def update_graph(self):
        self.parent.update_graph1()
        self.parent.update_list(name_of_material, line_colours_Q[self.parent.line_count])


class VFTPlotDialogue(QMainWindow):
    plot_counter = 0
    def __init__(self, parent=None):
        super(VFTPlotDialogue, self).__init__(parent)
        loadUi(ui_path + "vft_plot_window.ui", self)
        self.parent=parent

        # list_items = []
        # for key in list(vft_dict.keys()):
        #     list_items.append(QListWidgetItem(key))
        # self.listWidget.addItems(list(vft_dict.keys()))

        self.xParent = None
        self.yParent = None
        self.xClicked = None
        self.yClicked = None

        parent_itemsX = []
        parent_itemsY = []
        for item in list(vft_dict.keys()):
            parent_itemsX.append(QTreeWidgetItem([item]))
            parent_itemsY.append(QTreeWidgetItem([item]))
        self.xTreeWidget.addTopLevelItems(parent_itemsX)
        self.yTreeWidget.addTopLevelItems(parent_itemsY)
        for item in parent_itemsX:
            children = ['1000/T', 'T', 'tau', 'ln(tau)', 'amp', 'alpha', 'beta', 'alpha*beta']
            children_items = [QTreeWidgetItem([i]) for i in children]
            item.addChildren(children_items)
        for item in parent_itemsY:
            children = ['1000/T', 'T','tau', 'ln(tau)', 'amp', 'alpha', 'beta', 'alpha*beta']
            children_items = [QTreeWidgetItem([i]) for i in children]
            item.addChildren(children_items)

        self.xTreeWidget.itemClicked.connect(self.set_plot_dataX)
        self.yTreeWidget.itemClicked.connect(self.set_plot_dataY)
        self.plotButton.clicked.connect(self.plot)

    def set_plot_dataX(self, item, column):
        self.xClicked = item.text(column)
        self.xParent = item.parent().text(column)

    def set_plot_dataY(self, item, column):
        self.yClicked = item.text(column)
        self.yParent = item.parent().text(column)

    def plot(self):
        try:
            self.parent.actionSelected_Only.changed.disconnect(self.parent.viewMode_selected_only)
            self.parent.actionDefault.changed.disconnect(self.parent.viewMode_default)
        except:
            pass

        # self.parent.plotItem.clear()
        # self.parent.listWidget.clear()
        # if self.parent.fitChild != None:
        #     self.parent.fitChild.funcTree.clear()
        self.parent.plotItem.setLogMode(False, False)
        self.parent.parent.xAxisComboBox.setCurrentIndex(1)
        self.parent.parent.yAxisComboBox.setCurrentIndex(1)

        global thousand_over_temp
        thousand_over_temp = []
        temperature = []
        tau = []
        natural_log_tau = []
        amp = []
        alpha = []
        beta = []
        AlphaBeta = []
        for key in list(sorted(vft_dict[self.xParent].keys())):
            if vft_dict[self.xParent][key] != None:
                thousand_over_temp.append(1000/float(key))
                temperature.append(float(key))
                tau.append(float(vft_dict[self.xParent][key][0]))
                natural_log_tau.append(np.log(float(vft_dict[self.xParent][key][0])))
                amp.append(float(vft_dict[self.xParent][key][1]))
                alpha.append(float(vft_dict[self.xParent][key][2]))
                beta.append(float(vft_dict[self.xParent][key][3]))
                AlphaBeta.append(float(vft_dict[self.xParent][key][2])*float(vft_dict[self.xParent][key][3]))
                vft_values[self.xParent] = thousand_over_temp, natural_log_tau, temperature, amp, alpha, beta, AlphaBeta

        self.parent.line_count += 1
        colour = line_colours[self.parent.line_count]

        x_to_plot = None
        y_to_plot = None
        if self.xClicked == '1000/T':
            x_to_plot = thousand_over_temp
        if self.xClicked == 'T':
            x_to_plot = temperature
        if self.xClicked == 'tau':
            x_to_plot = tau
        if self.xClicked == 'ln(tau)':
            x_to_plot = natural_log_tau
        if self.xClicked == 'amp':
            x_to_plot = amp
        if self.xClicked == 'alpha':
            x_to_plot = alpha
        if self.xClicked == 'beta':
            x_to_plot = beta
        if self.xClicked == 'alpha*beta':
            x_to_plot = AlphaBeta
        if self.yClicked == '1000/T':
            y_to_plot = thousand_over_temp
        if self.yClicked == 'T':
            y_to_plot = temperature
        if self.yClicked == 'tau':
            y_to_plot = tau
        if self.yClicked == 'ln(tau)':
            y_to_plot = natural_log_tau
        if self.yClicked == 'amp':
            y_to_plot = amp
        if self.yClicked == 'alpha':
            y_to_plot = alpha
        if self.yClicked == 'beta':
            y_to_plot = beta
        if self.yClicked == 'alpha*beta':
            y_to_plot = AlphaBeta

        pen = pg.mkPen(color=colour, width=5)
        vft_plot_item = pg.PlotDataItem(x_to_plot, y_to_plot,
                                   pen=pen, symbol=drop_symbols[self.parent.line_count-1],
                                   symbolPen = colour,
                                   symbolBrush = 'white',
                                   symbolSize = 16)

        vft_lines[self.xParent] = vft_plot_item
        self.parent.plotItem.addItem(vft_plot_item)
        self.parent.update_lines()
        self.parent.update_list(self.xParent, line_colours_Q[self.parent.line_count])
        self.parent.legend.addItem(self.parent.plotLines[-1], self.xParent)
        self.close()

class FitDialogue(QMainWindow):
    hn_count = 0
    con_count = 0
    arrhenius_count = 0
    vft_count = 0
    total_fits = 0
    counter = 0
    hn_colours = [None, QtGui.QColor(228,19,47),  QtGui.QColor(13,148,8), QtGui.QColor(8,237,253)]*100
    con_colours = [None, QtGui.QColor(61,19,228), QtGui.QColor(253,8,253), QtGui.QColor(253,172,8)]*100
    def __init__(self, parent=None):
        super(FitDialogue, self).__init__(parent)
        loadUi(ui_path + "fit_window.ui", self)
        self.parent = parent
        self.child = None
        self.setWindowTitle("Fit Dialogue")

        self.func = self.findChild(QAction, "actionFunc")
        self.add = self.findChild(QAction, "actionAdd")
        self.updateButton = self.findChild(QAction, "actionUpdate")
        self.funcTree = self.findChild(QTreeWidget, "tree")


        self.func.triggered.connect(self.func_window)
        self.updateButton.triggered.connect(self.update_fit)
        self.add.triggered.connect(self.add_fits)
        self.actionAdd_Tau.triggered.connect(self.add_tau)

        self.comboBox = QComboBox()
        self.toolBar.addWidget(self.comboBox)
        combo_items = list(vft_dict.keys())
        self.comboBox.addItems(combo_items)



    def add_tau(self):
        if selected_line == None:
            parent = self.funcTree.currentItem()
            if parent.text(0).startswith('hn') == True:
                tau = parent.child(0)
                vft_dict[self.comboBox.currentText()][data_dict[last_added]['temp'][0]] = tau.text(1)
                print(tau.text(1))
        else:
            parent = self.funcTree.topLevelItem(0)
            if parent.text(0).startswith('hn') == True:
                tau = parent.child(0)
                amp = parent.child(1)
                a = parent.child(2)
                b = parent.child(3)
                vft_dict[self.comboBox.currentText()][data_dict[selected_line]['temp'][0]] = [tau.text(1), amp.text(1), a.text(1), b.text(1)]
                print(tau.text(1))
                self.statusbar.showMessage('added succesfully', 1500)

    def check_limiter(self):
        return self.parent.actionLimiter.isChecked()

    def func_window(self):
        self.child = FunctionDialogue(self)
        self.child.show()

    def add_fits(self):
        for i in lines_dict['temp']:
            lines_dict['fits'][i] = lines_dict['temp'][i][0], lines_dict['temp'][i][1]
            self.parent.plotItem.removeItem(lines_dict['temp'][i][0])
            self.parent.plotItem.addItem(lines_dict['fits'][i][0])
            self.parent.update_list_fits(i, lines_dict['fits'][i][1])
            print(lines_dict['fits'][i][1])
        lines_dict['temp'].clear()

    def hn_setup(self):
        global plot_data
# =============================================================================
#         TREE SETUP
# =============================================================================
        tau_value = 1
        amp_value = 1
        a_value = 0.5
        b_value = 0.5
        tau_error = 0
        tau_lower = 0
        tau_upper = np.inf
        amp_value = 1
        amp_error = 0
        amp_lower = 0
        amp_upper = np.inf
        a_value = 0.5
        a_error = 0
        a_lower = 0
        a_upper = 1
        b_value = 0.5
        b_error = 0
        b_lower = 0
        b_upper = 1
        x_lower = 0
        x_upper = np.inf
        self.check_limiter()
        if self.check_limiter() == True:
            print('limiter on...')
            x_lower = low_region
            x_upper = high_region

        FitDialogue.total_fits += 1
        FitDialogue.hn_count += 1
        self.funcTree.insertTopLevelItem(0, QTreeWidgetItem(['hn' + str(FitDialogue.hn_count)]))
        parent_item = self.funcTree.topLevelItem(0)
        parent_item.setExpanded(True)
        parent_item.setForeground(0, FitDialogue.hn_colours[FitDialogue.hn_count])
        for i in range(5):
            parent_item.setBackground(i, QtGui.QColor(199,199,199))
        font = QtGui.QFont()
        font.setBold(True)
        parent_item.setFont(0, font)
        tau_child = QTreeWidgetItem(parent_item, ['tau', str(tau_value), str(tau_error), str(tau_lower), str(tau_upper)])
        amp_child = QTreeWidgetItem(parent_item, ['amp', str(amp_value), str(amp_error), str(amp_lower), str(amp_upper)])
        a_child = QTreeWidgetItem(parent_item, ['a', str(a_value), str(a_error), str(a_lower), str(a_upper)])
        b_child = QTreeWidgetItem(parent_item, ['b', str(b_value), str(b_error), str(b_lower), str(b_upper)])
        x_child = QTreeWidgetItem(parent_item, ['range', '-', '-', str(x_lower), str(x_upper)])
        global hn_children
        hn_children = [tau_child, amp_child, a_child, b_child, x_child]

        for child in hn_children:
            child.setCheckState(5, Qt.Unchecked)
            child.setFlags(child.flags() | Qt.ItemIsEditable)

        self.hn_fit()

    def hn_fit(self):
        global params
        global params_dict
        if self.parent.actionLimiter.isChecked() == True:
            print('limiter on...')
            x_lower = low_region
            x_upper = high_region
            hn_children[4].setText(3, str(x_lower))
            hn_children[4].setText(4, str(x_upper))

        if selected_line == None:
            plot_data = np.column_stack((x_frq, y_eps))
        else:
            x = [float(i) for i in data_dict[selected_line]['frq']]
            y = [float(i) for i in data_dict[selected_line]['eps_db_prime']]
            plot_data = np.column_stack((x, y))
        HN_model = Model(HN_function,prefix = 'HN_1_')
        params = HN_model.make_params()
        params['HN_1_tau'].value = float(hn_children[0].text(1))
        params['HN_1_amp'].value = float(hn_children[1].text(1))
        params['HN_1_alpha'].value = float(hn_children[2].text(1))
        params['HN_1_beta'].value = float(hn_children[3].text(1))

        if hn_children[0].checkState(5) == 2:
            params['HN_1_tau'].vary = False
        if hn_children[1].checkState(5) == 2:
            params['HN_1_amp'].vary = False
        if hn_children[2].checkState(5) == 2:
            params['HN_1_alpha'].vary = False
        if hn_children[3].checkState(5) == 2:
            params['HN_1_beta'].vary = False

        params['HN_1_amp'].min = float(hn_children[1].text(3))
        params['HN_1_tau'].min = float(hn_children[0].text(3))
        params['HN_1_amp'].max = float(hn_children[1].text(4))
        params['HN_1_tau'].max = float(hn_children[0].text(4))
        params['HN_1_alpha'].min = 0
        params['HN_1_alpha'].max = 1

        params['HN_1_beta'].min = 0
        params['HN_1_beta'].max = 1

        x_fit = [x for x in plot_data[:,0] if x > float(hn_children[4].text(3)) and x < float(hn_children[4].text(4))]
        y_fit = [plot_data[i,1] for i,x in enumerate(plot_data[:,0]) if x > float(hn_children[4].text(3)) and x < float(hn_children[4].text(4))]

        colour = FitDialogue.hn_colours[FitDialogue.hn_count]
        fitted_params = HN_model.fit(y_fit,params,x = x_fit)
        params_dict = fitted_params.values
        y_fitted = HN_function(x_frq,fitted_params.values['HN_1_amp'],fitted_params.values['HN_1_tau'],fitted_params.values['HN_1_alpha'],fitted_params.values['HN_1_beta'])
        hn_children[0].setText(1, str(format(params_dict['HN_1_tau'], '.6g')))
        hn_children[1].setText(1, str(format(params_dict['HN_1_amp'], '.6g')))
        hn_children[2].setText(1, str(format(params_dict['HN_1_alpha'], '.6g')))
        hn_children[3].setText(1, str(format(params_dict['HN_1_beta'], '.6g')))
        hn_curve = self.parent.graphArea.plot(x_frq, y_fitted)
        hn_curve.setData(x_frq, y_fitted)
        self.parent.update_lines()
        lines_dict['temp']['hn' + str(FitDialogue.hn_count)] = self.parent.plotLines[-1], colour
        pen = pg.mkPen(color=colour, width=4)
        hn_curve.setPen(pen)
        hn_curve.setZValue(10)


        FitDialogue.counter += 1
        print('fit complete')

    def update_fit(self):

        for i in (lines_dict['temp']):
            self.parent.plotItem.removeItem(lines_dict['temp'][i][0])

        if hn_children != None:
            self.hn_fit()
        if con_children != None:
            self.con_fit()
        if arrhenius_children != None:
            self.arrhenius_fit()
        if vft_children != None:
            self.VFT_fit()

    def con_setup(self):
        x_lower = 0
        x_upper = np.inf
        self.check_limiter()
        if self.check_limiter() == True:
            print('limiter on...')
            x_lower = low_region
            x_upper = high_region
        FitDialogue.total_fits += 1
        FitDialogue.con_count += 1
        self.funcTree.insertTopLevelItem(0, QTreeWidgetItem(['con' + str(FitDialogue.con_count)]))
        parent_item = self.funcTree.topLevelItem(0)
        parent_item.setExpanded(True)
        parent_item.setForeground(0, FitDialogue.con_colours[FitDialogue.con_count])
        for i in range(5):
            parent_item.setBackground(i, QtGui.QColor(199,199,199))
        font = QtGui.QFont()
        font.setBold(True)
        parent_item.setFont(0, font)
        log_value = 10
        log_error = 0
        log_lower = 0
        log_upper = np.inf
        n_value = -1
        n_error = 0
        n_lower = 0
        n_upper = np.inf
        amp_child = QTreeWidgetItem(parent_item, ['amp', str(log_value), str(log_error), str(log_lower), str(log_upper)])
        exp_child = QTreeWidgetItem(parent_item, ['exp', str(n_value), str(n_error), str(n_lower), str(n_upper)])
        x_child = QTreeWidgetItem(parent_item, ['range', '-', '-', str(x_lower), str(x_upper)])

        global con_children
        con_children = [amp_child, exp_child, x_child]

        for child in con_children:
            child.setCheckState(5, Qt.Unchecked)
            child.setFlags(child.flags() | Qt.ItemIsEditable)
        self.con_fit()

    def con_fit(self):
        global params
        global params_dict
        if self.parent.actionLimiter.isChecked() == True:
            print('limiter on...')
            x_lower = low_region
            x_upper = high_region
            con_children[2].setText(3, str(x_lower))
            con_children[2].setText(4, str(x_upper))
        if selected_line == None:
            plot_data = np.column_stack((x_frq, y_eps))
        else:
            x = [float(i) for i in data_dict[selected_line]['frq']]
            y = [float(i) for i in data_dict[selected_line]['eps_db_prime']]
            plot_data = np.column_stack((x, y))
        con_model = Model(cond_function,prefix = 'con_1_')
        params = con_model.make_params()
        params['con_1_amp'].value = float(con_children[0].text(1))
        params['con_1_exp'].value = float(con_children[1].text(1))

        params['con_1_exp'].min = -np.inf
        params['con_1_exp'].max = 0

        if con_children[0].checkState(5) == 2:
            params['con_1_amp'].vary = False
        if con_children[1].checkState(5) == 2:
            params['con_1_exp'].vary = False


        x_fit = [x for x in plot_data[:,0] if x > float(con_children[2].text(3)) and x < float(con_children[2].text(4))]
        y_fit = [plot_data[i,1] for i,x in enumerate(plot_data[:,0]) if x > float(con_children[2].text(3)) and x < float(con_children[2].text(4))]

        colour = FitDialogue.con_colours[FitDialogue.con_count]
        fitted_params = con_model.fit(y_fit,params,x = x_fit)
        params_dict = fitted_params.values
        y_fitted = cond_function(x_frq,fitted_params.values['con_1_amp'],fitted_params.values['con_1_exp'])
        con_children[0].setText(1, str(format(params_dict['con_1_amp'], '.6g')))
        con_children[1].setText(1, str(format(params_dict['con_1_exp'], '.6g')) )
        con_curve = self.parent.graphArea.plot(x_frq, y_fitted, pen=con_colours_rgb[FitDialogue.con_count])
        con_curve.setData(x_frq, y_fitted)
        pen = pg.mkPen(color=colour, width=4)
        con_curve.setPen(pen)

        self.parent.update_lines()
        lines_dict['temp']['con' + str(FitDialogue.con_count)] = self.parent.plotLines[-1], colour


        FitDialogue.counter += 1

    def arrhenius_setup(self):
        x_lower = -np.inf
        x_upper = np.inf
        self.check_limiter()
        if self.check_limiter() == True:
            print('limiter on...')
            x_lower = low_region
            x_upper = high_region
        FitDialogue.total_fits += 1
        FitDialogue.arrhenius_count += 1
        self.funcTree.insertTopLevelItem(0, QTreeWidgetItem(['arrh' + str(FitDialogue.arrhenius_count)]))
        parent_item = self.funcTree.topLevelItem(0)
        parent_item.setExpanded(True)
        parent_item.setForeground(0, FitDialogue.con_colours[FitDialogue.arrhenius_count])
        for i in range(5):
            parent_item.setBackground(i, QtGui.QColor(199,199,199))
        font = QtGui.QFont()
        font.setBold(True)
        parent_item.setFont(0, font)
        const_value = 10e-12
        const_error = 0
        const_lower = 0
        const_upper = np.inf
        ea_value = 1
        ea_error = 0
        ea_lower = 0
        ea_upper = np.inf

        const_child = QTreeWidgetItem(parent_item, ['const', str(const_value), str(const_error), str(const_lower), str(const_upper)])
        ea_child = QTreeWidgetItem(parent_item, ['Ea', str(ea_value), str(ea_error), str(ea_lower), str(ea_upper)])

        x_child = QTreeWidgetItem(parent_item, ['range', '-', '-', str(x_lower), str(x_upper)])

        global arrhenius_children
        arrhenius_children = [const_child, ea_child, x_child]

        for child in arrhenius_children:
            child.setCheckState(5, Qt.Unchecked)
            child.setFlags(child.flags() | Qt.ItemIsEditable)

        self.arrhenius_fit()

    def arrhenius_fit(self):
        global plot_data
        if self.parent.actionLimiter.isChecked() == True:
            print('limiter on...')
            x_lower = low_region
            x_upper = high_region
            arrhenius_children[2].setText(3, str(x_lower))
            arrhenius_children[2].setText(4, str(x_upper))

        if selected_line == None:
            pass
            # x_data = list(sorted(vft_dict))
            # plot_data = np.column_stack((x_frq, y_eps))
        else:
            x = [float(i) for i in vft_values[selected_line][0]]
            y = [float(i) for i in vft_values[selected_line][2]]


            plot_data = np.column_stack((x, y))

        arrhenius_model = Model(arrhenius_function,prefix = 'arrhenius_1_')
        params = arrhenius_model.make_params()
        params['arrhenius_1_const'].value = float(arrhenius_children[0].text(1))
        params['arrhenius_1_ea'].value = float(arrhenius_children[1].text(1))

        if arrhenius_children[0].checkState(5) == 2:
            params['arrhenius_1_const'].vary = False
        if arrhenius_children[1].checkState(5) == 2:
            params['arrhenius_1_ea'].vary = False

        x_fit = [x for x in plot_data[:,0] if x > float(arrhenius_children[2].text(3)) and x < float(arrhenius_children[2].text(4))]
        y_fit = [plot_data[i,1] for i,x in enumerate(plot_data[:,0]) if x > float(arrhenius_children[2].text(3)) and x < float(arrhenius_children[2].text(4))]


        fitted_params = arrhenius_model.fit(y_fit,params,x = x_fit)
        params_dict = fitted_params.values
        y_fitted = arrhenius_function(x,fitted_params.values['arrhenius_1_const'],fitted_params.values['arrhenius_1_ea'])
        arrhenius_children[0].setText(1, str(format(params_dict['arrhenius_1_const'], '.6g')))
        arrhenius_children[1].setText(1, str(format(params_dict['arrhenius_1_ea'], '.6g')) )
        arrhenius_curve = self.parent.graphArea.plot(x, y_fitted, pen=con_colours_rgb[FitDialogue.arrhenius_count])
        arrhenius_curve.setData(x, y_fitted)
        self.parent.update_lines()
        lines_dict['temp']['arrhenius' + str(FitDialogue.arrhenius_count)] = self.parent.plotLines[-1], 'colour'

    def VFT_setup(self):
        x_lower = -np.inf
        x_upper = np.inf
        self.check_limiter()
        if self.check_limiter() == True:
            print('limiter on...')
            x_lower = low_region
            x_upper = high_region
        else:
            x_lower = 0
            x_upper = 10
        FitDialogue.total_fits += 1
        FitDialogue.vft_count += 1
        self.funcTree.insertTopLevelItem(0, QTreeWidgetItem(['vft' + str(FitDialogue.arrhenius_count)]))
        parent_item = self.funcTree.topLevelItem(0)
        parent_item.setExpanded(True)
        parent_item.setForeground(0, FitDialogue.con_colours[FitDialogue.vft_count])
        for i in range(5):
            parent_item.setBackground(i, QtGui.QColor(199,199,199))
        font = QtGui.QFont()
        font.setBold(True)
        parent_item.setFont(0, font)
        tau_nort_value = 1
        tau_nort_error = 0
        tau_nort_lower = 0
        tau_nort_upper = np.inf
        D_value = 1
        D_error = 0
        D_lower = 0
        D_upper = np.inf
        T_nort_value = 1
        T_nort_error = 0
        T_nort_lower = 0
        T_nort_upper = np.inf
        
        
        tau_nort_child = QTreeWidgetItem(parent_item, ['tau_nort', str(tau_nort_value), str(tau_nort_error), str(tau_nort_lower), str(tau_nort_upper)])
        D_child = QTreeWidgetItem(parent_item, ['D', str(D_value), str(D_error), str(D_lower), str(D_upper)])
        T_nort_child = QTreeWidgetItem(parent_item, ['T_nort', str(T_nort_value), str(T_nort_error), str(T_nort_lower), str(T_nort_upper)])

        x_child = QTreeWidgetItem(parent_item, ['range', '-', '-', str(x_lower), str(x_upper)])

        global vft_children
        vft_children = [tau_nort_child, D_child, T_nort_child, x_child]

        for child in vft_children:
            child.setCheckState(5, Qt.Unchecked)
            child.setFlags(child.flags() | Qt.ItemIsEditable)

        self.VFT_fit()
        
        
    def VFT_fit(self):
        global plot_data
        if self.parent.actionLimiter.isChecked() == True:
            print('limiter on...')
            x_lower = low_region
            x_upper = high_region
            vft_children[2].setText(3, str(x_lower))
            vft_children[2].setText(4, str(x_upper))
        else:
            x_lower = 0
            x_upper = 10

        if selected_line == None:
            pass
            # x_data = list(sorted(vft_dict))
            # plot_data = np.column_stack((x_frq, y_eps))
        else:
            x = [float(i) for i in vft_values[selected_line][0]]
            y = [float(i) for i in vft_values[selected_line][1]]
            plot_data = np.column_stack((x, y))
            
        vft_model = Model(VFT_function,prefix = 'vft_1_')
        params = vft_model.make_params()
        params['vft_1_tau_nort'].value = float(vft_children[0].text(1))
        params['vft_1_D'].value = float(vft_children[1].text(1))
        params['vft_1_T_nort'].value = float(vft_children[2].text(1))

        if vft_children[0].checkState(5) == 2:
            params['vft_1_tau_nort'].vary = False
        if vft_children[1].checkState(5) == 2:
            params['vft_1_D'].vary = False
        if vft_children[2].checkState(5) == 2:
            params['vft_1_T_nort'].vary = False

        # params['vft_1_tau_nort'].min = 1
        # params['vft_1_tau_nort'].max = np.inf
        
        # params['vft_1_D'].min = -np.inf
        # params['vft_1_D'].max = 0
        
        x_fit = [x for x in plot_data[:,0] if x > float(vft_children[3].text(3)) and x < float(vft_children[3].text(4))]
        y_fit = [plot_data[i,1] for i,x in enumerate(plot_data[:,0]) if x > float(vft_children[3].text(3)) and x < float(vft_children[3].text(4))]

        colour = FitDialogue.vft_count
        fitted_params = vft_model.fit(y_fit,params,x = x_fit)
        params_dict = fitted_params.values
        y_fitted = VFT_function(x,fitted_params.values['vft_1_tau_nort'],fitted_params.values['vft_1_D'], fitted_params.values['vft_1_T_nort'])
        vft_children[0].setText(1, str(format(params_dict['vft_1_tau_nort'], '.6g')))
        vft_children[1].setText(1, str(format(params_dict['vft_1_D'], '.6g')))
        vft_children[2].setText(1, str(format(params_dict['vft_1_T_nort'], '.6g')))
        vft_curve = self.parent.graphArea.plot(x, y_fitted, pen=con_colours_rgb[FitDialogue.vft_count])
        vft_curve.setData(x, y_fitted)
        self.parent.update_lines()
        lines_dict['temp']['vft' + str(FitDialogue.vft_count)] = self.parent.plotLines[-1], 'colour'
        pen = pg.mkPen(color='red', width=4)
        vft_curve.setPen(pen)
        vft_curve.setZValue(10)



    def closeEvent(self, event):
        for i in (lines_dict['temp']):
              self.parent.plotItem.removeItem(lines_dict['temp'][i][0])
        self.hide()
        FitDialogue.hn_count = 0
        FitDialogue.con_count = 0
        FitDialogue.arrhneius_count = 0
        FitDialogue.total_fits = 0

class FunctionDialogue(QMainWindow):
    def __init__(self, parent=None):
        super(FunctionDialogue, self).__init__(parent)
        loadUi(ui_path + "function_window.ui", self)
        self.parent = parent

        self.hnPage = self.findChild(QWidget, "hnPage")
        self.conPage = self.findChild(QWidget, "conPage")
        self.funcList = self.findChild(QListWidget, "funcList")
        self.stackedWidget = self.findChild(QStackedWidget, "stackedWidget")
        self.addFunction = self.findChild(QPushButton, "addFunction")

        self.funcList.currentRowChanged.connect(self.update_stacked)
        self.addFunction.clicked.connect(self.add_function)
        self.funcList.itemDoubleClicked.connect(self.onDoubleClicked)

    def update_stacked(self, row):
        if row == 0:
            self.stackedWidget.setCurrentIndex(0)
        elif row == 1:
            self.stackedWidget.setCurrentIndex(1)
        elif row == 2:
            self.stackedWidget.setCurrentIndex(2)
        elif row == 3:
            self.stackedWidget.setCurrentIndex(3)

    def add_function(self):
        if self.funcList.currentRow() == 0:
            self.parent.hn_setup()
            self.close()
        elif self.funcList.currentRow() == 1:
            self.parent.con_setup()
            self.close()
        elif self.funcList.currentRow() == 2:
            self.parent.arrhenius_setup()
            self.close()
        elif self.funcList.currentRow() == 3:
            self.parent.VFT_setup()
            self.close()

    @QtCore.pyqtSlot(QtWidgets.QListWidgetItem)
    def onDoubleClicked(self, item):
        if item.text() == 'Havriliak -Negami':
            self.parent.hn_setup()
            self.close()
        if item.text() == 'Conductivity':
            self.parent.con_setup()
            self.close()
        if item.text() == 'Arrhenius':
            self.parent.arrhenius_setup()
            self.close()
        if item.text() == 'VFT':
            self.parent.VFT_setup()
            self.close()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
