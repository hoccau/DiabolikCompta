#!/usr/bin/python3
# -*- coding: utf-8 -*- 

from PyQt5.QtWidgets import *
from PyQt5.QtCore import QRegExp, QDate
from PyQt5.QtGui import QRegExpValidator, QIntValidator 
from PyQt5.QtChart import *

class PieceComptable(QDialog):
    def __init__(self, parent=None):
        super(PieceComptable, self).__init__(parent)

        self.parent = parent
        self.model = parent.model

        if self.model.get_last_id('pieces_comptables') == None:
            self.id = 1
        else:
            self.id = int(self.model.get_last_id('pieces_comptables')) + 1
        self.setWindowTitle("Pièce comptable #"+str(self.id))
        
        nameFournisseur = QLabel("Fournisseur:")
        add_fournisseur = QPushButton('Ajouter')
        self.fournisseur = QComboBox()
        self.refresh_fournisseurs()

        namePrice = QLabel("Prix (€)")
        self.price = QLineEdit()
        regexp = QRegExp('\d[\d\.]+')
        self.price.setValidator(QRegExpValidator(regexp))

        nameTypePayement = QLabel("Type de payement")
        self.typePayement = QComboBox()
        self.typePayement.addItems(list(self.model.get_typesPayement().keys()))
        self.date = QCalendarWidget()

        self.submitButton = QPushButton("Enregistrer")
        quitButton = QPushButton("Annuler la pièce")

        self.grid = QGridLayout()
        self.piece_layout = QFormLayout(self)

        price_box = QHBoxLayout()
        price_box.addWidget(self.price)
        price_box.addWidget(self.typePayement)

        fournisseurs_box = QHBoxLayout()
        fournisseurs_box.addWidget(self.fournisseur, stretch=10)
        fournisseurs_box.addWidget(add_fournisseur)
        self.piece_layout.addRow(QLabel("Fournisseur:"), fournisseurs_box)
        self.piece_layout.addRow(QLabel("Date:"), self.date)
        # Subdivisions BOX
        self.subdivisions_grid = QGridLayout()
        box_subdivisions = QGroupBox('', self)
        box_subdivisions.setLayout(self.subdivisions_grid)
        self.subdivision_index = 1
        add_button = QPushButton('Ajouter une subdivision')
        self.subdivisions_grid.addWidget(add_button, 100, 0, 100, 7)
        self.subdivisions = []
        self.add_subdivision()
        #self.grid.addWidget(box_subdivisions, 0, 1)
        self.piece_layout.addRow(QLabel("Subdivisions:"), box_subdivisions)
        self.piece_layout.addRow(QLabel("Prix total:"), price_box)
        buttons_box = QHBoxLayout()
        buttons_box.addWidget(self.submitButton)
        buttons_box.addWidget(quitButton)
        self.piece_layout.addRow(buttons_box)
        box_piece = QGroupBox('Piece comptable', self)
        box_piece.setLayout(self.piece_layout)
        self.grid.addWidget(box_piece, 0,0)
        
        self.setLayout(self.grid)

        self.submitButton.clicked.connect(self.verif_datas)
        add_button.clicked.connect(self.add_subdivision)
        quitButton.clicked.connect(self.reject)
        add_fournisseur.clicked.connect(self.add_fournisseur)
    
    def add_field(self, label_name, widget):
        self.grid.addWidget(QLabel(label_name), self.field_index, 0)
        self.grid.addWidget(widget, self.field_index, 1)
        self.field_index += 1

    def add_layout(self, label_name, layout):
        self.grid.addWidget(QLabel(label_name), self.field_index, 0)
        self.grid.addLayout(layout, self.field_index, 1)
        self.field_index += 1

    def add_subdivision(self):
        subdivision = SubdivisionView(self, self.subdivision_index)
        self.subdivisions.append(subdivision)
        self.subdivisions_grid.addLayout(
            self.subdivisions[-1].layout,
            self.subdivision_index, 1)
        self.subdivision_index += 1

    def add_fournisseur(self):
        f = self.parent.addFournisseur()
        if f:
            self.refresh_fournisseurs()

    def get_total_subdivisions_price(self):
        total = 0
        for subdivision in self.subdivisions:
            print('sub price:', subdivision.prix.text())
            total += float(subdivision.prix.text())
        return total
            
    def all_subdivisions_valid(self):
        for subdivision in self.subdivisions:
            if subdivision.is_locked:
                return False
        return True

    def clear_all(self):
        self.price.clear()
        for subdivision in self.subdivisions:
            subdivision.clear_layout()

    def verif_datas(self):
        if self.fournisseur.currentText() == "":
            QMessageBox.warning(self, "Erreur", "Il faut entrer un nom de fournisseur")
        elif self.price.text() == "":
            QMessageBox.warning(self, "Erreur", "Il faut entrer un prix total")
        elif len(self.subdivisions) < 1:
            QMessageBox.warning(self, "Erreur", "Il faut entrer au minimum une subdivision")
        elif self.all_subdivisions_valid():
            QMessageBox.warning(self,
                "Erreur",
                "Toutes les subdivisions ne sont pas validées")
        elif self.get_total_subdivisions_price() != float(self.price.text()):
            QMessageBox.warning(self,
                "Erreur",
                "La somme des subdivisions est différente du prix total indiqué")
        else:
            self.submit_datas()
    
    def submit_datas(self):    
        record = {}
        #below : can be improved for faster ?
        f_id = self.model.get_fournisseurs()[self.fournisseur.currentText()]
        p_id = self.model.get_typesPayement()[self.typePayement.currentText()]
        record["id"] = str(self.id)
        record["fournisseur_id"] = f_id
        record["date"] = self.date.selectedDate().toString('yyyy-MM-dd')
        record["total"] = self.price.text()
        record["typePayement_id"] = p_id
        self.model.add(record, 'pieces_comptables')
        for subdivision in self.subdivisions:
            subdivision.submit_datas()
        self.model.tables['pieces_comptables'].select()
        self.close()

    def refresh_fournisseurs(self):
        self.fournisseur.clear()
        for fournisseur, rowid in list(self.model.get_fournisseurs().items()):
            self.fournisseur.addItem(fournisseur)
    
    def refresh_typePayement(self):
        self.typePayement.clear()
        for typePayement, rowid in list(self.model.get_typesPayement().items()):
            self.codeCompta.addItem(typePayement)

