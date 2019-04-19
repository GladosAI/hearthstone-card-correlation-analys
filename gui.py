import sys
from untitled import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
from read_json import CardInfo
from PyQt5 import QtGui, QtCore
from relatmatrix import RelatMat

class Hearthstone(QMainWindow, Ui_MainWindow):
    def __init__(self, cardinfo_class, rel_matrix_class):
        super(Hearthstone, self).__init__()
        self.setupUi(self)

        self.cardinfo = cardinfo_class()
        self.rmat = rel_matrix_class(self.cardinfo)

        self.c1_inittable()
        self.c2_inittable()

        self.c1_showlabel(self.c1_table.currentIndex().row())
        self.c1_prev.pressed.connect(self.c1_prev_press)
        self.c1_next.pressed.connect(self.c1_next_press)
        self.c1_table.clicked.connect(self.c1_tableselc)
        self.c1_sbid.clicked.connect(self.c1_sortbyid)
        # self.c1_table.sortByColumn()

        self.c2_showlabel(self.c2_table.currentIndex().row())
        self.c2_prev.pressed.connect(self.c2_prev_press)
        self.c2_next.pressed.connect(self.c2_next_press)
        self.c2_table.clicked.connect(self.c2_tableselc)
        self.c2_sbid.clicked.connect(self.c2_sortbyid)

        self.spinBox.setMaximum(5)
        self.spinBox.setMinimum(0)
        self.showspin()

        self.save.pressed.connect(self.save_but)
        self.load.pressed.connect(self.load_but)
        if self.rmat.corrmode:
            # self.spinBox.se
            return
        self.spinBox.valueChanged.connect(self.setspinbox)


    def save_but(self):
        self.rmat.save_matrix()

    def load_but(self):
        self.rmat.load_matrix()
        self.refrash_tabel()

    def refrash_tabel(self):
        self.c1_retable()
        self.c2_retable()
        self.c1_tableselc()
        self.c2_tableselc()

    def c1_sortbyid(self):
        self.c1_retable()
        self.c1_tableselc()

    def c2_sortbyid(self):
        self.c2_retable()
        self.c2_tableselc()

    def setspinbox(self):
        value = self.spinBox.value()
        self.rmat.change_value(self.get_curr_c1t_id(), self.get_curr_c2t_id(), value)
        self.rmat.change_value(self.get_curr_c2t_id(), self.get_curr_c1t_id(), value)
        # self.showspin()
        self.c1_tablemodel.setItem(self.c1_table.currentIndex().row(), 1, QtGui.QStandardItem(str(value)))
        self.c2_tablemodel.setItem(self.c2_table.currentIndex().row(), 1, QtGui.QStandardItem(str(value)))

    def showspin(self):
        self.spinBox.setValue(self.rmat.find_value(self.get_curr_c1t_id(), self.get_curr_c2t_id()))
        # self.spinBox.show()

    def get_curr_c1t_id(self):
        return int(self.c1_tablemodel.data(self.c1_tablemodel.index(self.c1_table.currentIndex().row(), 3)))

    def get_curr_c2t_id(self):
        return int(self.c2_tablemodel.data(self.c2_tablemodel.index(self.c2_table.currentIndex().row(), 3)))

    def c1_tableselc(self):
        nrow = self.get_curr_c1t_id()
        self.c1_showlabel(nrow)
        self.change_c2t_rel(nrow)
        self.showspin()

    def change_c2t_rel(self, c1_id):
        for i in range(len(self.cardinfo.id_map_card)):
            n_id = self.c2_tablemodel.data(self.c2_tablemodel.index(i, 3))
            self.c2_tablemodel.setItem(i, 1, QtGui.QStandardItem(str(self.rmat.find_value(c1_id, int(n_id)))))

    def c1_prev_press(self):
        nrow = self.c1_table.currentIndex().row()
        if nrow > 0:
            self.c1_table.selectRow(nrow - 1)
        else:
            self.c1_table.selectRow(0)
        self.c1_tableselc()

    def c1_next_press(self):
        nrow = self.c1_table.currentIndex().row()
        if nrow < len(self.cardinfo.id_map_card):
            self.c1_table.selectRow(nrow + 1)
        else:
            self.c1_table.selectRow(len(self.cardinfo.id_map_card))
        self.c1_tableselc()

    def c2_tableselc(self):
        nrow = self.get_curr_c2t_id()
        self.c2_showlabel(nrow)
        self.change_c1t_rel(nrow)
        self.showspin()

    def change_c1t_rel(self, c2_id):
        for i in range(len(self.cardinfo.id_map_card)):
            n_id = self.c1_tablemodel.data(self.c1_tablemodel.index(i, 3))
            self.c1_tablemodel.setItem(i, 1, QtGui.QStandardItem(str(self.rmat.find_value(int(n_id), c2_id))))

    def c2_prev_press(self):
        nrow = self.c2_table.currentIndex().row()
        if nrow > 0:
            self.c2_table.selectRow(nrow - 1)
        else:
            self.c2_table.selectRow(0)
        self.c2_tableselc()

    def c2_next_press(self):
        nrow = self.c2_table.currentIndex().row()
        if nrow < len(self.cardinfo.id_map_card):
            self.c2_table.selectRow(nrow + 1)
        else:
            self.c2_table.selectRow(len(self.cardinfo.id_map_card))
        self.c2_tableselc()

    def keyReleaseEvent(self, event):
        if event.key() == QtCore.Qt.Key_Right:
            self.c2_next_press()
        elif event.key() == QtCore.Qt.Key_Left:
            self.c2_prev_press()
        elif event.key() == QtCore.Qt.Key_Up:
            self.spinBox.stepUp()
        elif event.key() == QtCore.Qt.Key_Down:
            self.spinBox.stepDown()

    def c1_showlabel(self, cid):
        self.c1_name.setText(self.cardinfo.id_map_card[cid].get('name', ''))
        self.c1_text.setText(self.cardinfo.id_map_card[cid].get('text', ''))
        self.c1_attack.setText(str(self.cardinfo.id_map_card[cid].get('attack', '')))
        self.c1_cost.setText(str(self.cardinfo.id_map_card[cid].get('cost', '')))
        self.c1_health.setText(str(self.cardinfo.id_map_card[cid].get('health', '')))
        self.c1_race.setText(self.cardinfo.id_map_card[cid].get('race', ''))
        self.c1_rarity.setText(self.cardinfo.id_map_card[cid].get('rarity', ''))
        self.c1_cardClass.setText(self.cardinfo.id_map_card[cid].get('cardClass', ''))
        self.c1_type.setText(self.cardinfo.id_map_card[cid].get('type', ''))
        self.c1_set.setText(self.cardinfo.id_map_card[cid].get('set', ''))
        self.c1_id.setText(str(cid))

    def c1_inittable(self):
        self.c1_tablemodel = QtGui.QStandardItemModel(self.c1_table)
        self.c1_tablemodel.setColumnCount(4)
        self.c1_tablemodel.setHorizontalHeaderItem(2, QtGui.QStandardItem("cost"))
        self.c1_tablemodel.setHorizontalHeaderItem(0, QtGui.QStandardItem("name"))
        self.c1_tablemodel.setHorizontalHeaderItem(1, QtGui.QStandardItem("relat"))
        self.c1_tablemodel.setHorizontalHeaderItem(3, QtGui.QStandardItem("id"))
        self.c1_table.setModel(self.c1_tablemodel)
        self.c1_table.setColumnWidth(0, 140)
        self.c1_table.setColumnWidth(1, 50)
        self.c1_table.setColumnWidth(2, 40)
        self.c1_table.setColumnWidth(3, 40)

        self.c1_retable()

    def c1_retable(self):
        for i in range(len(self.cardinfo.id_map_card)):
            self.c1_tablemodel.setItem(i, 3, QtGui.QStandardItem(str(i)))
            self.c1_tablemodel.setItem(i, 0, QtGui.QStandardItem(str(self.cardinfo.id_map_card[i]['name'])))
            self.c1_tablemodel.setItem(i, 1, QtGui.QStandardItem(str(self.rmat.find_value(i, 0))))
            self.c1_tablemodel.setItem(i, 2, QtGui.QStandardItem(str(self.cardinfo.id_map_card[i]['cost'])))
        # self.c1_table.setModel(self.c1_tablemodel)
        self.c1_table.selectRow(0)

    def c2_showlabel(self, cid):
        self.c2_name.setText(self.cardinfo.id_map_card[cid].get('name', ''))
        self.c2_text.setText(self.cardinfo.id_map_card[cid].get('text', ''))
        self.c2_attack.setText(str(self.cardinfo.id_map_card[cid].get('attack', '')))
        self.c2_cost.setText(str(self.cardinfo.id_map_card[cid].get('cost', '')))
        self.c2_health.setText(str(self.cardinfo.id_map_card[cid].get('health', '')))
        self.c2_race.setText(self.cardinfo.id_map_card[cid].get('race', ''))
        self.c2_rarity.setText(self.cardinfo.id_map_card[cid].get('rarity', ''))
        self.c2_cardClass.setText(self.cardinfo.id_map_card[cid].get('cardClass', ''))
        self.c2_type.setText(self.cardinfo.id_map_card[cid].get('type', ''))
        self.c2_set.setText(self.cardinfo.id_map_card[cid].get('set', ''))
        self.c2_id.setText(str(cid))

    def c2_inittable(self):
        self.c2_tablemodel = QtGui.QStandardItemModel(self.c2_table)
        self.c2_tablemodel.setColumnCount(4)
        self.c2_tablemodel.setHorizontalHeaderItem(2, QtGui.QStandardItem("cost"))
        self.c2_tablemodel.setHorizontalHeaderItem(0, QtGui.QStandardItem("name"))
        self.c2_tablemodel.setHorizontalHeaderItem(1, QtGui.QStandardItem("relat"))
        self.c2_tablemodel.setHorizontalHeaderItem(3, QtGui.QStandardItem("id"))
        self.c2_table.setModel(self.c2_tablemodel)
        self.c2_table.setColumnWidth(0, 140)
        self.c2_table.setColumnWidth(1, 50)
        self.c2_table.setColumnWidth(2, 40)
        self.c2_table.setColumnWidth(3, 40)
        self.c2_retable()

    def c2_retable(self):
        for i in range(len(self.cardinfo.id_map_card)):
            self.c2_tablemodel.setItem(i, 3, QtGui.QStandardItem(str(i)))
            self.c2_tablemodel.setItem(i, 0, QtGui.QStandardItem(str(self.cardinfo.id_map_card[i]['name'])))
            self.c2_tablemodel.setItem(i, 1, QtGui.QStandardItem(str(self.rmat.find_value(0, i))))
            self.c2_tablemodel.setItem(i, 2, QtGui.QStandardItem(str(self.cardinfo.id_map_card[i]['cost'])))
        self.c2_table.selectRow(0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    h = Hearthstone(CardInfo, RelatMat)
    h.show()
    sys.exit(app.exec_())