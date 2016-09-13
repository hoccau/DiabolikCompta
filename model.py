from PyQt5.QtSql import QSqlQueryModel, QSqlDatabase, QSqlQuery

class Model(QSqlQueryModel):
    def __init__(self, parent=None):
        super(Model, self).__init__(parent)

        self.db = QSqlDatabase.addDatabase('QSQLITE')

    def create_db(self, db_name):
        self.connect_db(db_name)
        self.query.exec_("CREATE TABLE compta(\
        Fournisseur varchar(20),\
        Designation varchar(20),\
        Prix real,\
        CodeCompta int NOT NULL)")
        self.query.exec_("CREATE TABLE fournisseurs(\
        NOM varchar(20)\
        )")
        self.query.exec_("CREATE TABLE codecompta(\
        CODE int,\
        NOM varchar(20)\
        )")

    def connect_db(self, db_name):
        self.db.setDatabaseName(db_name)
        self.db.open()
        self.query = QSqlQuery()

    def get_fournisseurs(self):
        fournisseurs = []
        self.query.exec_("SELECT NOM FROM fournisseurs")
        while self.query.next():
            fournisseurs.append(self.query.value(0))
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
        return req

    def set_line(self, datas):
        query = "INSERT INTO compta (Fournisseur, Designation, Prix, CodeCompta)"
        query += " VALUES "
        query += "('"+datas[0]+"','"+datas[1]+"',"+datas[2]+","+datas[3]+")"
        print query
        q = self.query.exec_(query)
        print q

