#!/usr/bin/python3
# -*- coding: utf-8 -*- 

from PyQt5.QtSql import QSqlQueryModel, QSqlDatabase, QSqlQuery, QSqlRelationalTableModel, QSqlRelation, QSqlTableModel
from PyQt5.QtCore import Qt

class Model(QSqlQueryModel):
    def __init__(self, parent=None):
        super(Model, self).__init__(parent)

        self.db = QSqlDatabase.addDatabase('QSQLITE')

    def create_db(self, db_name):
        self.connect_db(db_name)
        self.query.exec_("CREATE TABLE infos(\
        centre varchar(20),\
        directeur_nom varchar(20),\
        directeur_prenom varchar(20)\
        )")
        self.query.exec_("INSERT INTO infos(\
        centre, directeur_nom, directeur_prenom) VALUES (\
        NULL, NULL, NULL)")
        self.query.exec_("CREATE TABLE fournisseurs(\
        id integer PRIMARY KEY,\
        NOM varchar(20)\
        )")
        self.query.exec_("CREATE TABLE codecompta(\
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
            self.query.exec_("INSERT INTO codecompta (code, nom) VALUES ("+code+")")
        self.query.exec_("CREATE TABLE type_payement (\
        id integer PRIMARY KEY,\
        NOM varchar(20)\
        )")
        self.query.exec_("INSERT INTO type_payement (NOM) VALUES ('Chèque')")
        self.query.exec_("INSERT INTO type_payement (NOM) VALUES ('Espèces')")
        self.query.exec_("INSERT INTO type_payement (NOM) VALUES ('Carte Banquaire')")
        req = self.query.exec_("CREATE TABLE compta(\
        id integer PRIMARY KEY,\
        Fournisseur_id integer NOT NULL,\
        Date varchar(10),\
        Designation varchar(20),\
        Prix real,\
        CodeCompta int NOT NULL,\
        TypePayement_id int NOT NULL,\
        FOREIGN KEY (Fournisseur_id) REFERENCES fournisseurs(id),\
        FOREIGN KEY (TypePayement_id) REFERENCES type_payement(id)\
        )")
        if req == False:
            print(self.query.lastError().text())
        self.query.exec_("CREATE UNIQUE INDEX idx_CODE ON codecompta (CODE)")
        self.query.exec_("CREATE UNIQUE INDEX idx_NOM ON fournisseurs (NOM)")

    def connect_db(self, db_name):
        self.db.setDatabaseName(db_name)
        self.db.open()
        self.query = QSqlQuery()
        self.qt_table_compta = QSqlRelationalTableModel(self, self.db)
        self.update_table_model()
        self.qt_table_infos = InfosModel(self, self.db)

    def update_table_model(self):
        self.qt_table_compta.setTable('compta')
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
        fournisseurs = {}
        self.query.exec_("SELECT NOM, ID FROM fournisseurs")
        while self.query.next():
            fournisseurs[self.query.value(0)] = self.query.value(1)
        return fournisseurs

    def get_codesCompta(self):
        codes_compta = {}
        self.query.exec_("SELECT NOM, CODE FROM codecompta")
        while self.query.next():
            codes_compta[self.query.value(0)] = self.query.value(1)
        return codes_compta

    def get_typesPayement(self):
        types_payement = {}
        self.query.exec_("SELECT NOM, ID FROM type_payement")
        while self.query.next():
            types_payement[self.query.value(0)] = self.query.value(1)
        return types_payement

    def add_fournisseur(self, name):
        req = self.query.exec_("insert into fournisseurs (nom) values('"+name+"')")
        if req == False:
            print(self.query.lastError().databaseText())
            return self.query.lastError().databaseText()
        else:
            return req

    def add_code_compta(self, code, name):
        query = "INSERT INTO codecompta (CODE, NOM)"
        query += " VALUES "
        query += "("+str(code)+",'"+name+"')"
        print("query:", query)
        req = self.query.exec_(query)
        print("req:", req)
        if req == False:
            return self.query.lastError().databaseText()
        else:
            return True

    def set_line(self, datas):
        query = "INSERT INTO compta (Fournisseur_id,  Date, Designation, Prix, CodeCompta, TypePayement_id)"
        query += " VALUES "
        query += "("\
        +str(datas["fournisseur_id"])+",'"\
        +str(datas["date"])+"','"\
        +datas["product"]+"',"\
        +datas["price"]+","\
        +str(datas["codeCompta_id"])+","\
        +str(datas["typePayement_id"])\
        +")"
        print(query)
        q = self.query.exec_(query)
        print("query success:", q)
        if q == False:
            print(self.query.lastError().databaseText())

    def get_last_id(self):
        query = "SELECT id FROM compta ORDER BY id DESC LIMIT 1"
        self.query.exec_(query)
        while self.query.next():
            return self.query.value(0)

    def get_totals_by_payement(self):
        query = "SELECT type_payement.NOM, sum(prix) FROM compta INNER JOIN type_payement ON type_payement.id = typePayement_id GROUP BY typePayement_id"
        self.query.exec_(query)
        res = self.query2dic()
        return res

    def get_totals_by_codecompta(self):
        query = "SELECT codecompta.NOM, sum(prix) FROM compta INNER JOIN codecompta ON codecompta.code = codecompta GROUP BY codecompta"
        req = self.query.exec_(query)
        res = self.query2dic()
        return res
        
    def query2dic(self):
        dic = {}
        while self.query.next():
            dic[self.query.value(0)] = self.query.value(1)
        return dic

    def get_total(self):
        self.query.exec_("SELECT sum(prix) FROM compta")
        while self.query.next():
            return self.query.value(0)

    def set_infos(self, directeur_nom=None, directeur_prenom=None, centre=None):
        q = "UPDATE infos SET \
        directeur_nom = '"+directeur_nom+"',\
        directeur_prenom = '" +directeur_prenom+"',\
        centre = '"+centre+"'"
        req = self.query.exec_(q)
        print("set-infos", q, req)

    def get_infos(self):
        q= "SELECT directeur_nom, directeur_prenom, centre FROM infos"
        req = self.query.exec_(q)
        if self.query.isValid():
            while self.query.next():
                print(self.query.value(0), self.query.value(1), self.query.value(2))
                return self.query.value(0), self.query.value(1), self.value(2)
        else:
            return " ", " ", " "
        

class InfosModel(QSqlTableModel):
    def __init__(self, parent, db):
        super(InfosModel, self).__init__(parent, db)

        self.setTable("infos")
        self.select()
