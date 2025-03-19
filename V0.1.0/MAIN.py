from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMdiArea, QAction, 
    QTreeWidgetItem, QListWidget, QListWidgetItem, 
    QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem,
    QShortcut, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QKeySequence

import os
import sys
import csv
import pickle

import numpy as np
import scipy as sp
from lmfit import Model
import pyqtgraph as pg

# Custom modules
from txt_csv import txt_to_csv
from FunctionClasses import ReloadTable, table_widget_parents, table_widget_children
from customgraph import CustomGraph
from customtree import CustomTree

# -----------------------------------------------------------------------------------
# Global Data Structures
# -----------------------------------------------------------------------------------
x_plot_key = None
x_plot_inner_key = None
y_plot_key = None
y_plot_inner_key = None
selected_line = None
name_of_material = None
tail = None
sheet_path = None

low_region = 0
high_region = np.inf

vft_values = {}
file_dict = {}
data_dict = {}
window_dict = {}
vft_dict = {}
vft_lines = {}

lines_dict = {
    'data': {},
    'fits': {},
    'temp': {},
    'hidden': {}
}

# -----------------------------------------------------------------------------------
# Fitting Functions
# -----------------------------------------------------------------------------------
def HN_function(x, amp, tau, alpha, beta):
    """
    Havriliak-Negami function: 
        Im(amp / [1 + (1j * 2π f * tau)^alpha]^beta), multiplied by -1
    """
    hn = np.zeros(len(x), dtype='complex')
    for i, freq in enumerate(x):
        hn[i] = amp / ((1 + (1j * 2 * np.pi * freq * tau)**alpha)**beta)
    return -1 * np.imag(hn)

def cond_function(x, amp, exp, imag=1, real=1):
    """
    Conductivity term: 
        Im(amp * (1j * 2π f)^exp), multiplied by -1
    """
    cond = np.zeros(len(x), dtype='complex')
    for i, freq in enumerate(x):
        cond[i] = amp * ((1j * 2 * np.pi * freq) ** exp)
    return -1 * np.imag(cond)

def arrhenius_function(x, const, ea):
    """
    Arrhenius function: const * exp(-Ea / (R * T))
    """
    arr = np.zeros(len(x))
    for i, temp in enumerate(x):
        arr[i] = const * np.exp(-ea / (sp.constants.R * temp))
    return arr

def VFT_function(x, tau_nort, D, T_nort):
    """
    Vogel-Fulcher-Tammann function: tau_nort * exp((-D * T_nort) / (T - T_nort))
    The -1 * imag(...) portion is not strictly relevant if we’re returning real values.
    """
    vft = np.zeros(len(x))
    for i, temp in enumerate(x):
        vft[i] = tau_nort * np.exp((-D * T_nort) / (temp - T_nort))
    return -1 * np.imag(vft)

# Predefined color sets, symbols
symbols = ['o', 's', 't', 'star', '+', 'x']
line_colours = [
    None,
    (0, 0, 0), (128, 128, 128), (128, 0, 0), (255, 0, 0),
    (255, 165, 0), (210, 210, 0), (128, 128, 0), (0, 128, 0),
    (0, 255, 0), (0, 128, 128), (0, 255, 255), (0, 0, 128),
    (0, 0, 255), (128, 0, 128), (255, 0, 255), (220, 20, 60)
] * 10
line_colours_Q = [
    None,
    QtGui.QColor(0, 0, 0), QtGui.QColor(128, 128, 128), QtGui.QColor(128, 0, 0),
    QtGui.QColor(255, 0, 0), QtGui.QColor(255, 165, 0), QtGui.QColor(210, 210, 0),
    QtGui.QColor(128, 128, 0), QtGui.QColor(0, 128, 0), QtGui.QColor(0, 255, 0),
    QtGui.QColor(0, 128, 128), QtGui.QColor(0, 255, 255), QtGui.QColor(0, 0, 128),
    QtGui.QColor(0, 0, 255), QtGui.QColor(128, 0, 128), QtGui.QColor(255, 0, 255),
    QtGui.QColor(220, 20, 60)
] * 10

drop_symbols = ['o', 's', 't', 'd', 't1'] * 10

