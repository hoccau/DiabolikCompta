#!/usr/bin/python3
# -*- coding: utf-8 -*- 

from PyQt5.QtWidgets import *
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtChart import *

class Form(QDialog):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        self.setWindowTitle("Pièce comptable")
        self.parent = parent
        self.model = parent.model
        self.fournisseurs = []

        comp = QCompleter(self.fournisseurs)
        
        nameFournisseur = QLabel("Fournisseur:")
        self.fournisseur = QComboBox() #Choisir plutôt dans une liste de fournisseurs
        self.refresh_fournisseurs()
        self.fournisseur.setCompleter(comp)
        nameProduct = QLabel("Désignation:")
        self.product = QLineEdit()

        namePrice = QLabel("Prix (€)")
        self.price = QLineEdit()
        #self.price.decimals = 2
        #self.price.setInputMask('00.00€')
        regexp = QRegExp('\d[\d\,\.]+')
        self.price.setValidator(QRegExpValidator(regexp))

        nameCodeCompta = QLabel("Code Compta")
        self.codeCompta = QComboBox()
        self.refresh_codeCompta()
        nameTypePayement = QLabel("Type de payement")
        self.typePayement = QComboBox()
        self.typePayement.addItems(list(self.model.get_typesPayement().keys()))
        self.date = QCalendarWidget()

        self.submitButton = QPushButton("Enregistrer")
        quitButton = QPushButton("Fermer")

        self.grid = QGridLayout()

        self.field_index = 0
        self.add_field("Fournisseur:", self.fournisseur)
        self.add_field("Date:", self.date)
        self.add_field("Désignation", self.product)
        self.add_field("Prix (€):", self.price)
        self.add_field("Code Compta", self.codeCompta)
        self.add_field("Type de payement", self.typePayement)
        self.field_index += 1
        self.grid.addWidget(self.submitButton, self.field_index, 0)
        self.grid.addWidget(quitButton, self.field_index, 1)

        self.setLayout(self.grid)

        self.submitButton.clicked.connect(self.verif_datas)
        quitButton.clicked.connect(self.reject)
    
    def add_field(self, label_name, widget):
        self.field_index += 1
        self.grid.addWidget(QLabel(label_name), self.field_index, 0)
        self.grid.addWidget(widget, self.field_index, 1)

    def clear_all(self):
        self.product.clear()
        self.price.clear()

    def verif_datas(self):
        if self.fournisseur.currentText() == "":
            QMessageBox.warning(self, "Erreur", "Il faut entrer un nom de fournisseur")
        elif self.product.text() == "":
            QMessageBox.warning(self, "Erreur", "Il faut entrer un nom de désignation")
        elif self.price.text() == "":
            QMessageBox.warning(self, "Erreur", "Il faut entrer un Prix")
        elif self.codeCompta.currentText() == "":
            QMessageBox.warning(self, "Erreur", "Il faut entrer un Code Compta")

        else:
            record = {}
            #below : can be improved for faster ?
            f_id = self.model.get_fournisseurs()[self.fournisseur.currentText()]
            p_id = self.model.get_typesPayement()[self.typePayement.currentText()]
            c_id = self.model.get_codesCompta()[self.codeCompta.currentText()]
            record["fournisseur_id"] = f_id
            record["date"] = self.date.selectedDate().toString('yyyy-MM-dd')
            record["product"] = self.product.text()
            record["price"] = self.price.text()
            record["codeCompta_id"] = c_id
            record["typePayement_id"] = p_id
            self.model.set_line(record)
            self.model.update_table_model()
            self.clear_all()

    def refresh_fournisseurs(self):
        self.fournisseur.clear()
        for fournisseur, rowid in list(self.model.get_fournisseurs().items()):
            self.fournisseur.addItem(fournisseur)

    def refresh_codeCompta(self):
        self.codeCompta.clear()
        for codeCompta, code in list(self.model.get_codesCompta().items()):
            self.codeCompta.addItem(codeCompta)
    
    def refresh_typePayement(self):
        self.typePayement.clear()
        for typePayement, rowid in list(self.model.get_typesPayement().items()):
            self.codeCompta.addItem(typePayement)

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

        #self.qt_table_compta = QSqlTableModel(self, self.db).setTable('compta')

class InfosCentreDialog(QDialog):
    def __init__(self, parent=None):
        super(InfosCentreDialog, self).__init__(parent)

        self.setWindowTitle("Centre")
        model = parent.model.qt_table_infos
        mapper = QDataWidgetMapper(self)
        mapper.setModel(model)

        self.centre = QLineEdit()
        self.directeur_nom = QLineEdit()
        self.directeur_prenom = QLineEdit()

        mapper.addMapping(self.centre, model.fieldIndex("centre"))
        mapper.addMapping(self.directeur_nom, model.fieldIndex("directeur_nom"))
        mapper.addMapping(self.directeur_prenom, model.fieldIndex("directeur_prenom"))
        
        layout = QFormLayout(self)
        
        layout.addRow("Nom du centre:", self.centre)
        layout.addRow("Nom du directeur:", self.directeur_nom)
        layout.addRow("Prénom du directeur:", self.directeur_prenom)
        
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
        self.setMinimumSize(700, 500)
        
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
        #chart.setTitle("Graphique")
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

