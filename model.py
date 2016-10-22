#!/usr/bin/python3
# -*- coding: utf-8 -*- 

from PyQt5.QtSql import QSqlQueryModel, QSqlDatabase, QSqlQuery, QSqlRelationalTableModel, QSqlRelation, QSqlTableModel
from PyQt5.QtCore import Qt

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
        directeur_prenom varchar(20)\
        )")
        self.exec_("INSERT INTO infos(\
        centre, directeur_nom, directeur_prenom) VALUES (\
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
        (200, 'centre')")
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

    def connect_db(self, db_name):
        self.db.setDatabaseName(db_name)
        self.db.open()
        self.query = QSqlQuery()
        self.qt_table_compta = QSqlRelationalTableModel(self, self.db)
        self.update_table_model()
        self.qt_table_infos = InfosModel(self, self.db)

    def update_table_model(self):
        self.qt_table_compta.setTable('pieces_comptables')
        f_rel = QSqlRelation("fournisseurs","id","NOM")
        c_rel = QSqlRelation("codecompta","code","NOM")
        p_rel = QSqlRelation("type_payement","id","NOM")
        self.qt_table_compta.setRelation(1, f_rel)
        self.qt_table_compta.setRelation(5, c_rel)
        self.qt_table_compta.setRelation(6, p_rel)
        self.qt_table_compta.select()
        self.qt_table_compta.setHeaderData(0, Qt.Horizontal, "Identification")
        self.qt_table_compta.setHeaderData(1, Qt.Horizontal, "Fournisseur")
        self.qt_table_compta.setHeaderData(5, Qt.Horizontal, "Code")
        self.qt_table_compta.setHeaderData(6, Qt.Horizontal, "Moyen de payement")

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

    def add_fournisseur(self, name):
        req = self.exec_("insert into fournisseurs (nom) values('"+name+"')")
        return req

    def add_code_compta(self, code, name):
        query = "INSERT INTO codecompta (CODE, NOM) VALUES ("\
        +str(code)+",'"+name+"')"
        req = self.exec_(query)
        return req

    def add_piece_comptable(self, datas):
        query = "INSERT INTO pieces_comptables (Fournisseur_id,  Date,\
        Total, TypePayement_id)"
        query += " VALUES ("\
        +str(datas["fournisseur_id"])+",'"\
        +str(datas["date"])+"',"\
        +datas["total"]+","\
        +str(datas["typePayement_id"])\
        +")"
        self.exec_(query)

    def add_subdivision(self, datas):
        query = "INSERT INTO subdivisions (\
        piece_comptable_id, code_compta_id, code_analytique_id, prix) VALUES("\
        +str(datas['piece_comptable_id'])+','\
        +str(datas['code_compta_id'])+','\
        +str(datas['code_analytique_id'])+','\
        +str(datas['prix'])+')'
        q = self.exec_(query)
        return q

    def get_last_id(self):
        query = "SELECT id FROM pieces_comptables ORDER BY id DESC LIMIT 1"
        self.exec_(query)
        while self.query.next():
            return self.query.value(0)

    def get_totals_by_payement(self):
        query = "SELECT type_payement.NOM, sum(total) FROM pieces_comptables\
        INNER JOIN type_payement ON type_payement.id = typePayement_id\
        GROUP BY typePayement_id"
        self.exec_(query)
        return self.query2dic()

    def get_totals_by_codecompta(self):
        query = "SELECT codecompta.NOM, sum(total) FROM pieces_comptables\
        INNER JOIN codecompta ON codecompta.code = codecompta GROUP BY codecompta"
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

    def get_last_id(self, table):
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
        q= "SELECT directeur_nom, directeur_prenom, centre FROM infos"
        req = self.query.exec_(q)
        if self.query.isValid():
            while self.query.next():
                print(self.query.value(0), self.query.value(1), self.query.value(2))
                return self.query.value(0), self.query.value(1), self.value(2)
        else:
            return " ", " ", " "
        
    def exec_(self, request):
        req = self.query.exec_(request)
        if DEBUG_SQL:
            print(req,":",request)
            if req == False:
                print(self.query.lastError().databaseText())
        return req

class InfosModel(QSqlTableModel):
    def __init__(self, parent, db):
        super(InfosModel, self).__init__(parent, db)

        self.setTable("infos")
        self.select()