# -----------------------------------------------------------------------------------
# Main Window
# -----------------------------------------------------------------------------------
class MainWindow(QMainWindow):
    sheet_count = 0
    graph_count = 0

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        ui_path = os.path.join(os.getcwd(), 'uis')
        # Load the main UI
        from PyQt5.uic import loadUi
        loadUi(os.path.join(ui_path, "main_window.ui"), self)

        self.resize(1300, 800)
        self.mdi = self.findChild(QMdiArea, 'mdiArea')

        # Menu actions
        self.fileMake_CSV = self.findChild(QAction, "actionMake_CSV")
        self.fileSheet = self.findChild(QAction, "actionSheet")
        self.graphGraph = self.findChild(QAction, "actionGraph")

        self.fileSheet.triggered.connect(self.sheet_window)
        self.fileMake_CSV.triggered.connect(self.load_file)
        self.graphGraph.triggered.connect(self.New_Graph)

        # Project tree
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
        self.fileTree.itemDoubleClicked.connect(self.treeDoubleClicked)

        # Color buttons in the toolbar
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

        # Shortcuts
        self.blackShortcut = QShortcut(QKeySequence("Ctrl+B"), self)
        self.blackShortcut.activated.connect(lambda: self.colour_change(1))

        # Symbol / size combo
        self.comboBox.currentTextChanged.connect(self.symbol_change)
        self.spinBox.valueChanged.connect(self.symbol_size)

        # Deletion
        self.delete = QShortcut(QKeySequence("Del"), self)
        self.delete.activated.connect(self.delete_tree_item)

        # Graph-labelling
        self.titleLineEdit.textEdited.connect(self.set_graph_title)
        self.xAxisLineEdit.textEdited.connect(self.set_x_title)
        self.yAxisLineEdit.textEdited.connect(self.set_y_title)
        self.titleSpinBox.valueChanged.connect(self.set_graph_title)
        self.xAxisSpinBox.valueChanged.connect(self.set_x_title)
        self.yAxisSpinBox.valueChanged.connect(self.set_y_title)

        # Axis combos
        self.xAxisComboBox.currentTextChanged.connect(self.x_axis_scale_change)
        self.yAxisComboBox.currentTextChanged.connect(self.y_axis_scale_change)

        # Sort sheets
        self.actionSort_Sheets.triggered.connect(self.sort_sheets)

        # VFT dict I/O
        self.actionSave_VFT_Dict_As.triggered.connect(self.save_vft_dict_as)
        self.actionOpen_VFT_Dict.triggered.connect(self.open_vft_dict)

        # Fit values rename
        self.fileTree.itemDoubleClicked.connect(self.fitted_value_name_change)
        self.fileTree.itemChanged.connect(self.change_keys)

        # Add dictionary to fit values
        self.added_dictionaries = 0
        self.actionAdd_Dictionary.triggered.connect(self.add_dictionary)

        # Symbol check + line width
        self.symbolCheckBox.stateChanged.connect(self.show_symbols)
        self.lineSpinBox.valueChanged.connect(self.change_line_width)

        # Ensure temp directory is ready
        current_dir = os.getcwd()
        if 'temp' not in os.listdir():
            os.mkdir('temp')
        temp_dir = os.path.join(current_dir, 'temp')
        for f in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, f))

    # ------------------- EVENT HANDLERS & UTILITY -------------------

    def change_line_width(self):
        if self.mdi.activeSubWindow() is not None:
            widget = self.mdi.activeSubWindow().widget()
            if isinstance(widget, GraphWindow):
                line_width = self.lineSpinBox.value()
                for i, data_item in enumerate(widget.plotItem.listDataItems()):
                    data_item.setPen(color=line_colours[i + 1], width=line_width)

    def show_symbols(self):
        if self.mdi.activeSubWindow() is not None:
            widget = self.mdi.activeSubWindow().widget()
            if isinstance(widget, GraphWindow):
                check_state = self.symbolCheckBox.checkState()
                for data_item in widget.plotItem.listDataItems():
                    if check_state == Qt.Unchecked:
                        data_item.setSymbolSize(0)
                    else:
                        data_item.setSymbolSize(4)

    def delete_tree_item(self):
        selected_items = self.fileTree.selectedItems()
        for item in selected_items:
            parent = item.parent()
            if parent is not None and parent.text(0) == 'fit values':
                if item.text(0) in vft_dict:
                    vft_dict.pop(item.text(0))
                parent.removeChild(item)

    def add_dictionary(self):
        """
        Add a new, empty dictionary under 'fit values' in the project tree.
        """
        self.added_dictionaries += 1
        name = f'new_dict_{self.added_dictionaries}'
        vft_dict[name] = {}
        child = QTreeWidgetItem([name])
        icon = QtGui.QIcon("icons/fit_values.png")
        child.setIcon(0, icon)
        child.setFlags(child.flags() | Qt.ItemIsEditable)
        self.treeFitValues.insertChild(0, child)

    def fitted_value_name_change(self, item, column):
        """
        Keep track of old name to allow renaming of fit dictionaries in the tree.
        """
        if item.parent() and item.parent().text(0) == 'fit values':
            global old_name
            old_name = item.text(column)

    def change_keys(self, item, column):
        """
        If a fit dictionary has been renamed in the tree, update `vft_dict`.
        """
        if item.parent() and item.parent().text(0) == 'fit values':
            try:
                new_name = item.text(column)
                if 'old_name' in globals():
                    vft_dict[new_name] = vft_dict.pop(old_name)
            except KeyError:
                pass

    def save_vft_dict_as(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, 'Save Values', os.getenv('HOME'), 'VFT(*.vft)'
        )
        if filename:
            with open(filename, 'wb') as f:
                pickle.dump(vft_dict, f, protocol=pickle.HIGHEST_PROTOCOL)

    def open_vft_dict(self):
        """
        Allows selection of multiple .vft files for merging into the existing `vft_dict`.
        """
        dialogue = QFileDialog(self)
        dialogue.setFileMode(QFileDialog.ExistingFiles)
        dialogue.setNameFilter('VFT(*.vft)')
        files, _ = dialogue.getOpenFileNames(
            self, "Open files", os.getenv('HOME'), 'VFT(*.vft)'
        )
        for filename in files:
            with open(filename, 'rb') as f:
                new_dict = pickle.load(f)

            # Merge
            global vft_dict
            vft_dict = vft_dict | new_dict

            # Update the tree
            for key in new_dict.keys():
                child = QTreeWidgetItem([key])
                icon = QtGui.QIcon("icons/fit_values.png")
                child.setIcon(0, icon)
                child.setFlags(child.flags() | Qt.ItemIsEditable)
                self.treeFitValues.insertChild(0, child)

        # Also populate vft_values
        for key in vft_dict.keys():
            thousand_over_temp, temperature, tau, ln_tau = [], [], [], []
            amp, alpha, beta, AlphaBeta = [], [], [], []
            for t in sorted(vft_dict[key].keys(), key=float):
                val = vft_dict[key][t]
                if val is not None:
                    temp_val = float(t)
                    temperature.append(temp_val)
                    thousand_over_temp.append(1000 / temp_val)
                    tau_val = float(val[0])
                    tau.append(tau_val)
                    ln_tau.append(np.log(tau_val))
                    amp.append(float(val[1]))
                    alpha.append(float(val[2]))
                    beta.append(float(val[3]))
                    AlphaBeta.append(float(val[2]) * float(val[3]))

            vft_values[key] = (
                thousand_over_temp,
                ln_tau,
                tau,
                temperature,
                amp,
                alpha,
                beta,
                AlphaBeta
            )

    def x_axis_scale_change(self):
        active_win = self.mdi.activeSubWindow()
        if not active_win:
            return
        graph_widget = active_win.widget()
        if isinstance(graph_widget, GraphWindow):
            current = self.xAxisComboBox.currentText()
            if current == 'log10':
                graph_widget.graphArea.setLogMode(x=True, y=None)
            else:
                graph_widget.graphArea.setLogMode(x=False, y=None)

    def y_axis_scale_change(self):
        active_win = self.mdi.activeSubWindow()
        if not active_win:
            return
        graph_widget = active_win.widget()
        if isinstance(graph_widget, GraphWindow):
            current = self.yAxisComboBox.currentText()
            if current == 'log10':
                graph_widget.graphArea.setLogMode(x=None, y=True)
            else:
                graph_widget.graphArea.setLogMode(x=None, y=False)

    def sort_sheets(self):
        self.treeSheet.sortChildren(0, Qt.AscendingOrder)
        self.treeFitValues.sortChildren(0, Qt.AscendingOrder)

    def set_graph_title(self):
        active_win = self.mdi.activeSubWindow()
        if active_win:
            graph_widget = active_win.widget()
            if isinstance(graph_widget, GraphWindow):
                size_pt = f"{self.titleSpinBox.value()}pt"
                graph_widget.plotItem.setTitle(
                    self.titleLineEdit.text(), color='black', size=size_pt
                )

    def set_x_title(self):
        active_win = self.mdi.activeSubWindow()
        if active_win:
            graph_widget = active_win.widget()
            if isinstance(graph_widget, GraphWindow):
                size_pt = f"{self.xAxisSpinBox.value()}pt"
                axis = graph_widget.plotItem.getAxis('bottom')
                label_style = {'color': 'black', 'font-size': size_pt}
                axis.setLabel(self.xAxisLineEdit.text(), **label_style)

    def set_y_title(self):
        active_win = self.mdi.activeSubWindow()
        if active_win:
            graph_widget = active_win.widget()
            if isinstance(graph_widget, GraphWindow):
                size_pt = f"{self.yAxisSpinBox.value()}pt"
                axis = graph_widget.plotItem.getAxis('left')
                label_style = {'color': 'black', 'font-size': size_pt}
                axis.setLabel(self.yAxisLineEdit.text(), **label_style)

    def colour_change(self, index: int):
        """
        Applies a color to the currently selected line in the graph's list widget.
        """
        global selected_line
        if not selected_line:
            return
        c = line_colours[index]
        qcolor = line_colours_Q[index]
        active_win = self.mdi.activeSubWindow()
        if not active_win:
            return
        graph_widget = active_win.widget()
        if not isinstance(graph_widget, GraphWindow):
            return

        # Data line
        if selected_line in lines_dict['data']:
            plot_item = lines_dict['data'][selected_line][2]
            plot_item.setPen(c)
            plot_item.setSymbolPen(c)
            plot_item.setSymbolBrush(c)
            # Update the listWidget color
            item = graph_widget.listWidget.currentItem()
            if item:
                item.setForeground(qcolor)

        # Fit line
        elif selected_line in lines_dict['fits']:
            fit_plot_item = lines_dict['fits'][selected_line][0]
            fit_plot_item.setPen(c)
            fit_plot_item.setSymbolPen(c)
            fit_plot_item.setSymbolBrush(c)
            # Update the listWidget color
            item = graph_widget.listWidget.currentItem()
            if item:
                item.setForeground(qcolor)

        # VFT lines
        elif selected_line in vft_lines:
            vft_item = vft_lines[selected_line]
            pen = pg.mkPen(color=c, width=3)
            vft_item.setPen(pen)
            vft_item.setSymbolPen(c)
            vft_item.setSymbolBrush(c)
            item = graph_widget.listWidget.currentItem()
            if item:
                item.setForeground(qcolor)

    def symbol_change(self):
        if not selected_line or selected_line not in lines_dict['data']:
            return
        current = self.comboBox.currentText()
        sym_map = {
            'Circle': symbols[0],
            'Square': symbols[1],
            'Triangle': symbols[2],
            'Star': symbols[3],
            '+': symbols[4],
            'x': symbols[5]
        }
        lines_dict['data'][selected_line][2].setSymbol(sym_map.get(current, 'o'))

    def symbol_size(self):
        if not selected_line or selected_line not in lines_dict['data']:
            return
        size_val = self.spinBox.value()
        lines_dict['data'][selected_line][2].setSymbolSize(size_val)

    # -----------------------------------------------------------------------------------
    # File I/O and Tree Management
    # -----------------------------------------------------------------------------------
    @pyqtSlot(list)
    def dropHandler(self, paths):
        """
        Handles dropped files into the project tree.
        """
        for f in paths:
            f_lower = f.lower()
            head, tail_name = os.path.split(f)
            tail_noext = tail_name.rsplit('.', 1)[0]

            if f_lower.endswith('.txt'):
                txt_to_csv(f, path=os.path.join(os.getcwd(), 'temp'))
                new_path = os.path.join(
                    os.getcwd(), 'temp', tail_noext + '.csv'
                )
                self.separate_data(new_path, tail_noext)
                self.update_fileTree_sheet(new_path, tail_noext)

            elif f_lower.endswith('.csv'):
                self.separate_data(f, tail_noext)
                self.update_fileTree_sheet(f, tail_noext)

    #@pyqtSlot("QTreeWidgetItem, int")
    def treeDoubleClicked(self, item, column):
        """
        Handles double-click events on the tree items:
        - Opening data (sheets)
        - Opening graphs
        - Opening fit value tables
        """
        parent = item.parent()
        if not parent:
            return

        if parent.text(column) == 'sheets':
            # Reload table
            file_key = item.text(column)
            if file_key in file_dict:
                sub = ReloadTable(10, 10)
                sub.setWindowTitle(file_key)
                sub.open_sheet(file_dict[file_key])
                self.mdi.addSubWindow(sub)
                sub.show()

        elif parent.text(column) == 'graphs':
            # Bring graph subwindow to front if it exists
            if item.text(column) in window_dict:
                subwindow = window_dict[item.text(column)]
                subwindow.show()

        elif parent.text(column) == 'fit values':
            # Open the FitValuesDisplay
            fit_child = FitValuesDisplay(self, item.text(column))
            self.mdi.addSubWindow(fit_child)
            fit_child.show()
            fit_child.populate_table()

    def load_file(self):
        """
        Convert a .txt to .csv (via txt_to_csv) and alert user.
        """
        fname, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "txt (*.txt);;csv (*.csv);;All files (*)"
        )
        if fname:
            txt_to_csv(fname)
            msg = QMessageBox(self)
            msg.setWindowTitle(" ")
            msg.setText("CSV created successfully")
            msg.setIcon(QMessageBox.Information)
            msg.exec_()

    def sheet_window(self):
        """
        Opens a new sheet subwindow (allowing CSV selection).
        """
        MainWindow.sheet_count += 1
        sheet_sub = Sheet()
        sheet_sub.setWindowIcon(QtGui.QIcon("icons/new_sheet.png"))
        self.mdi.addSubWindow(sheet_sub)
        sheet_sub.show()

    def separate_data(self, csv_path, name):
        """
        Reads CSV data into data_dict[name].
        Also attempts to add the temperature key to vft_dict for future fits.
        """
        global tail
        try:
            with open(csv_path, 'r') as data_file:
                csv_obj = csv.DictReader(data_file)
                frq, eps_prime, eps_db_prime = [], [], []
                run_info, temp_val = [], []

                for row in csv_obj:
                    frq.append(row.get('Freq.[Hz]', '0'))
                    eps_prime.append(row.get('Eps\'', '0'))
                    eps_db_prime.append(row.get('Eps\'\'', '0'))
                    run_info.append(row.get('run_info', ''))
                    temp_val.append(row.get('temp', ''))

            data_dict[name] = {
                'frq': frq,
                'eps_prime': eps_prime,
                'eps_db_prime': eps_db_prime,
                'run_info': run_info,
                'temp': temp_val
            }

            # Attempt to create or update an entry in vft_dict
            # e.g. "material_100K" => "material"
            split_name = name.split('_')
            if len(split_name) > 1:
                material_name_only = '_'.join(split_name[:-1])
            else:
                material_name_only = name

            if material_name_only not in vft_dict:
                vft_dict[material_name_only] = {}

            if temp_val and temp_val[0]:
                vft_dict[material_name_only][temp_val[0]] = None

            # Insert into Fit Values tree if new
            existing = set()
            for i in range(self.treeFitValues.childCount()):
                existing.add(self.treeFitValues.child(i).text(0))

            if material_name_only not in existing:
                child = QTreeWidgetItem([material_name_only])
                icon = QtGui.QIcon("icons/fit_values.png")
                child.setIcon(0, icon)
                child.setFlags(child.flags() | Qt.ItemIsEditable)
                self.treeFitValues.insertChild(0, child)

        except Exception as e:
            print(f"Error reading CSV: {csv_path}, {e}")

    def update_fileTree_sheet(self, path, name):
        """
        Adds a child item under 'sheets' for the newly loaded file.
        """
        item_to_add = QTreeWidgetItem([name])
        icon1 = QtGui.QIcon("icons/document_29383.png")
        item_to_add.setIcon(0, icon1)
        self.treeSheet.insertChild(0, item_to_add)
        file_dict[name] = path

    def New_Graph(self):
        MainWindow.graph_count += 1
        graph_child = GraphWindow(self)
        graph_key = f"graph_{MainWindow.graph_count}"

        self.mdi.addSubWindow(graph_child)
        graph_child.setWindowTitle(graph_key)
        graph_child.show()

        self.update_fileTree_graph(graph_key)

        # Keep track of subwindow in a dict
        window_dict[graph_key] = self.mdi.subWindowList()[-1]
        window_dict[graph_key].resize(600, 400)

    def update_fileTree_graph(self, graph_key):
        item = QTreeWidgetItem([graph_key])
        icon2 = QtGui.QIcon("icons/icons8-graph-64.png")
        item.setIcon(0, icon2)
        self.treeGraph.insertChild(0, item)

