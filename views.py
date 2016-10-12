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

        namePrice = QLabel("Prix (€)")
        self.price = QLineEdit()
        #self.price.decimals = 2
        #self.price.setInputMask('00.00€')
        regexp = QRegExp('\d[\d\,\.]+')
        self.price.setValidator(QRegExpValidator(regexp))

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
        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.price)
        self.hbox.addWidget(self.typePayement)
        self.add_layout("Prix Total:",self.hbox)
        self.subdivisions = []
        self.add_subdivision()
        self.grid.addWidget(QLabel("Subdivisions"), self.field_index -1, 0)
        self.grid.addWidget(self.submitButton, 100, 0)
        self.grid.addWidget(quitButton, 100, 1)

        self.setLayout(self.grid)

        self.submitButton.clicked.connect(self.verif_datas)
        quitButton.clicked.connect(self.reject)
    
    def add_field(self, label_name, widget):
        self.grid.addWidget(QLabel(label_name), self.field_index, 0)
        self.grid.addWidget(widget, self.field_index, 1)
        self.field_index += 1

    def add_layout(self, label_name, layout):
        self.grid.addWidget(QLabel(label_name), self.field_index, 0)
        self.grid.addLayout(layout, self.field_index, 1)
        self.field_index += 1

    def add_subdivision(self):
        subdivision = SubdivisionView(self, self.field_index)
        self.subdivisions.append(subdivision)
        self.grid.addLayout(self.subdivisions[-1].layout, self.field_index, 1)
        self.field_index += 1

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
            self.model.add_piece_comptable(record)
            self.model.update_table_model()
            self.clear_all()

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
        #self.grid = QGridLayout()
        self.layout = QHBoxLayout()
        self.product = QLineEdit()
        self.product.setPlaceholderText("Désignation")
        self.code_compta = QComboBox()
        self.code_analytique = QComboBox()
        self.refresh_code_compta()
        self.refresh_code_analytique()
        self.prix = QLineEdit()
        regexp = QRegExp('\d[\d\,\.]+')
        self.prix.setValidator(QRegExpValidator(regexp))
        self.prix.setPlaceholderText("Prix")
        self.submit_button = QPushButton("+")
        self.submit_button.setMaximumWidth(20)
        #self.submit_button.resize(20, 10)
        #print(self.submit_button.width())
        self.remove_button = QPushButton("-")
        self.remove_button.setMaximumWidth(20)
        self.submit_button.clicked.connect(self.submit_datas)
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
        for code_analytique, code in list(self.model.get_codes_analytiques().items()):
            self.code_analytique.addItem(code_analytique)

    def submit_datas(self):
        #self.layout.removeWidget(self.submit_button)
        self.submit_button.deleteLater()
        #del(self.submit_button)
        self.layout.insertWidget(4, self.remove_button)
        self.parent.add_subdivision()

    def delete_line(self):
        print(self.parent.subdivisions)
        self.layout.removeWidget(self.code_compta)
        del(self.code_compta)
        self.layout.removeWidget(self.product)
        del(self.product)
        self.layout.removeWidget(self.prix)
        del(self.prix)
        self.layout.removeWidget(self.submit_button)
        del(self.submit_button)
        self.layout.removeWidget(self.remove_button)
        del(self.remove_button)
        #label = self.parent.grid.itemAtPosition(self.index, 0)
        #self.parent.grid.removeItem(label)
        #self.parent.grid.removeItem(self.layout)
        del(self.layout)
        self.parent.subdivisions.remove(self)
        print(self.parent.subdivisions)

    def clear_layout(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                self.clearLayout(item.layout())
        self.parent.subdivisions.remove(self)

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

