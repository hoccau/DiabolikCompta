#!/usr/bin/python3
# -*- coding: utf-8 -*- 

from PyQt5.QtWidgets import *
from PyQt5.QtCore import QRegExp, QDate, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QRegExpValidator, QIntValidator 
from PyQt5.QtChart import *

class PieceComptable(QDialog):
    def __init__(self, parent=None, id_ = None):
        super(PieceComptable, self).__init__(parent)

        self.parent = parent
        self.model = parent.model

        self.fournisseur = QComboBox()
        add_fournisseur = QPushButton('Ajouter')
        self.date = QCalendarWidget()
        self.price = QLineEdit()
        self.type_payement = QComboBox()
        self.cheque_number = QLineEdit()
        self.submitButton = QPushButton("Enregistrer")
        quitButton = QPushButton("Annuler")

        self.refresh_fournisseurs()
        self.refresh_typePayement()
        regexp = QRegExp('\d[\d\.]+')
        self.price.setValidator(QRegExpValidator(regexp))
        regexp = QRegExp('^([0-9]{6})\d$') # 7 digits
        self.cheque_number.setValidator(QRegExpValidator(regexp))
        self.cheque_number.setPlaceholderText('Numéro')
        self.cheque_number.setFixedWidth(80)

        self.grid = QGridLayout()
        self.piece_layout = QFormLayout(self)

        self.price_box = QHBoxLayout()
        self.price_box.addWidget(self.price)
        self.price_box.addWidget(self.type_payement)
        self.price_box.addWidget(self.cheque_number)

        fournisseurs_box = QHBoxLayout()
        fournisseurs_box.addWidget(self.fournisseur, stretch=10)
        fournisseurs_box.addWidget(add_fournisseur)
        self.piece_layout.addRow(QLabel("Fournisseur:"), fournisseurs_box)
        self.piece_layout.addRow(QLabel("Date:"), self.date)
        
        # Subdivisions BOX
        self.subdivision_index = 1
        self.subdivisions = []
        self.codes_analytiques = self.model.get_dict(['nom','code'], 'code_analytique')

        box_subdivisions = QGroupBox('', self)
        add_button = QPushButton('Ajouter une subdivision')
        self.subdivisions_grid = QGridLayout()
        self.subdivisions_grid.addWidget(add_button, 100, 0, 100, 7)
        box_subdivisions.setLayout(self.subdivisions_grid)

        self.piece_layout.addRow(QLabel("Subdivisions:"), box_subdivisions)
        self.piece_layout.addRow(QLabel("Prix total:"), self.price_box)
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
        self.type_payement.currentTextChanged.connect(self.refresh_cheque_number)
        
        if not id_:
            self.add_subdivision()
            if self.model.get_last_id('pieces_comptables') == None:
                self.id = 1
            else:
                self.id = int(self.model.get_last_id('pieces_comptables')) + 1
            self.new_record = True
        else:
            self.new_record = False
            self.id = id_
            self.populate(id_)
        self.setWindowTitle("Pièce comptable #"+str(self.id))

    def populate(self, id_):
        piece = self.model.get_piece_by_id(id_)
        self.fournisseur.setCurrentText(piece['fournisseur'])
        self.date.setSelectedDate(QDate.fromString(piece['date'],'yyyy-MM-dd'))
        self.price.insert(str(piece['total']))
        self.type_payement.setCurrentText(piece['type_payement'])
        self.cheque_number.setText(str(piece['cheque_number']))
        for subdivision_datas in piece['subdivisions']:
            self.add_subdivision(subdivision_datas)

    def add_subdivision(self, datas=None):
        subdivision = SubdivisionView(
            parent = self,
            index = self.subdivision_index,
            codes_analytiques = self.codes_analytiques,
            datas = datas
            )
        self.subdivisions.append(subdivision)
        self.subdivisions_grid.addLayout(
            self.subdivisions[-1].layout,
            self.subdivision_index, 1)
        self.subdivision_index += 1

    def add_fournisseur(self):
        f = self.parent.add_fournisseur()
        if f:
            self.refresh_fournisseurs()

    def get_total_subdivisions_price(self):
        total = 0
        for subdivision in self.subdivisions:
            total += float(subdivision.prix.text())
        return round(total, 2)
            
    def all_subdivisions_valid(self):
        for subdivision in self.subdivisions:
            if not subdivision.verif_datas():
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
        elif self.type_payement.currentText() == 'Chèque'\
            and len(self.cheque_number.text()) < 7:
                QMessageBox.warning(
                    self,
                    "Erreur", "Il faut entrer un numéro de chèque valide"
                    )
        elif len(self.subdivisions) < 1:
            QMessageBox.warning(self, "Erreur", "Il faut entrer au minimum une subdivision")
        elif not self.all_subdivisions_valid():
            QMessageBox.warning(self,
                "Erreur",
                "Toutes les subdivisions ne sont pas correctement remplies")
        elif self.get_total_subdivisions_price() != float(self.price.text()):
            QMessageBox.warning(self,
                "Erreur",
                "La somme des subdivisions est différente du prix total indiqué")
        else:
            self.submit_datas()
    
    def submit_datas(self):    
        record = {}
        fournisseur_name = self.fournisseur.currentText()
        f_id = self.model.get_one('id','fournisseurs','nom', fournisseur_name)
        type_payement_name = self.type_payement.currentText()
        p_id = self.model.get_one('id','type_payement','nom', type_payement_name)
        
        record["id"] = str(self.id)
        record["fournisseur_id"] = f_id
        record["date"] = self.date.selectedDate().toString('yyyy-MM-dd')
        record["total"] = self.price.text()
        record["typePayement_id"] = p_id
        record["cheque_number"] = self.cheque_number.text()
        if self.new_record:
            self.model.add(record, 'pieces_comptables')
        else:
            self.model.update(record, 'pieces_comptables', 'id', str(self.id))
            self.model.delete('subdivisions', 'piece_comptable_id', str(self.id))
        for subdivision in self.subdivisions:
            subdivision.submit_datas()
        self.model.tables['pieces_comptables'].select()
        self.close()

    def refresh_fournisseurs(self):
        self.fournisseur.clear()
        for fournisseur in self.model.get_(['nom'],'fournisseurs'):
            self.fournisseur.addItem(fournisseur[0])
    
    def refresh_typePayement(self):
        self.type_payement.clear()
        for type_payement in self.model.get_(['nom'],'type_payement'):
            self.type_payement.addItem(type_payement[0])

    def refresh_cheque_number(self, text_value):
        if text_value == 'Chèque':
            self.cheque_number.show()
        else:
            self.cheque_number.clear()
            self.cheque_number.hide()