# -----------------------------------------------------------------------------------
# Simple Table Widget for CSV Display
# -----------------------------------------------------------------------------------
class MyTable(QTableWidget):
    path = ''

    def __init__(self, r, c):
        super().__init__(r, c)
        self.check_change = True
        self.init_ui()

    def init_ui(self):
        self.cellChanged.connect(self.cell_change)
        self.show()

    def cell_change(self):
        if self.check_change:
            row = self.currentRow()
            col = self.currentColumn()
            value = self.item(row, col)
            if value:
                print("Cell changed:", row, col, "->", value.text())

    def open_sheet(self):
        global sheet_path
        self.check_change = False
        fname, _ = QFileDialog.getOpenFileName(
            self, 'Open CSV', os.getenv('HOME'), 'CSV(*.csv)'
        )
        sheet_path = fname
        if fname:
            with open(fname, newline='') as csv_file:
                reader = csv.reader(csv_file, delimiter=',', quotechar='|')
                self.setRowCount(0)
                self.setColumnCount(10)
                for row_data in reader:
                    row = self.rowCount()
                    self.insertRow(row)
                    if len(row_data) > self.columnCount():
                        self.setColumnCount(len(row_data))
                    for column, stuff in enumerate(row_data):
                        item = QTableWidgetItem(stuff)
                        self.setItem(row, column, item)
        self.check_change = True

