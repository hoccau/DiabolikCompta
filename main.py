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

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.initUI()

    def initUI(self):

        menubar = self.menuBar()

        exitAction = QAction(QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(qApp.quit)
        viewdbAction = QAction(QIcon('db.png'), '&Voir', self)
        viewdbAction.triggered.connect(self.change_view)
        addFournisseurAction = QAction(QIcon('fournisseur.png'), '&Fournisseur', self)
        addFournisseurAction.triggered.connect(self.addFournisseur)
        addCodeComptaAction = QAction(QIcon('codecompta.png'), '&Code compta', self)
        addCodeComptaAction.triggered.connect(self.addCodeCompta)

        fileMenu = menubar.addMenu('&Fichier')
        fileMenu.addAction(exitAction)
        view_menu = menubar.addMenu('&Vue')
        view_menu.addAction(viewdbAction)
        addMenu = menubar.addMenu('&Ajouter')
        addMenu.addAction(addFournisseurAction)
        addMenu.addAction(addCodeComptaAction)

        self.statusBar().showMessage('Ready')
        self.show()

        self.model = Model(self)
        self.retrieve_db()
        self.form = Form(self)
        self.setCentralWidget(self.form)

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

    def change_view(self):
        print "changed!"

    def addFournisseur(self):
        name, ok = QInputDialog.getText(self, 'Input Dialog',
            'Nom du fournisseur:')
        if ok and name != "":
            res = self.model.add_fournisseur(name)
            if res:
                self.form.refresh_fournisseurs()
            else:
                QMessageBox.warning(self, "Erreur", "Erreur de requette dans la base")

    def addCodeCompta(self):
        name, code, ok = CodeComptaDialog.getCode()
        print name, code, ok
        if ok and name != "":
            self.model.add_code_compta(code, name)


                    
if __name__ == '__main__':
    import sys, os
    
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())