class SubdivisionView():
    def __init__(self, parent=None, index=None):
        self.parent = parent
        self.index = index
        self.model = parent.model
        self.is_locked = False
        self.layout = QHBoxLayout()
        self.product = QLineEdit()
        self.product.setPlaceholderText("Désignation")
        self.code_compta = QComboBox()
        self.code_analytique = QComboBox()
        self.refresh_code_compta()
        self.refresh_code_analytique()
        self.prix = QLineEdit()
        for widget in (self.prix, self.product, self.code_compta, self.code_analytique):
            widget.setStyleSheet(':disabled {color:#333}')
        regexp = QRegExp('\d[\d\.]+')
        self.prix.setValidator(QRegExpValidator(regexp))
        self.prix.setPlaceholderText("Prix")
        self.submit_button = QPushButton("OK")
        self.submit_button.setMaximumWidth(20)
        self.remove_button = QPushButton("-")
        self.remove_button.setMaximumWidth(20)
        self.submit_button.clicked.connect(self.verif_datas)
        self.remove_button.clicked.connect(self.clear_layout)

        self.layout.addWidget(self.product, stretch=8)
        self.layout.addWidget(self.prix, stretch=3)
        self.layout.addWidget(self.code_compta, stretch=10)
        self.layout.addWidget(self.code_analytique, stretch=5)
        self.layout.addWidget(self.submit_button, stretch=1)

    def refresh_code_compta(self):
        self.code_compta.clear()
        for code_compta, code in list(self.model.get_codesCompta().items()):
            self.code_compta.addItem(code_compta)
    
    def refresh_code_analytique(self):
        self.code_analytique.clear()
        names = list(self.model.get_codes_analytiques().keys())
        names.sort() #yes it's a bad way...
        for code_analytique in names:
            self.code_analytique.addItem(code_analytique)

    def lock(self):
        self.is_locked = True
        self.product.setEnabled(False)
        self.code_compta.setEnabled(False)
        self.code_analytique.setEnabled(False)
        self.prix.setEnabled(False)

    def verif_datas(self):
        if self.product.text() == "":
            QMessageBox.warning(self.parent, "Erreur", "Il faut entrer un nom de produit")
        elif self.prix.text() == "":
            QMessageBox.warning(self.parent, "Erreur", "Il faut entrer un prix")
        else:
            self.submit_button.deleteLater()
            self.layout.insertWidget(4, self.remove_button)
            self.lock()

    def submit_datas(self):
            CO_id = self.model.get_codesCompta()[self.code_compta.currentText()]
            CA_id = self.model.get_codes_analytiques()[self.code_analytique.currentText()]
            datas = {}
            datas["piece_comptable_id"] = self.parent.id
            datas["designation"] = self.product.text()
            datas["code_compta_id"] = CO_id
            datas["code_analytique_id"] = CA_id
            print(self.prix.text())
            datas["prix"] = self.prix.text()
            if self.parent.model.add(datas,'subdivisions'):
                print("subdivision ", self, "submited")
            else:
                QMessageBox.warning(self.parent, "Erreur", "Erreur de requête")

    def clear_layout(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                self.clearLayout(item.layout())
        self.parent.subdivisions.remove(self)

class AddInputDialog(QDialog):
    def __init__(self, parent=None):
        super(AddInputDialog, self).__init__(parent)
        self.model = parent.model
        self.setWindowTitle("Ajouter une entrée d'argent")
        
        self.montant = QLineEdit()
        regexp = QRegExp('\d[\d\.]+')
        self.montant.setValidator(QRegExpValidator(regexp))
        self.montant.setPlaceholderText("Montant")
        self.date = QDateEdit(QDate.currentDate())
        self.note = QTextEdit()
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            self)
        buttons.accepted.connect(self.submit)
        buttons.rejected.connect(self.reject)

        layout = QFormLayout(self)
        layout.addRow('Date:', self.date)
        layout.addRow('Montant:', self.montant)
        layout.addRow('Commentaire:', self.note)
        layout.addRow('', buttons)

        self.exec_()

    def submit(self):
        if self.montant.text() == '':
            QMessageBox.warning(None, "Erreur", "Il faut entrer un montant")
        else:
            date = QDate.fromString(self.date.text(),'dd/MM/yyyy')
            dic = {
                'date':date.toString('yyyy-MM-dd'),
                'montant':float(self.montant.text()),
                'comment':self.note.toPlainText()
                }
            self.model.add(dic,'inputs')
            self.accept()