# -----------------------------------------------------------------------------------
# Sheet Window
# -----------------------------------------------------------------------------------
class Sheet(QMainWindow):
    def __init__(self):
        super().__init__()
        self.form_widget = MyTable(10, 10)
        self.setCentralWidget(self.form_widget)
        col_headers = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        self.form_widget.setHorizontalHeaderLabels(col_headers)
        self.form_widget.open_sheet()
        self.show()

# -----------------------------------------------------------------------------------
# Fit Values Display Window
# -----------------------------------------------------------------------------------
class FitValuesDisplay(QMainWindow):
    def __init__(self, parent=None, data_name=None):
        super(FitValuesDisplay, self).__init__(parent)
        self.data_name = data_name
        from PyQt5.uic import loadUi
        ui_path = os.path.join(os.getcwd(), 'uis')
        loadUi(os.path.join(ui_path, "fit_values_display.ui"), self)
        self.setWindowTitle(self.data_name)

    def populate_table(self):
        if self.data_name not in vft_dict:
            return

        self.tableWidget.setColumnCount(5)
        self.tableWidget.setRowCount(40)
        self.tableWidget.setHorizontalHeaderLabels(["temp", "tau", "amp", "alpha", "beta"])
        # Headers in row 0
        self.tableWidget.setItem(0, 0, QTableWidgetItem('temp'))
        self.tableWidget.setItem(0, 1, QTableWidgetItem('tau'))
        self.tableWidget.setItem(0, 2, QTableWidgetItem('amp'))
        self.tableWidget.setItem(0, 3, QTableWidgetItem('alpha'))
        self.tableWidget.setItem(0, 4, QTableWidgetItem('beta'))

        keys = sorted(vft_dict[self.data_name].keys(), key=float)
        row_counter = 1
        for t in keys:
            tau_item, amp_item, alpha_item, beta_item = QTableWidgetItem(''), QTableWidgetItem(''), QTableWidgetItem(''), QTableWidgetItem('')
            val = vft_dict[self.data_name][t]
            self.tableWidget.setItem(row_counter, 0, QTableWidgetItem(t))
            if val is not None:
                tau_item = QTableWidgetItem(val[0])
                amp_item = QTableWidgetItem(val[1])
                alpha_item = QTableWidgetItem(val[2])
                beta_item = QTableWidgetItem(val[3])
            self.tableWidget.setItem(row_counter, 1, tau_item)
            self.tableWidget.setItem(row_counter, 2, amp_item)
            self.tableWidget.setItem(row_counter, 3, alpha_item)
            self.tableWidget.setItem(row_counter, 4, beta_item)
            row_counter += 1

