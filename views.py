#!/usr/bin/python
# -*- coding: utf-8 -*- 

from PyQt5.QtWidgets import *
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator

class Form(QWidget):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        self.parent = parent
        self.model = parent.model
        self.fournisseurs = []

        print self.fournisseurs
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

        self.submitButton = QPushButton("Valider")

        grid = QGridLayout()

        grid.addWidget(nameFournisseur, 1,0 )
        grid.addWidget(self.fournisseur, 1,1)
        grid.addWidget(nameProduct, 2, 0)
        grid.addWidget(self.product, 2, 1)
        grid.addWidget(namePrice, 3, 0)
        grid.addWidget(self.price, 3, 1)
        grid.addWidget(nameCodeCompta, 4, 0)
        grid.addWidget(self.codeCompta, 4, 1)
        grid.addWidget(self.submitButton, 5, 0)

        self.setLayout(grid)

        self.submitButton.clicked.connect(self.verif_datas)

    def verif_datas(self):
        if self.fournisseur.currentText() == "":
            QMessageBox.warning(self, "Erreur", "Il faut entrer un nom de fournisseur")
        if self.product.text() == "":
            QMessageBox.warning(self, "Erreur", "Il faut entrer un nom de désignation")
        if self.price.text() == "":
            QMessageBox.warning(self, "Erreur", "Il faut entrer un Prix")
        if self.codeCompta.currentText() == "":
            QMessageBox.warning(self, "Erreur", "Il faut entrer un Code Compta")

        else:
            record = {}
            #below : can be improved for faster ?
            f_id = self.model.get_fournisseurs()[self.fournisseur.currentText()]
            print f_id
            record["fournisseur_id"] = f_id
            record["product"] = self.product.text()
            record["price"] = self.price.text()
            record["codeCompta"] = self.codeCompta.currentText()
            self.model.set_line(record)
            print record

    def refresh_fournisseurs(self):
        self.fournisseur.clear()
        for fournisseur, rowid in self.model.get_fournisseurs().items():
            self.fournisseur.addItem(fournisseur)

    def refresh_codeCompta(self):
        self.codeCompta.clear()
        for codeCompta in self.model.get_codeCompta():
            self.codeCompta.addItem(codeCompta[0])

class CodeComptaDialog(QDialog):
    def __init__(self, parent=None):
        super(CodeComptaDialog, self).__init__(parent)

        layout = QGridLayout(self)
        label_code = QLabel("Code:")
        self.code = QSpinBox()
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


