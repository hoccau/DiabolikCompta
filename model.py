#!/usr/bin/python
# -*- coding: utf-8 -*- 

from PyQt5.QtSql import QSqlQueryModel, QSqlDatabase, QSqlQuery, QSqlRelationalTableModel, QSqlRelation
from PyQt5.QtCore import Qt

class Model(QSqlQueryModel):
    def __init__(self, parent=None):
        super(Model, self).__init__(parent)

        self.db = QSqlDatabase.addDatabase('QSQLITE')

    def create_db(self, db_name):
        self.connect_db(db_name)
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
        Designation varchar(20),\
        Prix real,\
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

    def update_table_model(self):
        self.qt_table_compta.setTable('compta')
        f_rel = QSqlRelation("fournisseurs","id","NOM")
        c_rel = QSqlRelation("codecompta","code","NOM")
        p_rel = QSqlRelation("type_payement","id","NOM")
        self.qt_table_compta.setRelation(1, f_rel)
        self.qt_table_compta.setRelation(4, c_rel)
        self.qt_table_compta.setRelation(5, p_rel)
        self.qt_table_compta.select()
        self.qt_table_compta.setHeaderData(0, Qt.Horizontal, "Identification")
        self.qt_table_compta.setHeaderData(1, Qt.Horizontal, "Fournisseur")
        self.qt_table_compta.setHeaderData(4, Qt.Horizontal, "Code")
        self.qt_table_compta.setHeaderData(5, Qt.Horizontal, "Moyen de payement")

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
        query = "INSERT INTO compta (Fournisseur_id, Designation, Prix, CodeCompta, TypePayement_id)"
        query += " VALUES "
        query += "("\
        +str(datas["fournisseur_id"])+",'"\
        +datas["product"]+"',"\
        +datas["price"]+","\
        +str(datas["codeCompta_id"])+","\
        +str(datas["typePayement_id"])\
        +")"
        print query
        q = self.query.exec_(query)
        print "query success:", q


