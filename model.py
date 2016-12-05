#!/usr/bin/python3
# -*- coding: utf-8 -*- 

from PyQt5.QtSql import QSqlQueryModel, QSqlDatabase, QSqlQuery, QSqlRelationalTableModel, QSqlRelation, QSqlTableModel
from PyQt5.QtCore import Qt, QDate, QAbstractItemModel

DEBUG_SQL = True

class Model(QSqlQueryModel):
    def __init__(self, parent=None):
        super(Model, self).__init__(parent)

        self.db = QSqlDatabase.addDatabase('QSQLITE')

    def create_db(self, db_name):
        self.connect_db(db_name)
        self.exec_("CREATE TABLE infos(\
        centre varchar(20),\
        directeur_nom varchar(20),\
        nombre_enfants int,\
        place varchar(20),\
        startdate varchar(10),\
        enddate varchar(10)\
        )")
        self.exec_("INSERT INTO infos(\
        centre, directeur_nom, nombre_enfants) VALUES (\
        NULL, NULL, NULL)")
        self.exec_("CREATE TABLE fournisseurs(\
        id integer PRIMARY KEY,\
        NOM varchar(20)\
        )")
        self.exec_("CREATE TABLE codecompta(\
        CODE int PRIMARY KEY,\
        NOM varchar(20)\
        )")
        codes_compta = [
            "60620, 'Produits entretien'",
            "60630, 'Petit équipement petit matériel'",
            "60640, 'Fournitures administratives'",
            "60650, 'Produits pharmaceutiques'",
            "6068, 'Fournitures pour activité'",
            "60681, 'Alimentation boissons'",
            "6112, 'Sorties extérieures & activités'",
            "6152, 'Entretien/réparation immobilier'",
            "6155, 'Entretien/réparation mobiler'",
            "6181, 'Documentation générale'",
            "624, 'Transport du personnel'",
            "625, 'Transport des usagers'",
            "626, 'Postes & Télécom'",
            "606510, 'Frais médicaux remboursables'"
            ]
        for code in codes_compta:
            self.exec_("INSERT INTO codecompta (code, nom) VALUES ("+code+")")
        self.exec_("CREATE TABLE type_payement (\
        id integer PRIMARY KEY,\
        NOM varchar(20)\
        )")
        self.exec_("INSERT INTO type_payement (NOM) VALUES ('Chèque')")
        self.exec_("INSERT INTO type_payement (NOM) VALUES ('Espèces')")
        self.exec_("INSERT INTO type_payement (NOM) VALUES ('Carte Banquaire')")
        self.exec_("CREATE TABLE code_analytique (\
        code INTEGER PRIMARY KEY,\
        nom VARCHAR(20))")
        self.exec_("INSERT INTO code_analytique (code, nom) VALUES\
        (200, 'Centre')")
        self.exec_("INSERT INTO code_analytique (code, nom) VALUES\
        (600, 'Véhicule')")
        self.exec_("CREATE TABLE pieces_comptables(\
        id integer PRIMARY KEY,\
        Fournisseur_id integer NOT NULL,\
        Date varchar(10),\
        total real,\
        TypePayement_id int NOT NULL,\
        FOREIGN KEY (Fournisseur_id) REFERENCES fournisseurs(id),\
        FOREIGN KEY (TypePayement_id) REFERENCES type_payement(id)\
        )")
        self.exec_("CREATE TABLE subdivisions(\
        id INTEGER PRIMARY KEY,\
        designation,\
        piece_comptable_id INTEGER,\
        code_compta_id INTEGER NOT NULL,\
        code_analytique_id INTEGER,\
        prix REAL,\
        FOREIGN KEY (piece_comptable_id) REFERENCES pieces_comptables(id),\
        FOREIGN KEY (code_compta_id) REFERENCES codecompta(id),\
        FOREIGN KEY (code_analytique_id) REFERENCES code_analytique(id)\
        )")
        self.exec_("CREATE UNIQUE INDEX idx_CODE ON codecompta (CODE)")
        self.exec_("CREATE UNIQUE INDEX idx_NOM ON fournisseurs (NOM)")
        self.exec_("CREATE TABLE inputs(\
        id INTEGER PRIMARY KEY,\
        date varchar(10),\
        montant real,\
        comment varchar(30) )")

    def connect_db(self, db_name):
        self.db.setDatabaseName(db_name)
        self.db.open()
        self.query = QSqlQuery()

        #Tables model
        self.tables = {}
        self.tables['pieces_comptables'] = TableModel(self, self.db)
        self.tables['pieces_comptables'].setTable('pieces_comptables')
        self.tables['pieces_comptables'].relational_mapping(
            ["fournisseurs","id","NOM",1,"Fournisseur"],
            ["type_payement","id","NOM",4,"Moyen de payement"])
        self.tables['pieces_comptables'].setHeaderData(0, Qt.Horizontal, "Identification")
        self.tables['subdivisions'] = TableModel(self, self.db)
        self.tables['subdivisions'].setTable('subdivisions')
        self.tables['subdivisions'].relational_mapping(
            ["codecompta","code","NOM",3,"Catégorie comptable"],
            ["code_analytique","code","NOM",4,"Catégorie analytique"])
        self.tables['inputs'] = InputsModel(self, self.db)
        self.qt_table_infos = InfosModel(self, self.db)
        self.qt_table_inputs = InputsModel(self, self.db)
        self.globals_datas = GlobalModel()
        self.g_model = GSqlModel()

    def get_fournisseurs(self):
        self.exec_("SELECT NOM, ID FROM fournisseurs")
        return self.query2dic()

    def get_codesCompta(self):
        self.exec_("SELECT NOM, CODE FROM codecompta")
        return self.query2dic()

    def get_codes_analytiques(self):
        self.exec_("SELECT nom, code FROM code_analytique ORDER BY code DESC")
        return self.query2dic()

    def get_typesPayement(self):
        self.query.exec_("SELECT NOM, ID FROM type_payement")
        return self.query2dic()

    def add(self, datas, table):
        col_title = ', '.join([str(i) for i in list(datas.keys())])
        values = []
        for value in list(datas.values()):
            if type(value) == str:
                values.append("'"+value+"'")
            else:
                values.append(str(value))
        values = ', '.join(values)
        query = "INSERT INTO "+table+" ("+col_title+') VALUES('+values+')'
        result = self.exec_(query)
        if result == True:
            self.refresh_model(table)
        return result

    def refresh_model(self, table):
        pass    

    def get_last_id(self, table):
        query = "SELECT id FROM "+table+" ORDER BY id DESC LIMIT 1"
        self.exec_(query)
        while self.query.next():
            return self.query.value(0)

    def get_general_totals(self):
        self.exec_('SELECT sum(total) FROM pieces_comptables')
        while self.query.next():
            return self.query.value(0)

    def get_price_by_child(self):
        return self.get_general_totals()\
        / float(self.get_infos()['nombre_enfants'])

    def get_days(self):
        self.exec_("SELECT startdate, enddate FROM infos")
        while self.query.next():
            start = QDate.fromString(self.query.value(0),'yyyy-MM-dd')
            end = QDate.fromString(self.query.value(1), 'yyyy-MM-dd')
        return start.daysTo(end)

    def get_price_by_child_by_day(self):
        return self.get_price_by_child() / float(self.get_days())

    def get_totals_by_payement(self):
        query = "SELECT type_payement.NOM, sum(total) FROM pieces_comptables\
        INNER JOIN type_payement ON type_payement.id = typePayement_id\
        GROUP BY typePayement_id"
        self.exec_(query)
        return self.query2dic()

    def get_totals_by_codecompta(self):
        query = "SELECT codecompta.NOM, sum(prix) FROM subdivisions\
        INNER JOIN codecompta ON codecompta.code = code_compta_id GROUP BY code_compta_id"
        self.exec_(query)
        return self.query2dic()

    def get_totals_by_code_analytique(self):
        query = 'SELECT code_analytique.nom, sum(prix) FROM subdivisions\
        INNER JOIN code_analytique ON code_analytique.code = code_analytique_id\
        GROUP BY code_analytique_id'
        self.exec_(query)
        return self.query2dic()
    
    def get_totals_by_fournisseur(self):
        query = 'SELECT fournisseurs.nom, sum(total) FROM pieces_comptables\
        INNER JOIN fournisseurs ON fournisseurs.id = fournisseur_id\
        GROUP BY fournisseur_id'
        self.exec_(query)
        return self.query2dic()
        
    def query2dic(self):
        dic = {}
        while self.query.next():
            dic[self.query.value(0)] = self.query.value(1)
        return dic

    def get_total(self):
        self.query.exec_("SELECT sum(total) FROM pieces_comptables")
        while self.query.next():
            return self.query.value(0)

    def get_last_rowid(self, table):
        self.exec_("SELECT DISTINCT last_insert_rowid() FROM " + table)
        while self.query.next():
            return self.query.value(0)

    def set_infos(self, directeur_nom=None, directeur_prenom=None, centre=None):
        q = "UPDATE infos SET \
        directeur_nom = '"+directeur_nom+"',\
        directeur_prenom = '" +directeur_prenom+"',\
        centre = '"+centre+"'"
        self.exec_(q)

    def get_infos(self):
        self.exec_('PRAGMA table_info(infos)')
        fields = []
        while self.query.next():
            fields.append(self.query.value(1))
        return self.row2dic(fields=fields, table='infos')
    
    def row2dic(self, fields=[], table=''):
        q = 'SELECT ' + ', '.join(fields) + ' FROM ' + table
        self.exec_(q)
        while self.query.next():
            dic = {}
            for i, field in enumerate(fields):
                dic[field] = self.query.value(i)
            return dic

    def exec_(self, request):
        req = self.query.exec_(request)
        if DEBUG_SQL:
            print(req,":",request)
            if req == False:
                print(self.query.lastError().databaseText())
        return req

    def queryChange(self):
        print("Query Changed!!!!!!!!!!!")