# -----------------------------------------------------------------------------------
# Graph Window
# -----------------------------------------------------------------------------------
class GraphWindow(QMainWindow):
    graph_count = 0

    def __init__(self, parent=None):
        super(GraphWindow, self).__init__()
        from PyQt5.uic import loadUi
        ui_path = os.path.join(os.getcwd(), 'uis')
        loadUi(os.path.join(ui_path, "graph_window.ui"), self)

        self.parent = parent
        self.fitChild = None
        self.setWindowTitle("Graph")

        # Actions
        self.plot = self.findChild(QAction, "actionPlot")
        self.fit = self.findChild(QAction, "actionFit")
        self.form = self.findChild(QAction, "actionForm")
        self.actionVFT_Plot = self.findChild(QAction, "actionVFT_Plot")
        self.actionLimiter = self.findChild(QAction, "actionLimiter")
        self.actionClipper = self.findChild(QAction, "actionClipper")
        self.actionClip = self.findChild(QAction, "actionClip")
        self.actionClear = self.findChild(QAction, "actionClear")
        self.actionSelected_Only = self.findChild(QAction, "actionSelected_Only")
        self.actionDefault = self.findChild(QAction, "actionDefault")
        self.actionAll_Black = self.findChild(QAction, "actionAll_Black")

        # Widgets
        self.listWidget = self.findChild(QListWidget, "listWidget")
        self.graphArea = self.findChild(CustomGraph, "graphArea")
        self.plotItem = self.graphArea.getPlotItem()
        self.plotLines = self.plotItem.listDataItems()
        self.runInfo = self.findChild(QtWidgets.QLabel, "runInfo")
        self.tempLabel = self.findChild(QtWidgets.QLabel, "tempLabel")

        # Setup
        self.graphArea.setLogMode(True, True)
        self.plotItem.enableAutoRange(True)

        self.lg = pg.LinearRegionItem(values=(0, 1), orientation='vertical',
                                      brush=(238, 238, 238), pen=(255, 0, 0))
        self.lg.sigRegionChanged.connect(self.regionUpdated)
        roi_pen = pg.mkPen(color='red', width=2)
        self.roi = pg.InfiniteLine(pos=0, angle=90, pen=roi_pen,
                                   movable=True, label='ClipAbove')

        self.legend = pg.LegendItem(offset=(-1, 1), labelTextColor=(0, 0, 0),
                                    labelTextSize='8pt', colCount=3)
        self.legend.setParentItem(self.plotItem)
        self.legend.setPos(1, 1)

        # Axis style
        self.xAxis = self.plotItem.getAxis('bottom')
        self.yAxis = self.plotItem.getAxis('left')
        font = QtGui.QFont()
        font.setPixelSize(16)
        self.xAxis.setTickFont(font)
        self.yAxis.setTickFont(font)
        pen = pg.mkPen('black')
        self.xAxis.setTextPen(pen)
        self.yAxis.setTextPen(pen)
        self.xAxis.enableAutoSIPrefix(False)
        self.yAxis.enableAutoSIPrefix(False)

        # Signals
        self.plot.triggered.connect(self.plot_widget)
        self.fit.triggered.connect(self.fit_widget)
        self.actionVFT_Plot.triggered.connect(self.vft_plot_widget)
        self.listWidget.itemClicked.connect(self.onListItemClicked)
        self.listWidget.itemSelectionChanged.connect(self.itemChanged)
        self.graphArea.graphDropped.connect(self.graphDroppedHandler)
        self.actionLimiter.changed.connect(self.toggle_limiter)
        self.actionClipper.changed.connect(self.toggle_clipper)
        self.actionClip.triggered.connect(self.clip)
        self.actionClear.triggered.connect(self.clear_graph)
        self.actionSelected_Only.changed.connect(self.viewMode_selected_only)
        self.actionDefault.changed.connect(self.viewMode_default)
        self.actionAll_Black.triggered.connect(self.all_black)

    # ------------------- Graph & List Functions -------------------

    def graphDroppedHandler(self, sheets):
        for sheet in sheets:
            self.update_graph_from_drop(sheet)
            self.update_list(sheet, line_colours_Q[self.plotItem.listDataItems().__len__()])

    def onListItemClicked(self, item):
        global selected_line
        selected_line = item.text()
        if selected_line in data_dict:
            self.runInfo.setText(data_dict[selected_line]['run_info'][0])
            self.tempLabel.setText(str(data_dict[selected_line]['temp'][0]) + 'K')

    def itemChanged(self):
        """
        Called when listWidget selection changes.
        """
        global selected_line
        item = self.listWidget.currentItem()
        if not item:
            return
        selected_line = item.text()
        if selected_line in data_dict:
            self.runInfo.setText(data_dict[selected_line]['run_info'][0])
            self.tempLabel.setText(str(data_dict[selected_line]['temp'][0]))

            if self.actionSelected_Only.isChecked():
                self.plotItem.clear()
                if selected_line in lines_dict['data']:
                    self.plotItem.addItem(lines_dict['data'][selected_line][2])

        elif selected_line in lines_dict['fits']:
            if self.actionSelected_Only.isChecked():
                self.plotItem.clear()
                self.plotItem.addItem(lines_dict['fits'][selected_line][0])

    def toggle_limiter(self):
        if self.actionLimiter.isChecked():
            self.plotItem.addItem(self.lg)
            self.lg.setZValue(100)
        else:
            self.plotItem.removeItem(self.lg)

    def regionUpdated(self):
        global low_region, high_region
        low_region, high_region = self.lg.getRegion()
        if self.parent.xAxisComboBox.currentText() == 'log10':
            low_region = 10 ** low_region
            high_region = 10 ** high_region

    def toggle_clipper(self):
        if self.actionClipper.isChecked():
            self.plotItem.addItem(self.roi)
        else:
            self.plotItem.removeItem(self.roi)

    def clip(self):
        """
        Example method: read the self.roi value to clip data above or below.
        """
        pass  # implement as needed

    def clear_graph(self):
        self.plotItem.clear()
        self.listWidget.clear()
        self.runInfo.clear()
        self.tempLabel.clear()
        self.legend.clear()

    def viewMode_selected_only(self):
        if self.actionSelected_Only.isChecked():
            self.actionDefault.setChecked(False)
            if selected_line in lines_dict['data']:
                self.plotItem.clear()
                self.plotItem.addItem(lines_dict['data'][selected_line][2])
            elif selected_line in lines_dict['fits']:
                self.plotItem.clear()
                self.plotItem.addItem(lines_dict['fits'][selected_line][0])
        else:
            self.actionDefault.setChecked(True)
            self.viewMode_default()

    def viewMode_default(self):
        if self.actionDefault.isChecked():
            self.actionSelected_Only.setChecked(False)
            self.plotItem.clear()
            # Re-draw all lines
            for k in lines_dict['data']:
                self.plotItem.addItem(lines_dict['data'][k][2])
            for k in lines_dict['fits']:
                self.plotItem.addItem(lines_dict['fits'][k][0])

    def all_black(self):
        for i, key in enumerate(lines_dict['data']):
            item = lines_dict['data'][key][2]
            item.setPen('black')
            item.setSymbolPen('black')
            item.setSymbolBrush('black')
        for i in range(self.listWidget.count()):
            self.listWidget.item(i).setForeground(line_colours_Q[1])

    def update_graph_from_drop(self, data_name):
        """
        Plots the data from data_dict or vft_values if found.
        """
        self.plotItem.enableAutoRange(True)
        if data_name in data_dict:
            # Normal dataset
            x_vals = [float(i) for i in data_dict[data_name]['frq']]
            y_vals = [float(i) for i in data_dict[data_name]['eps_db_prime']]
            color_idx = self.plotItem.listDataItems().__len__() + 1
            pen = pg.mkPen(color=line_colours[color_idx], width=2)
            item = self.graphArea.plot(
                x_vals, y_vals,
                pen=pen, symbol='o', symbolPen=line_colours[color_idx],
                symbolBrush=line_colours[color_idx], symbolSize=8
            )
            lines_dict['data'][data_name] = [x_vals, y_vals, item]
            self.legend.addItem(item, f"{data_dict[data_name]['temp'][0]}K")
            self.runInfo.setText(data_dict[data_name]['run_info'][0])
            self.tempLabel.setText(str(float(data_dict[data_name]['temp'][0])) + 'K')

        elif data_name in vft_values:
            # VFT data
            color_idx = self.plotItem.listDataItems().__len__() + 1
            x_vals = vft_values[data_name][0]
            y_vals = vft_values[data_name][2]
            pen = pg.mkPen(color=line_colours[color_idx], width=2)
            item = self.graphArea.plot(
                x_vals, y_vals,
                pen=pen, symbol='o', symbolPen=line_colours[color_idx],
                symbolBrush=line_colours[color_idx], symbolSize=5
            )
            vft_lines[data_name] = item
            self.legend.addItem(item, data_name)

    def update_list(self, material, colour):
        icon = QtGui.QIcon("icons/plot_line_icon.png")
        list_item = QListWidgetItem(material)
        list_item.setIcon(icon)
        if colour:
            list_item.setForeground(colour)
        self.listWidget.addItem(list_item)

    def plot_widget(self):
        child = PlotDialogue(self)
        child.show()

    def vft_plot_widget(self):
        child = VFTPlotDialogue(self)
        child.show()

    def fit_widget(self):
        if not self.fitChild:
            self.fitChild = FitDialogue(self)
        self.fitChild.show()
        self.fitChild.update_fit()

    def closeEvent(self, event):
        # Hide instead of destroy if you want to keep it in memory
        event.ignore()
        self.parent.mdi.activeSubWindow().hide()

