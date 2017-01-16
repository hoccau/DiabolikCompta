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
from PyQt5.QtCore import Qt, QTranslator, QLocale, QLibraryInfo, QThread

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
        addFormAction = self.add_action('&Pièce comptable', self.add_piece_comptable)
        addFournisseurAction = self.add_action('&Fournisseur', self.addFournisseur)
        addCodeComptaAction = self.add_action('&Code compta', self.addCodeCompta)
        addInputAction = self.add_action("Entrée d'argent", self.add_input)
        setInfosAction = self.add_action('Editer les infos du centre', self.set_infos)
        editPieceAction = self.add_action('Editer la piece', self.edit_piece)
        ViewRapportAction = self.add_action('Rapport', self.viewRapport)
        exportPdfAction = self.add_action('Exporter un rapport', self.export_pdf)

        fileMenu = menubar.addMenu('&Fichier')
        fileMenu.addAction(openAction)
        fileMenu.addAction(exportPdfAction)
        fileMenu.addAction(exitAction)
        edit_menu = menubar.addMenu('&Édition')
        edit_menu.addAction(delRowAction)
        edit_menu.addAction(editPieceAction)
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

    def edit_piece(self):
        code, ok = QInputDialog.getInt(self, 'Identifiant de la pièce',
            'Entrez l\'identifiant de la pièce à étiter')
        if ok:
            self.piece_comptable = PieceComptable(self, code)
            self.piece_comptable.show()
        
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

        layout = QVBoxLayout()
        for k, g_model in self.model.general_results.items():
            table = QTableView()
            table.setModel(g_model.model)
            table.resizeColumnsToContents()
            table.verticalHeader().hide()
            table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            layout.addWidget(table)
        widget = QWidget()
        widget.setLayout(layout)
        self.right_dock.setWidget(widget)

    def create_table_view(self, model):
        view = QTableView()
        view.setModel(model)
        view.setItemDelegate(QSqlRelationalDelegate())
        view.resizeColumnsToContents()
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
            self.model.connect_db(file_name[0])

    def retrieve_db(self):
        files = os.listdir('./')
        files = [x for x in files if x.split('.')[-1] == 'db']

        if len(files) == 1:
            QMessageBox.information(self, "Base trouvée","Base de donnée : "+files[0])
            self.model.connect_db(files[0])
            return True

        elif len(files) > 1:
            #QMessageBox.critical(None, "Plusieurs bases trouvées", "Plusieurs bases de données trouvées. Je ne sais que faire...")
            combo = QComboBox(self)
            for db_name in files:
                combo.addItem(db_name)
        
        elif len(files) == 0:
            reponse = QMessageBox.question(
                None,
                'message',
                'Pas de base de données trouvée. Faut-il en créer une nouvelle ?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
                )
            if reponse == QMessageBox.No:
                return False
            if reponse == QMessageBox.Yes:
                new_db = self.create_new_db()
                if new_db:
                    self.model.connect_db(new_db)
                    self.set_infos()
                    return True

    def create_new_db(self):
        db_name, code = self.input_db_name()
        if db_name == None or code == None:
            return False
        else:
            progress_dialog = WaitingDialog(
                self,
                self.model,
                db_name,
                code)
            progress_dialog.resize(200,100)
            progress_dialog.exec_()
            return db_name

    def input_db_name(self):
        code, ok = QInputDialog.getInt(self, 'Code centre',
            'Entrez le code de votre centre:')
        if ok and code != '':
            name = 'centre' + str(code) + '.db'
            return name, code
        else:
            return None, None

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

class Thread(QThread):
    def __init__(self, function, *args):
        super(Thread, self).__init__()
        self.function = function
        self.args = args
    def run(self):
        self.function(*self.args)
        self.finished.emit()

if __name__ == '__main__':
    import sys, os
    
    app = QApplication(sys.argv)
    translator = QTranslator()
    translator.load('qt_' + QLocale.system().name(), 
        QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    app.installTranslator(translator)
    main_window = MainWindow()
    sys.exit(app.exec_())