class SubdivisionView():
    def __init__(self, parent=None, index=None, codes_analytiques=None, datas=None):
        self.parent = parent
        self.index = index
        self.model = parent.model
        self.codes_analytiques = codes_analytiques
        
        self.product = QLineEdit()
        self.prix = QLineEdit()
        self.code_analytique_box = QComboBox()
        self.code_compta_box = QComboBox()
        self.remove_button = QPushButton("-")

        self.layout = QHBoxLayout()
        self.product.setPlaceholderText("Désignation")
        self.refresh_code_analytique()
        self.refresh_code_compta()
        for widget in (self.prix, self.product, self.code_compta_box, self.code_analytique_box):
            widget.setStyleSheet(':disabled {color:#333}')
        regexp = QRegExp('\d[\d\.]+')
        self.prix.setValidator(QRegExpValidator(regexp))
        self.prix.setPlaceholderText("Prix")
        self.remove_button.setMaximumWidth(20)

        self.remove_button.clicked.connect(self.clear_layout)
        self.code_analytique_box.currentIndexChanged.connect(self.refresh_code_compta)

        self.layout.addWidget(self.product, stretch=8)
        self.layout.addWidget(self.prix, stretch=3)
        self.layout.addWidget(self.code_analytique_box, stretch=5)
        self.layout.addWidget(self.code_compta_box, stretch=10)
        self.layout.addWidget(self.remove_button, stretch=1)

        if datas:
            self.populate(datas)

    def populate(self, datas):
        self.product.insert(datas['designation'])
        self.prix.insert(str(datas['prix']))
        self.code_analytique_box.setCurrentText(datas['code_analytique'])
        self.code_compta_box.setCurrentText(datas['code_compta'])

    def refresh_code_compta(self):
        self.code_compta_box.clear()
        code_analytique_id = self.codes_analytiques[self.code_analytique_box.currentText()]
        filtre = 'code_analytique_id = '+str(code_analytique_id)
        for line in self.model.get_(['nom'], 'codecompta', filtre):
            self.code_compta_box.addItem(line[0])
    
    def refresh_code_analytique(self):
        self.code_analytique_box.clear()
        for code_analytique in sorted(self.codes_analytiques.keys()):
            self.code_analytique_box.addItem(code_analytique)

    def verif_datas(self):
        if self.product.text() == "":
            QMessageBox.warning(self.parent, "Erreur", "Il faut entrer un nom de produit")
        elif self.prix.text() == "":
            QMessageBox.warning(self.parent, "Erreur", "Il faut entrer un prix")
        else:
            return True

    def submit_datas(self):
            name_cc = self.code_compta_box.currentText()
            cc_id = self.model.get_one('code', 'codecompta', 'nom', name_cc)
            ca_id = self.codes_analytiques[self.code_analytique_box.currentText()]
            datas = {}
            datas["piece_comptable_id"] = self.parent.id
            datas["designation"] = self.product.text()
            datas["code_compta_id"] = cc_id
            datas["code_analytique_id"] = ca_id
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
        self.parent.adjustSize()

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
        label_name = QLabel("Libellé comptable:")
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
        validator = QIntValidator()
        validator.setBottom(0)
        self.nbr_children.setValidator(validator)
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
            v = round(v, 2)
            layout.addRow(k+":", QLabel(str(v)+"€"))
        total = round(self.parent.model.get_total(), 2)
        layout.addRow("Total:", QLabel(str(total)+"€"))
        box1.setLayout(layout)
        return box1