class InfosModel(QSqlTableModel):
    def __init__(self, parent, db):
        super(InfosModel, self).__init__(parent, db)

        self.setTable("infos")
        self.select()

class InputsModel(QSqlTableModel):
    def __init__(self, parent, db):
        super(InputsModel, self).__init__(parent, db)
        self.setTable("inputs")
        self.select()
"""
class InputsOuputsModel(QAbstractProxyModel):
    def __init__(self, parent, db):
        super(InputsOutputsModel, self).__init__(parent, db)
        
    def mapFromSource(self):
        return None
"""
# test... s'instancie avec succès :p
class GlobalModel(QAbstractItemModel):
    def __init__(self):
        super(GlobalModel).__init__()
    def index(self, row, column):
        return self.createIndex(row, column)
    def parent(self):
        return QModelIndex()
    def rowCount(self):
        return 0
    def columnCount(self):
        return 0
    def data(self):
        return "Ma donnée!!!"

class GSqlModel(QSqlQueryModel):
    def __init__(self):
        super(GSqlModel, self).__init__()
        self.query = "SELECT sum(montant) from inputs"
        self.setHeaderData(0, Qt.Horizontal, "Argent disponible")
        self.refresh()
    def refresh(self):
        self.setQuery(self.query)

class TableModel(QSqlRelationalTableModel):
    def __init__(self, parent, db):
        super(TableModel, self).__init__(parent, db)

    def relational_mapping(self, *args):
        """
        relation : [table, id, reference, nbr_col, name_col]
        """
        for relation in args:
            rel = QSqlRelation(relation[0], relation[1], relation[2])
            self.setRelation(relation[3], rel)
            self.setHeaderData(relation[3], Qt.Horizontal, relation[4])
        self.select()