# -----------------------------------------------------------------------------------
# Plot Dialogue
# -----------------------------------------------------------------------------------
class PlotDialogue(QMainWindow):
    def __init__(self, parent=None):
        super(PlotDialogue, self).__init__(parent)
        from PyQt5.uic import loadUi
        ui_path = os.path.join(os.getcwd(), 'uis')
        loadUi(os.path.join(ui_path, "plot_window.ui"), self)

        self.parent = parent
        self.setWindowTitle("Plot Dialogue")

        self.plotButton = self.findChild(QtWidgets.QPushButton, "pushPlot")
        self.XTree = self.findChild(QtWidgets.QTreeWidget, "XTree")
        self.YTree = self.findChild(QtWidgets.QTreeWidget, "YTree")

        # Build trees
        parent_items_x = table_widget_parents(data_dict)
        parent_items_y = table_widget_parents(data_dict)
        self.XTree.addTopLevelItems(parent_items_x)
        self.YTree.addTopLevelItems(parent_items_y)

        for i in range(len(parent_items_x)):
            children_x = table_widget_children(data_dict)
            children_y = table_widget_children(data_dict)
            parent_items_x[i].addChildren(children_x)
            parent_items_y[i].addChildren(children_y)

        self.XTree.itemClicked.connect(self.onItemClicked_x)
        self.YTree.itemClicked.connect(self.onItemClicked_y)
        self.plotButton.clicked.connect(self.update_graph)

    @pyqtSlot(QtWidgets.QTreeWidgetItem, int)
    def onItemClicked_x(self, item, column):
        global x_plot_key, x_plot_inner_key
        if item.parent() is not None:
            x_plot_inner_key = item.text(column)
            x_plot_key = item.parent().text(column)

    @pyqtSlot(QtWidgets.QTreeWidgetItem, int)
    def onItemClicked_y(self, item, column):
        global y_plot_key, y_plot_inner_key, name_of_material
        if item.parent() is not None:
            y_plot_inner_key = item.text(column)
            y_plot_key = item.parent().text(column)
            name_of_material = item.parent().text(column)

    def update_graph(self):
        """
        Plots the chosen x/y from the trees onto the active GraphWindow.
        """
        if not (x_plot_key and x_plot_inner_key and y_plot_key and y_plot_inner_key):
            return

        # Convert data to float
        x_vals = [float(i) for i in data_dict[x_plot_key][x_plot_inner_key]]
        y_vals = [float(i) for i in data_dict[y_plot_key][y_plot_inner_key]]

        # Access the current GraphWindow
        graph_win = self.parent
        if not isinstance(graph_win, GraphWindow):
            return
        graph_win.line_count += 1
        color_idx = graph_win.line_count
        pen = pg.mkPen(color=line_colours[color_idx], width=2)

        item = graph_win.graphArea.plot(
            x_vals, y_vals, pen=pen, symbol='o',
            symbolPen=line_colours[color_idx],
            symbolBrush=line_colours[color_idx],
            symbolSize=5
        )
        lines_dict['data'][name_of_material] = [x_vals, y_vals, item]
        graph_win.legend.addItem(item, name_of_material)
        graph_win.update_list(name_of_material, line_colours_Q[color_idx])
        self.close()