class DateDelegate(QItemDelegate):
    def __init__(self, parent):
        super(DateDelegate).__init__(parent)

    def displayText(self, value):
        date = QDate.fromString(value, "yyyy-MM-dd")
        return date.toString("dd/MM/yyyy")

class WaitingDialog(QDialog):
    def __init__(self, parent=None, model=None, db_name="", code_centre=0):
        super(WaitingDialog, self).__init__(parent)
        self.db_filename = db_name
        self.layout = QVBoxLayout(self)
        self.label = QLabel("Création de la base de données...")
        self.progressBar = QProgressBar(self)
        self.progressBar.setRange(0,1)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.progressBar)

        self.myLongTask = CreateDB(model, db_name, code_centre)
        self.myLongTask.taskFinished.connect(self.onFinished)

        self.progressBar.setRange(0,0)
        self.myLongTask.start()

    def onFinished(self):
        self.progressBar.setRange(0,1)
        self.progressBar.setValue(1)
        self.label.setText(
            "Base de donnée "+self.db_filename + " créée.")
        button = QPushButton("OK")
        button.clicked.connect(self.accept)
        self.layout.addWidget(button)

class CreateDB(QThread):
    taskFinished = pyqtSignal()
    def __init__(self, model, db_name, code_centre, parent=None):
        QThread.__init__(self)
        self.model = model
        self.db_name = db_name
        self.code_centre = code_centre
    def run(self):
        self.model.create_db(self.db_name, self.code_centre)
        self.taskFinished.emit()

