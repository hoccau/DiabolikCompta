#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Diabolik Compta
Logiciel de comptabilité léger pour centre de vacances
"""

from PyQt5.QtWidgets import *
from model import Model
from views import *
from PyQt5.QtSql import QSqlRelationalDelegate
from PyQt5.QtCore import Qt, QTranslator, QLocale, QLibraryInfo, QSettings, QMimeDatabase
import sys, os

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.config = QSettings("Kidivid", "DiabolikCompta")
        self.initUI()

    def initUI(self):

        self.setWindowTitle("Diabolik Compta")
        menubar = self.menuBar()

        exitAction = self._add_action('&Quitter', qApp.quit, 'Ctrl+Q')
        newAction = self._add_action('Nouveau', self.create_new_db, 'Ctrl+N')
        openAction = self._add_action('&Ouvrir', self.open_db, 'Ctrl+O')
        aboutAction = self._add_action('à propos', self.about_d)

        self.db_actions = {} #actions for which database connexion is needed
        self.db_actions['delRow'] = self._add_action(
            '&Supprimer la ligne', self.remove_current_row)
        self.db_actions['addForm'] = self._add_action(
            '&Pièce comptable', self.add_piece_comptable)
        self.db_actions['add_fournisseur'] = self._add_action(
            '&Fournisseur', self.add_fournisseur)
        self.db_actions['add_code_compta'] = self._add_action(
            '&Code compta', self.add_code_compta)
        self.db_actions['addInput'] = self._add_action(
            "Entrée d'argent", self.add_input)
        self.db_actions['add_retrait'] = self._add_action(
            "Retrait de liquide", self.add_retrait)
        self.db_actions['setInfos'] = self._add_action(
            'Editer les infos du centre', self.set_infos)
        self.db_actions['editPiece'] = self._add_action(
            'Editer la piece', self.edit_piece, 'Ctrl+E')
        self.db_actions['ViewRapport'] = self._add_action(
            'Rapport', self.view_rapport)
        self.db_actions['exportPdf'] = self._add_action(
            'Exporter un rapport PDF', self.export_pdf)
        self.db_actions['exportXlsx'] = self._add_action(
            'Exporter un fichier Excel', self.export_excel)
        self.db_actions['close'] = self._add_action(
            '&Fermer', self.close_db, 'Ctrl+W')
        
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
        addMenu.addAction(self.db_actions['add_fournisseur'])
        addMenu.addAction(self.db_actions['add_code_compta'])
        addMenu.addAction(self.db_actions['addInput'])
        addMenu.addAction(self.db_actions['add_retrait'])
        aideMenu = menubar.addMenu('&Aide')
        aideMenu.addAction(aboutAction)

        self.enable_db_actions(False)

        self.statusBar().showMessage('Ready')
        self.model = Model(self)

        self.setMinimumSize(1024, 600)
        self.show()

        self.retrieve_db()

    def enable_db_actions(self, b=True):
        for name, action in self.db_actions.items():
            action.setEnabled(b)

    def _create_tables_views(self):
        """ Create main Arrays views inside a QTabWidget """
        self.tabs = QTabWidget()

        self.pieces_comptables_view = self._create_table_view(
            self.model.tables['pieces_comptables'])
        self.subdivisions_view = self._create_table_view(self.model.tables['subdivisions'])
        self.inputs_view = self._create_table_view(self.model.tables['inputs'])
        self.retraits_view = self._create_table_view(self.model.tables['retraits'])

        self.tabs.addTab(self.pieces_comptables_view, "Pièces comptables")
        self.tabs.addTab(self.subdivisions_view, "Subdivisions")
        self.tabs.addTab(self.inputs_view, "Entrées d'argent")
        self.tabs.addTab(self.retraits_view, "Retrait de liquide")

        self.tabs.currentChanged.connect(self.tab_selected)
        
        self.setCentralWidget(self.tabs)

    def _create_table_view(self, model):
        view = QTableView()
        view.setModel(model)
        view.setItemDelegate(QSqlRelationalDelegate())
        view.resizeColumnsToContents()
        view.setSortingEnabled(True)
        view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        view.setSelectionBehavior(QAbstractItemView.SelectRows)
        return view

    def _create_results_views(self):
        self.right_dock = QDockWidget('Informations Générales', self)
        self.right_dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(Qt.RightDockWidgetArea, self.right_dock)
        layout = QVBoxLayout()
        for k, g_model in sorted(self.model.general_results.items()):
            table = QTableView()
            table.setModel(g_model.model)
            table.resizeColumnsToContents()
            table.verticalHeader().hide()
            table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            layout.addWidget(table)
        self.right_col = QWidget()
        self.right_col.setLayout(layout)
        self.right_dock.setWidget(self.right_col)

    def _add_action(self, name, function_name, shortcut=None):
        action = QAction(name, self)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(function_name)
        return action
    
    def _get_selected_piece(self):
        """ Return the selected piece_comptable id if it is currently selected """
        current_table = self.tabs.currentWidget().model().tableName()
        id_ = None
        if current_table == 'pieces_comptables':
            select = self.tabs.currentWidget().selectionModel()
            row = select.currentIndex().row()
            id_ = self.tabs.currentWidget().model().record(row).value(0)
        return id_

    def tab_selected(self, index):
        """ enable or disable actions when a tab is selected """
        current_table = self.tabs.currentWidget().model().tableName()
        can_be_removed = ['pieces_comptables', 'retraits_liquide', 'inputs']
        print(current_table)
        if current_table in  can_be_removed:
            self.db_actions['delRow'].setEnabled(True)
        else:
            self.db_actions['delRow'].setEnabled(False)
        if current_table == 'pieces_comptables':
            self.db_actions['editPiece'].setEnabled(True)
        else:
            self.db_actions['editPiece'].setEnabled(False)

    def view_rapport(self):
        RapportDialog(self)

    def remove_current_row(self):
        current_table = self.tabs.currentWidget().model().tableName()
        select = self.tabs.currentWidget().selectionModel()
        row = select.currentIndex().row()
        if row != -1:
            if current_table == 'pieces_comptables':
                self.remove_piece(row)
            elif current_table == 'retraits_liquide':
                self.remove_retrait(row)
            elif current_table == 'inputs':
                self.remove_input(row)
        else:
            QMessageBox.warning(
                self, "Erreur", "Veuillez d'abord sélectionner une pièce comptable,\
                un retrait de liquide, ou une entrée d'argent dans le tableau \
                correspondant.")
    
    def remove_piece(self, row):
        id_ = self._get_selected_piece()
        if id_:
            reponse = QMessageBox.question(
                None,
                'Sûr(e)?',
                'Vous êtes sur le point de supprimer définitivement la\
                pièce comptable numero '+str(id_)+' (ligne '+str(row+1)+') ainsi\
                que toutes les subdivisions associées. Êtes-vous sûr(e) ?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
                )
            if reponse == QMessageBox.Yes:
                self.model.tables['pieces_comptables'].removeRow(row)
                self.model.tables['pieces_comptables'].select()
                self.model.tables['subdivisions'].select()
                [table.select() for table in self.model.general_results.values()]

    def remove_input(self, row):
        reponse = QMessageBox.question(
            None,
            'Sûr(e)?',
            "Vous êtes sur le point de supprimer définitivement une\
            entrée d'argent. Êtes-vous sûr(e) ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
            )
        if reponse == QMessageBox.Yes:
            self.model.tables['inputs'].removeRow(row)
            self.model.tables['inputs'].select()
            [table.select() for table in self.model.general_results.values()]

    def remove_retrait(self, row):
        reponse = QMessageBox.question(
            None,
            'Sûr(e)?',
            "Vous êtes sur le point de supprimer définitivement un\
            retrait de liquide. Êtes-vous sûr(e) ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
            )
        if reponse == QMessageBox.Yes:
            self.model.tables['retraits'].removeRow(row)
            self.model.tables['retraits'].select()
            [table.select() for table in self.model.general_results.values()]

    def open_db(self):
        file_name = QFileDialog.getOpenFileName(
            self,
            'Ouvrir un fichier',
            "",
            "Bases de données (*.db)")
        if file_name[0]:
            self.connect_db(file_name[0])

    def close_db(self):
        self.enable_db_actions(False)
        self.model.db.close()
        self.tabs.close()
        self.right_dock.close()

    def retrieve_db(self):
        path = self.config.value("lastdbpath")
        if path:
            if os.path.exists(path):
                self.connect_db(path)

    def create_new_db(self):
        code, ok = QInputDialog.getInt(
            self, 'Code centre', 'Entrez le code de votre centre:')
        if ok and code != '':
            #db_name, format_ = QFileDialog.getSaveFileName(
            #    self,
            #    "Enregistrer une nouvelle base",
            #    None,
            #    'DB(*.db)')
            user_path = os.path.expanduser('~')
            user_folder_name = "DiabolikCompta"
            if not os.path.isdir(os.path.join(user_path, user_folder_name)):
                os.mkdir(os.path.join(user_path, user_folder_name))
            path = os.path.join(
                user_path,
                'DiabolikCompta',
                'centre'+str(code)+'.db')
            if path:
                if path.split('.')[-1] != 'db':
                    path += '.db'
                progress_dialog = WaitingDialog(
                    self,
                    self.model,
                    path,
                    code)
                progress_dialog.resize(200, 90)
                if progress_dialog.exec_():
                    self.connect_db(path)
                    self.set_infos()

    def connect_db(self, db_path):
        mime_db = QMimeDatabase()
        mime = mime_db.mimeTypeForFile(db_path)
        if mime.name() != 'application/x-sqlite3':
            QMessageBox.warning(self, "Erreur", "Mauvais format de fichier")
            return False
        else:
            self.model.connect_db(db_path)
            self.statusBar().showMessage('Connecté sur : '+db_path)
            self.config.setValue("lastdbpath", db_path)
            self._create_tables_views()
            self._create_results_views()
            self.enable_db_actions(True)
            return True

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
            if filename[-5:] != '.xlsx':
                filename += '.xlsx'
            import export_xlsx
            export_xlsx.create_xlsx(filename, model=self.model)

    def edit_piece(self):
            id_ = self._get_selected_piece()
            if id_:
                self.piece_comptable = PieceComptable(self, id_)
                self.piece_comptable.show()
            else:
                QMessageBox.warning(
                    self, "Erreur", "Veuillez sélectionner une pièce comptable\
                    dans le tableau 'Pièces comptables'.")

    def add_piece_comptable(self):
        self.piece_comptable = PieceComptable(self)
        self.piece_comptable.show()

    def add_fournisseur(self):
        name, ok = QInputDialog.getText(
            self, 'Fournisseur', 'Nom du fournisseur:')
        if ok and name != "":
            res = self.model.add({'nom': name}, 'fournisseurs')
            if res:
                return True
            elif res == "UNIQUE constraint failed: fournisseurs.NOM":
                QMessageBox.warning(self, "Erreur", "Ce nom existe déjà.")
            else:
                QMessageBox.warning(self, "Erreur", "Erreur de requette inconnue!")

    def add_code_compta(self):
        name, code, ok = CodeComptaDialog.getCode()
        if ok and name != "":
            datas = {'code': code, 'nom': name}
            response = self.model.add(datas, 'codecompta')
            if response == "UNIQUE constraint failed: codecompta.CODE":
                QMessageBox.warning(self, "Erreur", "Ce code existe déjà")

    def add_input(self):
        AddInputDialog(self)

    def add_retrait(self):
        AddRetraitDialog(self)

    def about_d(self):
        QMessageBox.information(self, "Diabolik Compta", "version 0.0.6")

app = QApplication(sys.argv)
translator = QTranslator()
translator.load('qt_' + QLocale.system().name(),
    QLibraryInfo.location(QLibraryInfo.TranslationsPath))
app.installTranslator(translator)
main_window = MainWindow()
sys.exit(app.exec_())
