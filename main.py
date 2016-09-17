#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Diabolik Compta
Logiciel de comptabilité léger pour centre de vacances
"""

from PyQt5 import QtSql
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from model import Model
from views import *
from PyQt5.QtSql import QSqlRelationalDelegate

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.initUI()

    def initUI(self):

        menubar = self.menuBar()

        exitAction = QAction(QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(qApp.quit)
        openAction = QAction(QIcon('open.png'), '&Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.triggered.connect(self.open_db)
        cumAction = QAction(QIcon('db.png'), '&Cumul', self)
        cumAction.triggered.connect(self.show_cumul)
        showRowAction = QAction(QIcon('db.png'), '&Row', self)
        showRowAction.triggered.connect(self.show_row)
        delRowAction = QAction(QIcon('db.png'), '&Supprimer la ligne', self)
        delRowAction.triggered.connect(self.remove_current_row)
        addFormAction = QAction(QIcon('form.png'), '&Ligne de comptabilité', self)
        addFormAction.triggered.connect(self.addDatas)
        addFournisseurAction = QAction(QIcon('fournisseur.png'), '&Fournisseur', self)
        addFournisseurAction.triggered.connect(self.addFournisseur)
        addCodeComptaAction = QAction(QIcon('codecompta.png'), '&Code compta', self)
        addCodeComptaAction.triggered.connect(self.addCodeCompta)

        fileMenu = menubar.addMenu('&Fichier')
        fileMenu.addAction(openAction)
        fileMenu.addAction(exitAction)
        edit_menu = menubar.addMenu('&Édition')
        edit_menu.addAction(delRowAction)
        view_menu = menubar.addMenu('&Vue')
        view_menu.addAction(cumAction)
        view_menu.addAction(showRowAction)
        #view_menu.addAction(viewFormAction)
        addMenu = menubar.addMenu('&Ajouter')
        addMenu.addAction(addFormAction)
        addMenu.addAction(addFournisseurAction)
        addMenu.addAction(addCodeComptaAction)

        self.statusBar().showMessage('Ready')
        self.setMinimumSize(850,300)
        self.show()

        self.model = Model(self)
        self.retrieve_db()
        self.form = Form(self)

        self.mainView = QTableView(self)
        self.mainView.setModel(self.model.qt_table_compta)
        self.mainView.setItemDelegate(QSqlRelationalDelegate())
        self.setCentralWidget(self.mainView)

    def remove_current_row(self):
        row = self.mainView.currentIndex().row()
        model = self.mainView.currentIndex().model()
        row_id = model.index(row, 0).data()
        print "row to remove:", row
        self.model.qt_table_compta.removeRow(row)
        self.model.update_cumul(row_id + 1)
        self.model.update_table_model()

    def show_row(self):
        row = self.mainView.currentIndex().row()
        model = self.mainView.currentIndex().model()
        print "id:", model.index(row,0).data(), "m2:", m2
        print "row", row
        
    def show_cumul(self):
        self.model.update_cumul(3)

    def open_db(self):
        file_name = QFileDialog.getOpenFileName(self, 'Open File')
        if file_name[0]:
            self.model.connect_db(file_name[0])

    def retrieve_db(self):
        files = os.listdir('./')
        files = filter(lambda x: x.split('.')[-1] == 'db', files)

        if len(files) == 1:
            QMessageBox.information(self, "Base trouvée","Base de donnée : "+files[0])
            self.model.connect_db(files[0])
        
        elif len(files) == 0:
            reponse = QMessageBox.question(
                None,
                'message',
                'Pas de base de données trouvée. Faut-il en créer une nouvelle ?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
                )
            if reponse == QMessageBox.Yes:
                db_name = self.input_db_name()
                self.model.create_db(db_name)
            if reponse == QMessageBox.No:
                return None

        elif len(files) > 1:
            #QMessageBox.critical(None, "Plusieurs bases trouvées", "Plusieurs bases de données trouvées. Je ne sais que faire...")
            combo = QComboBox(self)
            for db_name in files:
                combo.addItem(db_name)

    def input_db_name(self):
        name, ok = QInputDialog.getText(self, 'Input Dialog', 
            'Entrez le nom de la base:')
        if ok and name != "":
            if name.split('.')[-1] != 'db':
                name = name + '.db'
            return name

    def switch_to_form_view(self):
        self.form = Form(self) #because: http://stackoverflow.com/questions/17914960/pyqt-runtimeerror-wrapped-c-c-object-has-been-deleted
        self.setCentralWidget(self.form)

    def switch_to_db_view(self):
        self.mainView = QTableView(self)
        self.mainView.setModel(self.model.qt_table_compta)
        self.setCentralWidget(self.mainView)

    def addDatas(self):
        self.form.show()

    def addFournisseur(self):
        name, ok = QInputDialog.getText(self, 'Input Dialog',
            'Nom du fournisseur:')
        if ok and name != "":
            res = self.model.add_fournisseur(name)
            if res == True:
                self.form.refresh_fournisseurs()
                self.model.update_table_model()
            elif res == "UNIQUE constraint failed: fournisseurs.NOM":
                QMessageBox.warning(self, "Erreur", "Ce nom existe déjà.")
            else:
                QMessageBox.warning(self, "Erreur", "Erreur de requette inconnue!")

    def addCodeCompta(self):
        name, code, ok = CodeComptaDialog.getCode()
        print name, code, ok
        if ok and name != "":
            response = self.model.add_code_compta(code, name)
            if response == "UNIQUE constraint failed: codecompta.CODE":
                QMessageBox.warning(self, "Erreur", "Ce code existe déjà")
            else:
                self.form.refresh_codeCompta()
                self.model.update_table_model()

                    
if __name__ == '__main__':
    import sys, os
    
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())


