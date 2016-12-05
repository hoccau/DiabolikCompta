#!/usr/bin/python3
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
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        
        self.initUI()

    def initUI(self):

        self.setWindowTitle("Diabolik Compta")
        menubar = self.menuBar()

        exitAction = self.add_action('&Quitter', qApp.quit, 'Ctrl+Q')
        openAction = self.add_action('&Ouvrir', self.open_db, 'Ctrl+O')
        delRowAction = self.add_action('&Supprimer la ligne', self.remove_current_row)
        addFormAction = self.add_action('&Pièce comptable', self.addDatas)
        addFournisseurAction = self.add_action('&Fournisseur', self.addFournisseur)
        addCodeComptaAction = self.add_action('&Code compta', self.addCodeCompta)
        addInputAction = self.add_action("Entrée d'argent", self.add_input)
        setInfosAction = self.add_action('Editer les infos du centre', self.set_infos)
        ViewRapportAction = self.add_action('Rapport', self.viewRapport)
        exportPdfAction = self.add_action('Exporter un rapport', self.export_pdf)

        fileMenu = menubar.addMenu('&Fichier')
        fileMenu.addAction(openAction)
        fileMenu.addAction(exportPdfAction)
        fileMenu.addAction(exitAction)
        edit_menu = menubar.addMenu('&Édition')
        edit_menu.addAction(delRowAction)
        edit_menu.addAction(setInfosAction)
        view_menu = menubar.addMenu('&Vue')
        view_menu.addAction(ViewRapportAction)
        addMenu = menubar.addMenu('&Ajouter')
        addMenu.addAction(addFormAction)
        addMenu.addAction(addFournisseurAction)
        addMenu.addAction(addCodeComptaAction)
        addMenu.addAction(addInputAction)

        self.statusBar().showMessage('Ready')
        self.model = Model(self)

        self.right_dock = QDockWidget('Informations Générales', self)
        self.right_dock.setFeatures(QDockWidget.NoDockWidgetFeatures)

        self.addDockWidget(Qt.RightDockWidgetArea, self.right_dock)

        self.setMinimumSize(1024,600)
        self.show()
        
        db_found = self.retrieve_db()
        if db_found:
            self.create_tables_views()
        
    def create_tables_views(self):
        main_tab_widget = QTabWidget()
        self.pieces_comptables_view = self.create_table_view(
            self.model.tables['pieces_comptables'])
        self.subdivisions_view = self.create_table_view(self.model.tables['subdivisions'])
        self.inputs_view = self.create_table_view(self.model.tables['inputs'])

        main_tab_widget.addTab(self.pieces_comptables_view, "Pièces comptables")
        main_tab_widget.addTab(self.subdivisions_view, "Subdivisions")
        main_tab_widget.addTab(self.inputs_view, "Entrées d'argent")
        self.setCentralWidget(main_tab_widget)

        v = QTableView()
        v.setModel(self.model.g_model)
        v.setEditTriggers(QAbstractItemView.NoEditTriggers)
        #grid.addWidget(v)
        self.right_dock.setWidget(v)

    def create_table_view(self, model):
        view = QTableView()
        view.setModel(model)
        view.setItemDelegate(QSqlRelationalDelegate())
        return view

    def add_action(self, name, function_name, shortcut=None):
        action = QAction(name, self)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(function_name)
        return action

    def viewRapport(self):
        RapportDialog(self)

    def remove_current_row(self):
        row = self.pieces_comptables_view.currentIndex().row()
        #model = self.mainView.currentIndex().model()
        #row_id = model.index(row, 0).data()
        print("row to remove:", row)
        self.model.tables['pieces_comptables'].removeRow(row)
        self.model.tables['pieces_comptables'].select()
        #self.model.qt_table_compta.update_table_model()

    def open_db(self):
        file_name = QFileDialog.getOpenFileName(self, 'Open File')
        if file_name[0]:
            self.model.connect_db(file_name[0])

    def retrieve_db(self):
        files = os.listdir('./')
        files = [x for x in files if x.split('.')[-1] == 'db']

        if len(files) == 1:
            QMessageBox.information(self, "Base trouvée","Base de donnée : "+files[0])
            self.model.connect_db(files[0])
            return True
        
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
                self.set_infos()
                return True

            if reponse == QMessageBox.No:
                return False

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

    def set_infos(self):
        InfosCentreDialog(self)

    def export_pdf(self):
        filename, _format = QFileDialog.getSaveFileName(
            self, "Exporter le rapport", None, 'PDF(*.pdf)')
        if filename:
            if filename[-4:] != '.pdf':
                filename += '.pdf'
            import export
            export.create_pdf(filename, model=self.model)

    def addDatas(self):
        self.form = Form(self)
        self.form.show()

    def addFournisseur(self):
        name, ok = QInputDialog.getText(self, 'Fournisseur',
            'Nom du fournisseur:')
        if ok and name != "":
            res = self.model.add({'nom':name}, 'fournisseurs')
            if res == True:
                return True
            elif res == "UNIQUE constraint failed: fournisseurs.NOM":
                QMessageBox.warning(self, "Erreur", "Ce nom existe déjà.")
            else:
                QMessageBox.warning(self, "Erreur", "Erreur de requette inconnue!")

    def addCodeCompta(self):
        name, code, ok = CodeComptaDialog.getCode()
        if ok and name != "":
            datas = {'code':code, 'nom':name}
            response = self.model.add(datas, 'codecompta')
            if response == "UNIQUE constraint failed: codecompta.CODE":
                QMessageBox.warning(self, "Erreur", "Ce code existe déjà")
            #else:
                #self.form.refresh_codeCompta()
                #self.model.update_table_model()

    def add_input(self):
        res = AddInputDialog(self)

if __name__ == '__main__':
    import sys, os
    
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())
