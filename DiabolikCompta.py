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
from PyQt5.QtCore import Qt, QTranslator, QLocale, QLibraryInfo, QThread, QSettings
import sys, os, configparser

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.config = QSettings("Kidivid", "DiabolikCompta")
        self.initUI()

    def initUI(self):

        self.setWindowTitle("Diabolik Compta")
        menubar = self.menuBar()

        exitAction = self.add_action('&Quitter', qApp.quit, 'Ctrl+Q')
        newAction = self.add_action('Nouveau', self.create_new_db, 'Ctrl+N')
        openAction = self.add_action('&Ouvrir', self.open_db, 'Ctrl+O')
        aboutAction = self.add_action('à propos', self.about_d)

        self.db_actions = {}
        self.db_actions['delRow'] = self.add_action('&Supprimer la ligne', self.remove_current_row)
        self.db_actions['addForm'] = self.add_action('&Pièce comptable', self.add_piece_comptable)
        self.db_actions['addFournisseur'] = self.add_action('&Fournisseur', self.addFournisseur)
        self.db_actions['addCodeCompta'] = self.add_action('&Code compta', self.addCodeCompta)
        self.db_actions['addInput'] = self.add_action("Entrée d'argent", self.add_input)
        self.db_actions['setInfos'] = self.add_action('Editer les infos du centre', self.set_infos)
        self.db_actions['editPiece'] = self.add_action('Editer la piece', self.edit_piece)
        self.db_actions['ViewRapport'] = self.add_action('Rapport', self.viewRapport)
        self.db_actions['exportPdf'] = self.add_action('Exporter un rapport PDF', self.export_pdf)
        self.db_actions['exportXlsx'] = self.add_action('Exporter un fichier Excel', self.export_excel)
        self.db_actions['close'] = self.add_action('&Fermer', self.close_db, 'Ctrl+W')
        

        fileMenu = menubar.addMenu('&Fichier')
        fileMenu.addAction(newAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(self.db_actions['close'])
        fileMenu.addAction(self.db_actions['exportPdf'])
        fileMenu.addAction(self.db_actions['exportXlsx'])
        fileMenu.addAction(exitAction)
        edit_menu = menubar.addMenu('&Édition')
        edit_menu.addAction(self.db_actions['delRow'])
        edit_menu.addAction(self.db_actions['editPiece'])
        edit_menu.addAction(self.db_actions['setInfos'])
        view_menu = menubar.addMenu('&Vue')
        view_menu.addAction(self.db_actions['ViewRapport'])
        addMenu = menubar.addMenu('&Ajouter')
        addMenu.addAction(self.db_actions['addForm'])
        addMenu.addAction(self.db_actions['addFournisseur'])
        addMenu.addAction(self.db_actions['addCodeCompta'])
        addMenu.addAction(self.db_actions['addInput'])
        aideMenu = menubar.addMenu('&Aide')
        aideMenu.addAction(aboutAction)

        self.enable_db_actions(False)

        self.statusBar().showMessage('Ready')
        self.model = Model(self)

        self.right_dock = QDockWidget('Informations Générales', self)
        self.right_dock.setFeatures(QDockWidget.NoDockWidgetFeatures)

        self.addDockWidget(Qt.RightDockWidgetArea, self.right_dock)

        self.setMinimumSize(1024,600)
        self.show()
        
        self.retrieve_db()

    def enable_db_actions(self, b = True):
        for name, action in self.db_actions.items():
            action.setEnabled(b)

    def create_tables_views(self):
        self.tabs = QTabWidget()
        self.pieces_comptables_view = self.create_table_view(
            self.model.tables['pieces_comptables'])
        #self.pieces_comptables_view = self.create_table_view(self.model.filter_model)
        self.subdivisions_view = self.create_table_view(self.model.tables['subdivisions'])
        self.inputs_view = self.create_table_view(self.model.tables['inputs'])
        self.tabs.addTab(self.pieces_comptables_view, "Pièces comptables")
        self.tabs.addTab(self.subdivisions_view, "Subdivisions")
        self.tabs.addTab(self.inputs_view, "Entrées d'argent")
        self.setCentralWidget(self.tabs)

        layout = QVBoxLayout()
        for k, g_model in self.model.general_results.items():
            table = QTableView()
            table.setModel(g_model.model)
            table.resizeColumnsToContents()
            table.verticalHeader().hide()
            table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            layout.addWidget(table)
        self.right_col = QWidget()
        self.right_col.setLayout(layout)
        self.right_dock.setWidget(self.right_col)

    def create_table_view(self, model):
        view = QTableView()
        view.setModel(model)
        view.setItemDelegate(QSqlRelationalDelegate())
        view.resizeColumnsToContents()
        view.setSortingEnabled(True)
        view.setEditTriggers(QAbstractItemView.NoEditTriggers)
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
        reponse = QMessageBox.question(
            None,
            'Sûr(e)?',
            'Vous êtes sur le point de supprimer définitivement une\
            pièce comptable ainsi que toutes les subdivisions associées.\
            Êtes-vous sûr(e) ?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
            )
        if reponse == QMessageBox.Yes:
            self.model.tables['pieces_comptables'].removeRow(row)
            self.model.tables['pieces_comptables'].select()
            self.model.tables['subdivisions'].select()

    def open_db(self):
        file_name = QFileDialog.getOpenFileName(self, 'Open File')
        if file_name[0]:
            self.connect_db(file_name[0])

    def close_db(self):
        self.enable_db_actions(False)
        self.model.db.close()
        self.tabs.close()
        self.right_col.close()

    def retrieve_db(self):
        path = self.config.value("lastdbpath")
        if path:
            if os.path.exists(path):
                self.connect_db(path)
        
    def create_new_db(self):
        code, ok = QInputDialog.getInt(self, 'Code centre',
            'Entrez le code de votre centre:')
        if ok and code != '':
            db_name, format_ = QFileDialog.getSaveFileName(
                self,
                "Enregistrer une nouvelle base",
                None,
                'DB(*.db)')
            if db_name:
                if db_name.split('.')[-1] != 'db':
                    db_name += '.db'
                progress_dialog = WaitingDialog(
                    self,
                    self.model,
                    db_name,
                    code)
                progress_dialog.resize(200, 90)
                if progress_dialog.exec_():
                    self.connect_db(db_name)
                    self.set_infos()

    def connect_db(self, db_path):
        self.model.connect_db(db_path)
        self.statusBar().showMessage('Connecté sur : '+db_path)
        self.config.setValue("lastdbpath", db_path)
        self.create_tables_views()
        self.enable_db_actions(True)

    def set_infos(self):
        InfosCentreDialog(self)

    def export_pdf(self):
        filename, _format = QFileDialog.getSaveFileName(
            self, "Exporter le rapport", None, 'PDF(*.pdf)')
        if filename:
            if filename[-4:] != '.pdf':
                filename += '.pdf'
            import export_pdf
            export_pdf.create_pdf(filename, model=self.model)

    def export_excel(self):
        filename, _format = QFileDialog.getSaveFileName(
            self, "Exporter une feuille Excel", None, 'XLSX(*.xlsx)')
        if filename:
            if filename[-4:] != '.xlsx':
                filename += '.xlsx'
            import export_xlsx
            export_xlsx.create_xlsx(filename, model=self.model)
    
    def edit_piece(self):
        code, ok = QInputDialog.getInt(self, 'Identifiant de la pièce',
            'Entrez l\'identifiant de la pièce à éditer')
        if ok:
            ids_list = self.model.get_(['id'], 'pieces_comptables')
            ids = [item for l in ids_list for item in l]
            if code in ids:
                self.piece_comptable = PieceComptable(self, code)
                self.piece_comptable.show()
            else:
                QMessageBox.warning(self, "Erreur", "Cette pièce n'existe pas.")

    def add_piece_comptable(self):
        self.piece_comptable = PieceComptable(self)
        self.piece_comptable.show()

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

    def add_input(self):
        res = AddInputDialog(self)

    def about_d(self):
        QMessageBox.information(self, "Diabolik Compta","version 0.0.2")

class Thread(QThread):
    def __init__(self, function, *args):
        super(Thread, self).__init__()
        self.function = function
        self.args = args
    def run(self):
        self.function(*self.args)
        self.finished.emit()

app = QApplication(sys.argv)
translator = QTranslator()
translator.load('qt_' + QLocale.system().name(), 
    QLibraryInfo.location(QLibraryInfo.TranslationsPath))
app.installTranslator(translator)
main_window = MainWindow()
sys.exit(app.exec_())