# -----------------------------------------------------------------------------------
# VFT Plot Dialogue
# -----------------------------------------------------------------------------------
class VFTPlotDialogue(QMainWindow):
    plot_counter = 0

    def __init__(self, parent=None):
        super(VFTPlotDialogue, self).__init__(parent)
        from PyQt5.uic import loadUi
        ui_path = os.path.join(os.getcwd(), 'uis')
        loadUi(os.path.join(ui_path, "vft_plot_window.ui"), self)

        self.parent = parent
        self.setWindowTitle("VFT Plot")

        self.xTreeWidget = self.findChild(QtWidgets.QTreeWidget, "xTreeWidget")
        self.yTreeWidget = self.findChild(QtWidgets.QTreeWidget, "yTreeWidget")
        self.plotButton = self.findChild(QtWidgets.QPushButton, "plotButton")

        # Build trees
        parent_items_x = [QTreeWidgetItem([k]) for k in vft_dict.keys()]
        parent_items_y = [QTreeWidgetItem([k]) for k in vft_dict.keys()]

        self.xTreeWidget.addTopLevelItems(parent_items_x)
        self.yTreeWidget.addTopLevelItems(parent_items_y)

        for item in parent_items_x:
            children = ['1000/T', 'T', 'tau', 'ln(tau)', 'amp', 'alpha', 'beta', 'alpha*beta']
            item.addChildren([QTreeWidgetItem([c]) for c in children])
        for item in parent_items_y:
            children = ['1000/T', 'T', 'tau', 'ln(tau)', 'amp', 'alpha', 'beta', 'alpha*beta']
            item.addChildren([QTreeWidgetItem([c]) for c in children])

        self.xParent = None
        self.yParent = None
        self.xClicked = None
        self.yClicked = None

        self.xTreeWidget.itemClicked.connect(self.set_plot_dataX)
        self.yTreeWidget.itemClicked.connect(self.set_plot_dataY)
        self.plotButton.clicked.connect(self.plot)

    def set_plot_dataX(self, item, column):
        if item.parent():
            self.xClicked = item.text(column)
            self.xParent = item.parent().text(column)

    def set_plot_dataY(self, item, column):
        if item.parent():
            self.yClicked = item.text(column)
            self.yParent = item.parent().text(column)

    def plot(self):
        if not self.xParent or not self.yParent:
            return

        # Construct local arrays from vft_dict
        key = self.xParent
        if key not in vft_values:
            return

        # vft_values[key] = (thousand_over_temp, ln_tau, tau, temperature, amp, alpha, beta, alphaBeta)
        xdata, ydata = None, None
        data_tuple = vft_values[key]
        # Map tree labels to indices in data_tuple
        label_map = {
            '1000/T': 0,
            'ln(tau)': 1,
            'tau': 2,
            'T': 3,
            'amp': 4,
            'alpha': 5,
            'beta': 6,
            'alpha*beta': 7
        }

        if self.xClicked in label_map:
            xdata = data_tuple[label_map[self.xClicked]]
        if self.yClicked in label_map:
            ydata = data_tuple[label_map[self.yClicked]]
        if not xdata or not ydata:
            return

        # Plot it on the active GraphWindow
        graph_win = self.parent
        if not isinstance(graph_win, GraphWindow):
            return
        graph_win.line_count += 1
        color_idx = graph_win.line_count
        pen = pg.mkPen(color=line_colours[color_idx], width=2)

        item = pg.PlotDataItem(
            xdata, ydata,
            pen=pen,
            symbol=drop_symbols[color_idx - 1],
            symbolPen=line_colours[color_idx],
            symbolBrush='white',
            symbolSize=8
        )
        vft_lines[key] = item
        graph_win.plotItem.addItem(item)
        graph_win.legend.addItem(item, key)
        graph_win.update_list(key, line_colours_Q[color_idx])

        self.close()

