#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtSql import QSqlQueryModel, QSqlDatabase, QSqlQuery, QSqlRelationalTableModel, QSqlRelation, QSqlTableModel
from PyQt5.QtCore import Qt, QDate

DEBUG_SQL = True

class Model(QSqlQueryModel):
    def __init__(self, parent=None):
        super(Model, self).__init__(parent)
        self.db = QSqlDatabase.addDatabase('QSQLITE')

    def create_db(self, db_name, code_centre):
        connected = self.connect_db(db_name)
        if connected:
            with open('create_db.sql', 'r', encoding='utf-8') as f:
            # NOTE: With QT SQLite driver, we cannot execute many requests in
            # one time. So, we parse the file:
                r = f.read()
                # split requests and remove the last one because it's empty
                r = r.split(';')[:-1]
            for query in r:
                self.exec_(query)
            # import Diabolo codes
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
                "626100, 'Postes & Télécom'",
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
                "615529, 'Entretient/réparations Transporter'",
                ]
            # There is one code_analytique by centre (given by user)
            self.exec_(
                "INSERT INTO code_analytique (code, nom) VALUES\
                ("+str(code_centre)+", 'Centre')")
            self.exec_(
                "INSERT INTO code_analytique (code, nom) VALUES\
                (100, 'Véhicule')")
            for code in codes_compta_centre:
                self.exec_(
                    "INSERT INTO codecompta (code, nom, code_analytique_id)\
                    VALUES ("+code+", "+str(code_centre)+")")
            for code in codes_compta_vehicules:
                self.exec_(
                    "INSERT INTO codecompta (code, nom, code_analytique_id)\
                    VALUES ("+code+", 100)")

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
            ["fournisseurs", "id", "NOM", 1, "Fournisseur"],
            ["type_payement", "id", "NOM", 4, "Moyen de payement"])
        self.tables['pieces_comptables'].setHeaderData(
                0, Qt.Horizontal, "Identification")
        self.tables['pieces_comptables'].setHeaderData(
                5, Qt.Horizontal, "Numero de chèque")
        self.tables['subdivisions'] = TableModel(self, self.db)
        self.tables['subdivisions'].setTable('subdivisions')
        self.tables['subdivisions'].relational_mapping(
            ["codecompta", "code", "NOM", 3, "Catégorie comptable"],
            ["code_analytique", "code", "NOM", 4, "Catégorie analytique"])
        self.tables['pieces_comptables'].setHeaderData(
                2, Qt.Horizontal, "N° de pièce comptable")
        self.tables['inputs'] = InputsModel(self, self.db)
        self.tables['retraits'] = RetraitsModel(self, self.db)
        self.qt_table_infos = InfosModel(self, self.db)
        self.qt_table_inputs = InputsModel(self, self.db)

        self.general_results = {
            'chiffre_affaire': GeneralResultModel(
                'SELECT total(montant) FROM inputs',
                'Total Argent Reçu'),
            'Dépenses': GeneralResultModel(
                'SELECT total(prix) FROM subdivisions',
                'Total dépenses'),
            'Argent_disponible': GeneralResultModel(
                'SELECT (SELECT total(inputs.montant) from inputs)\
                - (SELECT total(subdivisions.prix) FROM subdivisions)',
                'Argent Disponible'),
            'Liquide_disponible': GeneralResultModel(
                'SELECT (SELECT total(montant) FROM retraits_liquide)\
                - (SELECT total(total) FROM pieces_comptables\
                WHERE typePayement_id = 2)',
                'Liquide Disponible')
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
        query = "SELECT " + wanted + " FROM " + table\
            + " WHERE "+qfilter_key+" = '"+qfilter_value+"' LIMIT 1"
        self.exec_(query)
        while self.query.next():
            return self.query.value(0)

    def add(self, datas, table):
        """ add a record to a table. Return True if the query succeed.

        :Args:
            datas: dict of col_name:value datas
            table: SQL table to add datas
        """
        col_title = ', '.join([str(i) for i in list(datas.keys())])
        values = ', '.join([':'+str(i) for i in list(datas.keys())])
        self.query.prepare(
            "INSERT INTO " + table
            + " (" + col_title + ') VALUES(' + values+')')
        for k, v in datas.items():
            self.query.bindValue(':'+k, v)
        result = self.exec_()
        if result == True:
            self.refresh_model(table)
        return result

    def delete(self, table, qfilter_key, qfilter_value):
        self.exec_('DELETE FROM '+table+' WHERE '+qfilter_key+' = '+"'"+qfilter_value+"'")

    def update(self, datas={}, table='', qfilter_key=None, qfilter_value=None):
        l = []
        for k, v in datas.items():
            l += [str(k) + "='" + str(v)+"'"]
        self.exec_("UPDATE " + table + " SET " + ', '.join(l)
            + ' WHERE ' + qfilter_key + " = '" + qfilter_value + "'")

    def refresh_model(self, table):
        if table in self.tables.keys():
            self.tables[table].select()
            print('Table '+table+' refreshed.')
        else:
            print('refresh nothing: table '+table+' is not present in self.tables models')
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
            if self.query.value(0) == '':
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
            start = QDate.fromString(self.query.value(0), 'yyyy-MM-dd')
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
        INNER JOIN codecompta ON codecompta.code = code_compta_id\
        GROUP BY code_compta_id"
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
        directeur_nom = '" + directeur_nom + "',\
        directeur_prenom = '" + directeur_prenom + "',\
        centre = '" + centre + "'"
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

    def exec_(self, request=None):
        if request:
            req = self.query.exec_(request)
        else:
            req = self.query.exec_()
            request = self.query.lastQuery()
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
        total,\
        type_payement.NOM,\
        cheque_number\
        FROM subdivisions\
        INNER JOIN pieces_comptables ON pieces_comptables.id = piece_comptable_id\
        INNER JOIN fournisseurs ON fournisseurs.id = pieces_comptables.Fournisseur_id\
        INNER JOIN codecompta ON code_compta_id = codecompta.code\
        INNER JOIN type_payement ON typepayement_id = type_payement.id"
        )
        return self._row2array(11)

    def _row2array(self, nbr_col):
        result = []
        while self.query.next():
            result.append([self.query.value(x) for x in range(nbr_col)])
        return result


    def get_piece_by_id(self, id_):
        self.exec_("SELECT fournisseurs.nom, date, total, type_payement.nom, cheque_number\
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
            result['cheque_number'] = self.query.value(4)
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

class RetraitsModel(QSqlTableModel):
    def __init__(self, parent, db):
        super(RetraitsModel, self).__init__(parent, db)
        self.setTable("retraits_liquide")
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
