#!/usr/bin/python3
# -*- coding: utf-8 -*- 

from PyQt5.QtSql import QSqlQueryModel, QSqlDatabase, QSqlQuery, QSqlRelationalTableModel, QSqlRelation, QSqlTableModel
from PyQt5.QtCore import Qt, QDate, QAbstractItemModel, QSortFilterProxyModel

DEBUG_SQL = True

class Model(QSqlQueryModel):
    def __init__(self, parent=None):
        super(Model, self).__init__(parent)
        self.db = QSqlDatabase.addDatabase('QSQLITE')

    def create_db(self, db_name, code_centre):
        self.connect_db(db_name)
        self.exec_("PRAGMA foreign_keys = ON")
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
        NOM varchar(20),\
        code_analytique_id int\
        )")
        codes_compta_centre = [
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
        codes_compta_vehicules = [
            "606161, 'Carburant Master'",
            "606162, 'Carburant Crafter'",
            "606163, 'Carburant Trafic'",
            "606164, 'Carburant Vito'",
            "606165, 'Carburant Caravel'",
            "606166, 'Carburant Transporter'",
            "615221, 'Entretient/réparations Master'",
            "615222, 'Entretient/réparations Crafter'",
            "615223, 'Entretient/réparations Trafic'",
            "615224, 'Entretient/réparations Vito'",
            "615225, 'Entretient/réparations Caravel'",
            "615226, 'Entretient/réparations Transporter'",
            ]
        for code in codes_compta_centre:
            self.exec_("INSERT INTO codecompta (code, nom, code_analytique_id)\
            VALUES ("+code+", "+str(code_centre)+")")
        for code in codes_compta_vehicules:
            self.exec_("INSERT INTO codecompta (code, nom, code_analytique_id)\
            VALUES ("+code+", 100)")

        self.exec_("CREATE TABLE type_payement (\
        id integer PRIMARY KEY,\
        NOM varchar(20)\
        )")
        moyens_de_payement = ['Chèque','Espèces','Carte Bancaire','Autre']
        for moyen in moyens_de_payement:
            self.exec_("INSERT INTO type_payement (NOM) VALUES ('"+moyen+"')")
        self.exec_("CREATE TABLE code_analytique (\
        code INTEGER PRIMARY KEY,\
        nom VARCHAR(20))")
        self.exec_("INSERT INTO code_analytique (code, nom) VALUES\
        ("+str(code_centre)+", 'Centre')")
        self.exec_("INSERT INTO code_analytique (code, nom) VALUES\
        (600, 'Véhicule')")
        self.exec_("CREATE TABLE pieces_comptables(\
        id integer PRIMARY KEY,\
        Fournisseur_id integer NOT NULL,\
        Date varchar(10),\
        total real,\
        TypePayement_id int NOT NULL,\
        FOREIGN KEY (Fournisseur_id) REFERENCES fournisseurs(id) ON DELETE NO ACTION,\
        FOREIGN KEY (TypePayement_id) REFERENCES type_payement(id) ON DELETE NO ACTION\
        )")
        self.exec_("CREATE TABLE subdivisions(\
        id INTEGER PRIMARY KEY,\
        designation,\
        piece_comptable_id INTEGER,\
        code_compta_id INTEGER NOT NULL,\
        code_analytique_id INTEGER,\
        prix REAL,\
        FOREIGN KEY (piece_comptable_id) REFERENCES pieces_comptables(id)\
        ON DELETE CASCADE,\
        FOREIGN KEY (code_compta_id) REFERENCES codecompta(code) ON DELETE NO ACTION,\
        FOREIGN KEY (code_analytique_id) REFERENCES code_analytique(code) ON DELETE NO ACTION\
        )")
        self.exec_("CREATE UNIQUE INDEX idx_CODE ON codecompta (CODE)")
        self.exec_("CREATE UNIQUE INDEX idx_NOM_FO ON fournisseurs (NOM)")
        self.exec_("CREATE UNIQUE INDEX idx_CODE_AN ON code_analytique (CODE)")
        self.exec_("CREATE TABLE inputs(\
        id INTEGER PRIMARY KEY,\
        date varchar(10),\
        montant real,\
        comment varchar(30) )")

    def connect_db(self, db_name):
        self.db.setDatabaseName(db_name)
        ok = self.db.open()
        if ok:
            print("Database open.")
        else:
            return False
        self.query = QSqlQuery()
        self.exec_("PRAGMA foreign_keys = ON")

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

        self.general_results = {
            'chiffre_affaire':GeneralResultModel(
                'SELECT sum(montant) FROM inputs',
                'Total Argent Reçu'),
            'Dépenses':GeneralResultModel(
                'SELECT sum(prix) FROM subdivisions',
                'Total dépenses'),
            'Argent_disponible':GeneralResultModel(
                'SELECT (SELECT sum(inputs.montant) from inputs)\
                - (SELECT sum(subdivisions.prix) FROM subdivisions)',
                'Argent Disponible')
                }
        return True

    def get_(self, cols=[], table="", qfilter=""):
        """ Return an array with records """
        query = "SELECT "+", ".join(cols)+" FROM "+table
        if qfilter != "":
            query += " WHERE "+qfilter
        self.exec_(query)
        dataset = []
        while self.query.next():
            line = []
            for i, field in enumerate(cols):
                line.append(self.query.value(i))
            dataset.append(line)
        return dataset

    def get_dict(self, cols=[], table='', qfilter=""):
        """ Return a dictionnary with key, value given at cols parameter """
        if len(cols) != 2:
            raise IndexError('get_dict() takes 2 items array as first argument,\
            which will be key, value of the returned dictionnary')
        else:
            query = "SELECT "+", ".join(cols)+" FROM "+table
            if qfilter != "":
                query += " WHERE "+qfilter
            self.exec_(query)
            return self.query2dic()

    def get_one(self, wanted, table, qfilter_key=None, qfilter_value=None):
        query = "SELECT " + wanted + " FROM " + table+\
        " WHERE "+qfilter_key+" = '"+qfilter_value+"' LIMIT 1"
        self.exec_(query)
        while self.query.next():
            return self.query.value(0)

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

    def delete(self, table, qfilter_key, qfilter_value):
        self.exec_('DELETE FROM '+table+' WHERE '+qfilter_key+' = '+"'"+qfilter_value+"'")

    def update(self, datas={}, table='', qfilter_key=None, qfilter_value=None):
        l = []
        for k, v in datas.items():
            l += [str(k) + "='" + str(v)+"'"]
        self.exec_("UPDATE "+table+" SET "+', '.join(l)+\
        ' WHERE '+qfilter_key+" = '"+qfilter_value+"'")

    def refresh_model(self, table):
        if table in self.tables.keys():
            self.tables[table].select()
            print('Table '+table+' refreshed.')
        else:
            print('Table '+table+' is not present in self.tables models')
        if table in ['inputs', 'subdivisions', 'pieces_comptables']:
            for m in self.general_results.values():
                m.select()

    def get_last_id(self, table):
        query = "SELECT id FROM "+table+" ORDER BY id DESC LIMIT 1"
        self.exec_(query)
        while self.query.next():
            return self.query.value(0)

    def get_general_totals(self):
        self.exec_('SELECT sum(total) FROM pieces_comptables')
        while self.query.next():
            if self.query.value(0) == '' :
                return 0
            else:
                return self.query.value(0)

    def get_price_by_child(self):
        try:
            nbr_enfants = float(self.get_infos()['nombre_enfants'])
        except ValueError:
            return 0
        result = self.get_general_totals() / nbr_enfants
        return round(result, 2)

    def get_days(self):
        self.exec_("SELECT startdate, enddate FROM infos")
        while self.query.next():
            start = QDate.fromString(self.query.value(0),'yyyy-MM-dd')
            end = QDate.fromString(self.query.value(1), 'yyyy-MM-dd')
        return start.daysTo(end)

    def get_price_by_child_by_day(self):
        nbr_days = self.get_days()
        if nbr_days != 0:
            result = self.get_price_by_child() / float(self.get_days())
            return round(result, 2)
        else:
            return 0

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
        return self._row2dic(fields=fields, table='infos')
    
    def _row2dic(self, fields=[], table=''):
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

    def get_pieces_comptables(self):
        self.exec_("SELECT pieces_comptables.id, fournisseurs.nom, date, total, type_payement.nom\
        FROM pieces_comptables\
        INNER JOIN fournisseurs ON fournisseurs.id = Fournisseur_id\
        INNER JOIN type_payement ON type_payement.id = typePayement_id")
        result = []
        while self.query.next():
            result.append([self.query.value(x) for x in range(5)])
        return result

    def get_subdivisions(self):
        self.exec_("SELECT id, designation, piece_comptable_id, codecompta.nom, code_analytique.nom, prix\
        FROM subdivisions\
        INNER JOIN codecompta ON codecompta.CODE = subdivisions.code_compta_id\
        INNER JOIN code_analytique ON code_analytique.CODE = subdivisions.code_analytique_id")
        return self._row2array(6)

    def get_subdivisions_for_export(self):
        self.exec_("SELECT\
        piece_comptable_id,\
        pieces_comptables.Date,\
        fournisseurs.nom,\
        designation,\
        code_compta_id,\
        codecompta.nom,\
        subdivisions.code_analytique_id,\
        prix,\
        type_payement.NOM\
        FROM subdivisions\
        INNER JOIN pieces_comptables ON pieces_comptables.id = piece_comptable_id\
        INNER JOIN fournisseurs ON fournisseurs.id = pieces_comptables.Fournisseur_id\
        INNER JOIN codecompta ON code_compta_id = codecompta.code\
        INNER JOIN type_payement ON typepayement_id = type_payement.id"
        )
        return self._row2array(9)

    def _row2array(self, nbr_col):
        result = []
        while self.query.next():
            result.append([self.query.value(x) for x in range(nbr_col)])
        return result


    def get_piece_by_id(self, id_):
        self.exec_("SELECT fournisseurs.nom, date, total, type_payement.nom\
        FROM pieces_comptables\
        INNER JOIN fournisseurs ON fournisseurs.id = Fournisseur_id\
        INNER JOIN type_payement ON type_payement.id = typePayement_id\
        WHERE pieces_comptables.id = '"+str(id_)+"' LIMIT 1")
        result = {}
        while self.query.next():
            result['fournisseur'] = self.query.value(0)
            result['date'] = self.query.value(1)
            result['total'] = self.query.value(2)
            result['type_payement'] = self.query.value(3)
        self.exec_("SELECT id, designation, codecompta.nom, code_analytique.nom, prix\
        FROM subdivisions\
        INNER JOIN codecompta ON codecompta.CODE = subdivisions.code_compta_id\
        INNER JOIN code_analytique ON code_analytique.CODE = subdivisions.code_analytique_id\
        WHERE piece_comptable_id = '"+str(id_)+"'")
        result['subdivisions'] = []
        while self.query.next():
            sub = {}
            sub['id'] = self.query.value(0)
            sub['designation'] = self.query.value(1)
            sub['piece_comptable'] = id_
            sub['code_compta'] = self.query.value(2)
            sub['code_analytique'] = self.query.value(3)
            sub['prix'] = self.query.value(4)
            result['subdivisions'].append(sub)
        return result

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

class GeneralResultModel():
    def __init__(self, query, label):
        self.model = QSqlQueryModel()
        self.query = query
        self.model.setQuery(self.query)
        self.model.setHeaderData(0, Qt.Horizontal, label)
    def select(self):
        self.model.setQuery(self.query)

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
