#!/usr/bin/python3
# -*- coding: utf-8 -*- 

from xlsxwriter import Workbook
from xlsxwriter.utility import xl_rowcol_to_cell
import datetime

def create_xlsx(filename='foo.xlsx', model=None):
    classeur = Workbook(filename)
    bold = classeur.add_format({'bold': True})

    feuille1 = classeur.add_worksheet("Informations diverses")
    infos_centre = model.get_infos()
    names = [
        "Centre",
        "Nom du directeur",
        "Lieu du centre",
        "Nombre d'enfants",
        "Début du séjour",
        "Fin du séjour"
        ]
    write_infos_sheet(
        names = names,
        infos_dic = infos_centre,
        feuille = feuille1,
        workbook = classeur
        )

    feuille2 = classeur.add_worksheet("Pièces comptables")
    names = ['id','fournisseur','date','total','moyen de payement']
    write_sheet(
        names = names,
        array = model.get_pieces_comptables(),
        feuille = feuille2,
        workbook = classeur
        )

    feuille3 = classeur.add_worksheet("Subdivisions comptables")
    names = [
        'Numéro de pièce',
        'Fournisseur',
        'Date',
        'Montant',
        'Cumul',
        'Code comptable']
    subdivisions = model.get_subdivisions_for_export()
    write_subdivisions_sheet(
        names = names, 
        array = subdivisions,
        feuille = feuille3,
        workbook = classeur
        )

    classeur.close()

def header(f):
    def wrapper(*args, **kwargs):
        header_format = kwargs['workbook'].add_format({
            'bold':True,
            'text_wrap':True,
            'align':'center',
            'font_color':'#ffffff',
            'bg_color':'#ee2527',
            'border':1
            })
        data_format = kwargs['workbook'].add_format({
            'border':1
            })
        nbr_cols = len(kwargs['names'])
        kwargs['feuille'].set_column(0, nbr_cols - 1, 15, data_format)
        kwargs['feuille'].set_row(0, 30)
        for i, name in enumerate(kwargs['names']):
            kwargs['feuille'].write(0, i, name, header_format)
        response = f(*args, **kwargs) #decorated function
    return wrapper

@header
def write_infos_sheet(names=[], infos_dic={}, feuille=None, workbook=None):
    ordered = [
        'centre',
        'directeur_nom',
        'nombre_enfants',
        'place',
        'startdate',
        'enddate'
        ]
    i = 0
    print(infos_dic.items())
    date_format = workbook.add_format({'num_format': 'd mmmm yyyy'})
    for k in ordered:
        if k == 'startdate' or k == 'enddate':
            date = from_iso_date(infos_dic[k])
            if date:
                feuille.write_datetime(1,i, date, date_format)
            else:
                feuille.write(1, i, "Non renseigné")
        else:
            feuille.write(1, i, infos_dic[k])
        i += 1

@header
def write_sheet(names=[], array=[], feuille=None, workbook=None):
    date_format = workbook.add_format({'num_format': 'd mmmm yyyy'})
    for i, row in enumerate(array):
        for j, cell in enumerate(row):
            if j == 2:
                date = from_iso_date(cell)
                if date:
                    feuille.write_datetime(i+1, j, date, date_format)
                else:
                    feuille.write(1, i, "Non renseigné")
            else:
                feuille.write(i+1, j, cell)

@header
def write_subdivisions_sheet(names=[], array=[], feuille=None, workbook=None):
    for i, row in enumerate(array):
        j, idx, last = 0, 0, 6
        while j < last:
            if j == 4:
                if i == 0:
                    feuille.write_formula(i+1, j, '= D2')
                else:
                    last_cumul = xl_rowcol_to_cell(i, j)
                    montant = xl_rowcol_to_cell(i+1, j-1)
                    feuille.write_formula(i+1, j, '=' + last_cumul + '+' + montant)
            elif j == 2:
                date_format = workbook.add_format({'num_format': 'd mmmm yyyy'})
                date = from_iso_date(row[idx])
                if date:
                    feuille.write_datetime(i+1, j, date, date_format)
                else:
                    feuille.write(i+1, j, "Non renseigné")
                idx += 1
            else:
                feuille.write(i+1, j, row[idx])
                idx += 1
            j += 1

def from_iso_date(date):
    try:
        formated_date = datetime.datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        print("value error", date)
        return None
    else:
        return formated_date

__all__ = ['create_xlsx']

if __name__ == '__main__':
    import model
    import sys
    sqlmodel = model.Model()
    sqlmodel.connect_db(sys.argv[1])
    create_xlsx(model=sqlmodel)
