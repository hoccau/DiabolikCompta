#!/usr/bin/python
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
        Cumul real,\
        CodeCompta int NOT NULL,\
        TypePayement_id int NOT NULL,\
        FOREIGN KEY (Fournisseur_id) REFERENCES fournisseurs(id),\
        FOREIGN KEY (TypePayement_id) REFERENCES type_payement(id)\
        )")
        if req == False:
            print self.query.lastError().text()
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
        self.qt_table_compta.setRelation(6, c_rel)
        self.qt_table_compta.setRelation(7, p_rel)
        self.qt_table_compta.select()
        self.qt_table_compta.setHeaderData(0, Qt.Horizontal, "Identification")
        self.qt_table_compta.setHeaderData(1, Qt.Horizontal, "Fournisseur")
        self.qt_table_compta.setHeaderData(6, Qt.Horizontal, "Code")
        self.qt_table_compta.setHeaderData(7, Qt.Horizontal, "Moyen de payement")

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
            print self.query.lastError().databaseText()
            return self.query.lastError().databaseText()
        else:
            return req

    def add_code_compta(self, code, name):
        query = "INSERT INTO codecompta (CODE, NOM)"
        query += " VALUES "
        query += "("+str(code)+",'"+name+"')"
        print "query:", query
        req = self.query.exec_(query)
        print "req:", req
        if req == False:
            return self.query.lastError().databaseText()
        else:
            return True

    def set_line(self, datas):
        last_cumul = self.get_last_cumul()
        query = "INSERT INTO compta (Fournisseur_id,  Date, Designation, Prix, Cumul, CodeCompta, TypePayement_id)"
        query += " VALUES "
        query += "("\
        +str(datas["fournisseur_id"])+",'"\
        +str(datas["date"])+"','"\
        +datas["product"]+"',"\
        +datas["price"]+","\
        +str(last_cumul + float(datas["price"]))+","\
        +str(datas["codeCompta_id"])+","\
        +str(datas["typePayement_id"])\
        +")"
        print query
        q = self.query.exec_(query)
        print "query success:", q
        if q == False:
            print self.query.lastError().databaseText()

    def get_last_cumul(self):
        query = "SELECT cumul FROM compta ORDER BY id DESC LIMIT 1"
        req = self.query.exec_(query)
        last_cumul = 0
        while self.query.next():
            last_cumul = self.query.value(0)
        return last_cumul

    def compute_cumul_sum(self):
        res = self.query.exec_("SELECT Prix FROM compta")
        cumul = 0
        while self.query.next():
            cumul += self.query.value(0)
        return cumul
        
    def compute_cumul_eff(self, line_id):
        query = "SELECT cumul FROM compta WHERE ID < "\
        +str(line_id)+" ORDER BY id DESC LIMIT 1"
        print "query:", query
        req = self.query.exec_(query)
        if req == False:
            print self.query.lastError().databaseText()
        while self.query.next():
            last_cumul = self.query.value(0)
        return last_cumul + price
        
    def get_last_id(self):
        query = "SELECT id FROM compta ORDER BY id DESC LIMIT 1"
        self.query.exec_(query)
        while self.query.next():
            return self.query.value(0)

    def update_cumul(self, begin_row_id):
        last_id = self.get_last_id()
        for row_id in range(begin_row_id, int(last_id) +1):
            self.query.exec_("SELECT prix FROM compta WHERE id = "+str(row_id))
            price = 0
            while self.query.next():
                price = self.query.value(0)
            self.query.exec_("SELECT cumul FROM compta WHERE id < "+str(row_id)+" ORDER BY id DESC LIMIT 1")
            while self.query.next():
                last_cumul = self.query.value(0)
            cumul = price + last_cumul
            print "cumul:", last_cumul, " prix:", price
            self.query.exec_(
                "UPDATE compta SET cumul = '"+str(cumul)+"' WHERE id = "+str(row_id)
                )

    def get_totals_by_payement(self):
        query = "SELECT type_payement.NOM, sum(prix) FROM compta INNER JOIN type_payement ON type_payement.id = typePayement_id GROUP BY typePayement_id"
        self.query.exec_(query)
        res = {}
        while self.query.next():
            res[self.query.value(0)] = self.query.value(1)
        return res

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
        print "set-infos", q, req

    def get_infos(self):
        q= "SELECT directeur_nom, directeur_prenom, centre FROM infos"
        req = self.query.exec_(q)
        if self.query.isValid():
            while self.query.next():
                print self.query.value(0), self.query.value(1), self.query.value(2)
                return self.query.value(0), self.query.value(1), self.value(2)
        else:
            return " ", " ", " "
        

class InfosModel(QSqlTableModel):
    def __init__(self, parent, db):
        super(InfosModel, self).__init__(parent, db)

        self.setTable("infos")
        self.select()