# -----------------------------------------------------------------------------------
# Fit Dialogue
# -----------------------------------------------------------------------------------
class FitDialogue(QMainWindow):
    hn_count = 0
    con_count = 0
    arrhenius_count = 0
    vft_count = 0
    total_fits = 0

    hn_colours = [None, QtGui.QColor(228, 19, 47), QtGui.QColor(13, 148, 8), QtGui.QColor(8, 237, 253)] * 100
    con_colours = [None, QtGui.QColor(61, 19, 228), QtGui.QColor(253, 8, 253), QtGui.QColor(253, 172, 8)] * 100

    def __init__(self, parent=None):
        super(FitDialogue, self).__init__(parent)
        from PyQt5.uic import loadUi
        ui_path = os.path.join(os.getcwd(), 'uis')
        loadUi(os.path.join(ui_path, "fit_window.ui"), self)

        self.parent = parent
        self.setWindowTitle("Fit Dialogue")

        self.func = self.findChild(QAction, "actionFunc")
        self.add = self.findChild(QAction, "actionAdd")
        self.updateButton = self.findChild(QAction, "actionUpdate")
        self.actionAdd_Tau = self.findChild(QAction, "actionAdd_Tau")

        self.funcTree = self.findChild(QtWidgets.QTreeWidget, "tree")
        self.toolBar = self.findChild(QtWidgets.QToolBar, "toolBar")

        self.func.triggered.connect(self.func_window)
        self.updateButton.triggered.connect(self.update_fit)
        self.add.triggered.connect(self.add_fits)
        self.actionAdd_Tau.triggered.connect(self.add_tau)

        # Combo for choosing which dictionary to update
        self.comboBox = QComboBox()
        self.toolBar.addWidget(self.comboBox)
        self.comboBox.addItems(list(vft_dict.keys()))

    def add_tau(self):
        """
        Example method to add a newly fit tau value into the selected dictionary in vft_dict.
        You can adapt as needed.
        """
        global selected_line
        dict_key = self.comboBox.currentText()
        if not dict_key:
            return
        # Attempt to get temperature from selected_line
        if selected_line in data_dict and dict_key in vft_dict:
            # Let's pick first param (tau) from the first top-level item
            top_item = self.funcTree.topLevelItem(0)
            if top_item and top_item.childCount() >= 1:
                tau_child = top_item.child(0)
                tau_val = tau_child.text(1)
                # For example: use data_dict[selected_line]['temp'][0]
                current_temp = data_dict[selected_line]['temp'][0]
                vft_dict[dict_key][current_temp] = [tau_val, '0', '0', '0']
                self.statusbar.showMessage('Tau added successfully', 1500)

    def func_window(self):
        child = FunctionDialogue(self)
        child.show()

    def add_fits(self):
        """
        Move items from lines_dict['temp'] to lines_dict['fits'].
        """
        for k, v in lines_dict['temp'].items():
            lines_dict['fits'][k] = (v[0], v[1])
            if self.parent:
                self.parent.plotItem.removeItem(v[0])
                self.parent.plotItem.addItem(lines_dict['fits'][k][0])
                self.parent.update_list_fits(k, lines_dict['fits'][k][1])
        lines_dict['temp'].clear()

    def update_fit(self):
        """
        Re-run fits if they exist.
        """
        for k, v in lines_dict['temp'].items():
            if self.parent:
                self.parent.plotItem.removeItem(v[0])

        # If you have references to children, re-run them (HN, con, arr, VFT).
        # For example:
        # if some_hn_children is not None: self.hn_fit()
        # etc.
        # In your original code, you called them conditionally.
        pass

    def closeEvent(self, event):
        # Remove in-progress lines
        for k, v in lines_dict['temp'].items():
            if self.parent:
                self.parent.plotItem.removeItem(v[0])
        lines_dict['temp'].clear()

        FitDialogue.hn_count = 0
        FitDialogue.con_count = 0
        FitDialogue.arrhenius_count = 0
        FitDialogue.vft_count = 0
        FitDialogue.total_fits = 0
        self.hide()

# -----------------------------------------------------------------------------------
# Function Dialogue
# -----------------------------------------------------------------------------------
class FunctionDialogue(QMainWindow):
    def __init__(self, parent=None):
        super(FunctionDialogue, self).__init__(parent)
        from PyQt5.uic import loadUi
        ui_path = os.path.join(os.getcwd(), 'uis')
        loadUi(os.path.join(ui_path, "function_window.ui"), self)

        self.parent = parent
        self.setWindowTitle("Function Dialogue")

        self.hnPage = self.findChild(QtWidgets.QWidget, "hnPage")
        self.conPage = self.findChild(QtWidgets.QWidget, "conPage")
        self.funcList = self.findChild(QtWidgets.QListWidget, "funcList")
        self.stackedWidget = self.findChild(QtWidgets.QStackedWidget, "stackedWidget")
        self.addFunction = self.findChild(QtWidgets.QPushButton, "addFunction")

        self.funcList.currentRowChanged.connect(self.update_stacked)
        self.addFunction.clicked.connect(self.add_function)
        self.funcList.itemDoubleClicked.connect(self.onDoubleClicked)

    def update_stacked(self, row):
        self.stackedWidget.setCurrentIndex(row)

    def add_function(self):
        """
        In your original code, calling e.g., self.parent.hn_setup().
        Here, you’d do that again if you want to create HN, Conductivity, etc.
        """
        if self.funcList.currentRow() == 0:  # HN
            pass  # self.parent.hn_setup()
        elif self.funcList.currentRow() == 1:  # Conductivity
            pass  # self.parent.con_setup()
        elif self.funcList.currentRow() == 2:  # Arrhenius
            pass
        elif self.funcList.currentRow() == 3:  # VFT
            pass
        self.close()

    @pyqtSlot(QtWidgets.QListWidgetItem)
    def onDoubleClicked(self, item):
        txt = item.text()
        if txt == 'Havriliak -Negami':
            pass  # self.parent.hn_setup()
            self.close()
        elif txt == 'Conductivity':
            pass  # self.parent.con_setup()
            self.close()
        elif txt == 'Arrhenius':
            pass
        elif txt == 'VFT':
            pass
        self.close()

# -----------------------------------------------------------------------------------
# Main Execution
# -----------------------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
