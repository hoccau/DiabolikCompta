#!/usr/bin/python3
# -*- coding: utf-8 -*- 

from xlsxwriter import Workbook
from xlsxwriter.utility import xl_rowcol_to_cell
import datetime

def create_xlsx(filename='foo.xlsx', model=None):
    classeur = Workbook(filename)

    header_format = classeur.add_format({
        'bold':True,
        'align':'center',
        'font_color':'#ffffff',
        'bg_color':'#ee2527',
        'border':1,
        'shrink':True
        })
    data_format = classeur.add_format({'border':1})
    date_format = classeur.add_format({'num_format': 'd mmmm yyyy','border':1})
    
    feuille = classeur.add_worksheet("Grand livre comptable")
    names = [
        ["Centre","centre"],
        ["Nom du directeur","directeur_nom"],
        ["Lieu du centre","place"],
        ["Nombre d'enfants","nombre_enfants"],
        ["Début du séjour","startdate"],
        ["Fin du séjour", "enddate"]
        ]
    infos = model.get_infos()
    debut, fin = [from_iso_date(infos[k]) for k in ['startdate', 'enddate']]
    debut, fin = [datetime.datetime.strftime(i, '%d/%m/%Y') for i in [debut, fin]]
    H1 = infos['centre'] + ' (direction : ' + infos['directeur_nom'] + ')'
    H2 = 'Du '+debut + ' au '+fin+' à ' + infos['place'] + '. Avec ' + str(infos['nombre_enfants']) + ' enfants.'
    chapeau_options = {
        'width':600,
        'height':50,
        'font':{'color':'#ffffff'},
        'fill':{'color':'#ee2527'},
        }
    feuille.insert_textbox('A1', H1+'\n'+H2, chapeau_options)

    feuille.set_column('A:A', 6)
    feuille.set_column('B:B', 15)
    feuille.set_column('C:C', 15)
    feuille.set_column('D:D', 17)
    feuille.set_column('F:F', 17)
    feuille.set_column('J:J', 15)

    line_offset = 3
    
    ### Chapeau ###
    names = [
        'N° pièce',
        'Date',
        "Fournisseur",
        "Objet",
        "N° comptable",
        'Libellé comptable',
        'Code analytique',
        'Montant',
        'Cumul',
        'Moyen de payement',
        'N° chèque']
    for i, name in enumerate(names):
        feuille.write(line_offset - 1, i, name, header_format)
    
    ### Datas ###
    subdivisions = model.get_subdivisions_for_export()
    for i, record in enumerate(subdivisions):
        feuille.write(i+line_offset, 0, record[0], data_format) # n° piece
        date = from_iso_date(record[1])
        feuille.write_datetime(i+line_offset, 1, date, date_format)
        for j in range(2, 8): 
            feuille.write(i+line_offset, j, record[j], data_format)
        if i == 0:
            feuille.write_formula(i + line_offset, 8, '= H4', data_format)
        else:
            last_cumul = xl_rowcol_to_cell(i+line_offset - 1, 8)
            montant = xl_rowcol_to_cell(i+line_offset, 7)
            feuille.write_formula(
                i+line_offset,
                8,
                '=' + last_cumul + '+' + montant,
                data_format
                )
        feuille.write(i+line_offset, 9, record[8], data_format) #moyen payement
        feuille.write(i+line_offset, 10, record[9], data_format) #numero de chèque
   
    [feuille.set_row(i, 30) for i in range(3)] # first row to 30 height

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