class CodeComptaDialog(QDialog):
    def __init__(self, parent=None):
        super(CodeComptaDialog, self).__init__(parent)

        self.setWindowTitle("Ajouter un code de comptabilité")
        layout = QGridLayout(self)
        label_code = QLabel("Code:")
        self.code = QSpinBox()
        self.code.setMaximum(999999)
        label_name = QLabel("Nom:")
        self.name = QLineEdit()

        layout.addWidget(label_code, 0, 0)
        layout.addWidget(self.code, 0, 1)
        layout.addWidget(label_name, 1, 0)
        layout.addWidget(self.name, 1, 1)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @staticmethod
    def getCode(parent = None):
        dialog = CodeComptaDialog(parent)
        result = dialog.exec_()
        return (dialog.name.text(), dialog.code.value(), result == QDialog.Accepted)

class InfosCentreDialog(QDialog):
    def __init__(self, parent=None):
        super(InfosCentreDialog, self).__init__(parent)

        self.setWindowTitle("Informations du centre")
        model = parent.model.qt_table_infos
        mapper = QDataWidgetMapper(self)
        mapper.setModel(model)

        self.centre = QLineEdit()
        self.directeur_nom = QLineEdit()
        self.nbr_children = QLineEdit()
        self.nbr_children.setValidator(QIntValidator())
        self.place = QLineEdit()
        self.startdate = QDateEdit()
        self.startdate.setDate(QDate.currentDate())
        self.enddate = QDateEdit()
        self.enddate.setDate(QDate.currentDate())

        mapper.addMapping(self.centre, model.fieldIndex("centre"))
        mapper.addMapping(self.directeur_nom, model.fieldIndex("directeur_nom"))
        mapper.addMapping(self.nbr_children, model.fieldIndex("nombre_enfants"))
        mapper.addMapping(self.place, model.fieldIndex("place"))
        mapper.addMapping(self.startdate, model.fieldIndex("startdate"))
        mapper.addMapping(self.enddate, model.fieldIndex("enddate"))
        
        layout = QFormLayout(self)
        
        layout.addRow("Nom du centre:", self.centre)
        layout.addRow("Lieu:", self.place)
        layout.addRow("Directeur:", self.directeur_nom)
        layout.addRow("Nombre d'enfants:", self.nbr_children)
        layout.addRow("Début:", self.startdate)
        layout.addRow("Fin:", self.enddate)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            self)
        buttons.accepted.connect(mapper.submit)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        mapper.toFirst()
        self.exec_()

class RapportDialog(QDialog):
    def __init__(self, parent):
        super(RapportDialog, self).__init__(parent)

        self.setWindowTitle("Rapport")
        self.parent = parent
        self.setMinimumSize(1024, 800)
        
        grid = QGridLayout(self)
        totals = parent.model.get_totals_by_payement()
        text1 = self.create_text(totals, "Par type de payement")
        graph1 = self.create_chart(totals)
        grid.addWidget(text1, 0, 0)
        grid.addWidget(graph1, 0, 1)
        by_code = parent.model.get_totals_by_codecompta()
        text2 = self.create_text(by_code, "Par catégorie comptable")
        graph2 = self.create_chart(by_code)
        grid.addWidget(text2, 1, 0)
        grid.addWidget(graph2, 1, 1)

        self.exec_()

    def create_chart(self, dic):
        series = QPieSeries()
        for k, v in dic.items():
            series.append(k,v)
        chart = QChart()
        chart.addSeries(series)
        chartView = QChartView(chart)
        return chartView
        
    def create_text(self, dic, titre):
        layout = QFormLayout()
        box1 = QGroupBox(titre, parent=self)
        for k, v in list(dic.items()):
            layout.addRow(k+":", QLabel(str(v)+"€"))
        layout.addRow("Total:", QLabel(str(self.parent.model.get_total())+"€"))
        box1.setLayout(layout)
        return box1

class DateDelegate(QItemDelegate):
    def __init__(self, parent):
        super(DateDelegate).__init__(parent)

    def displayText(self, value):
        date = QDate.fromString(value, "yyyy-MM-dd")
        return date.toString("dd/MM/yyyy")
