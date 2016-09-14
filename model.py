from PyQt5.QtSql import QSqlQueryModel, QSqlDatabase, QSqlQuery

class Model(QSqlQueryModel):
    def __init__(self, parent=None):
        super(Model, self).__init__(parent)

        self.db = QSqlDatabase.addDatabase('QSQLITE')

    def create_db(self, db_name):
        self.connect_db(db_name)
        self.query.exec_("CREATE TABLE fournisseurs(\
        NOM varchar(20)\
        )")
        req = self.query.exec_("CREATE TABLE compta(\
        Fournisseur_id integer NOT NULL,\
        Designation varchar(20),\
        Prix real,\
        CodeCompta int NOT NULL,\
        FOREIGN KEY (Fournisseur_id) REFERENCES fournisseurs(rowid))")
        if req == False:
            print self.query.lastError().text()
        self.query.exec_("CREATE TABLE codecompta(\
        CODE int PRIMARY KEY,\
        NOM varchar(20)\
        )")
        self.query.exec_("CREATE UNIQUE INDEX idx_CODE ON codecompta (CODE)")
        self.query.exec_("CREATE UNIQUE INDEX idx_NOM ON fournisseurs (NOM)")

    def connect_db(self, db_name):
        self.db.setDatabaseName(db_name)
        self.db.open()
        self.query = QSqlQuery()

    def get_fournisseurs(self):
        fournisseurs = {}
        self.query.exec_("SELECT NOM, ROWID FROM fournisseurs")
        while self.query.next():
            fournisseurs[self.query.value(0)] = self.query.value(1)
        return fournisseurs

    def get_codeCompta(self):
        codes_compta = []
        self.query.exec_("SELECT NOM, CODE FROM codecompta")
        while self.query.next():
            codes_compta.append([self.query.value(0), self.query.value(1)])
        return codes_compta

    def add_fournisseur(self, name):
        req = self.query.exec_("insert into fournisseurs values('"+name+"')")
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

        print self.query.lastError().text()
        print self.query.lastError().driverText()
        print self.query.lastError().databaseText()

    def set_line(self, datas):
        query = "INSERT INTO compta (Fournisseur_id, Designation, Prix, CodeCompta)"
        query += " VALUES "
        query += "("\
        +str(datas["fournisseur_id"])+",'"\
        +datas["product"]+"',"\
        +datas["price"]+",'"\
        +datas["codeCompta"]\
        +"')"
        print query
        q = self.query.exec_(query)
        print "query success:", q

