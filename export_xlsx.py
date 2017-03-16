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
    price_format = classeur.add_format({'num_format': "0.00 €", 'border':1})
    percent_format = classeur.add_format({'num_format': '0.0" "%', 'border':1})
    
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
        # below: fournisseur, objet, n° comptable, libellé, code analytique
        for j in range(2, 7): 
            feuille.write(i+line_offset, j, record[j], data_format)
        feuille.write(i + line_offset, 7, record[7], price_format) #montant
        if i == 0:
            feuille.write_formula(i + line_offset, 8, '= H4', price_format)
        else:
            last_cumul = xl_rowcol_to_cell(i+line_offset - 1, 8)
            montant = xl_rowcol_to_cell(i+line_offset, 7)
            feuille.write_formula(
                i+line_offset,
                8,
                '= ' + last_cumul + '+' + montant,
                price_format,
                )
        feuille.write(i+line_offset, 9, record[8], data_format) #moyen payement
        feuille.write(i+line_offset, 10, record[9], data_format) #numero de chèque
   
    [feuille.set_row(i, 30) for i in range(3)] # first row to 30 height

    ### Sheet Bilan du sejour ###
    feuille_bilan = classeur.add_worksheet("Bilan du séjour")
    feuille_bilan.insert_textbox(
        'A1',
        "Bilan du séjour",
        chapeau_options)
    totals = model.get_general_totals()
    feuille_bilan.write('I4', "Total des dépenses", header_format)
    feuille_bilan.write('I5', totals, price_format)
    feuille_bilan.merge_range('A4:C4', "Dépenses par type de payement", header_format)
    line_offset = 4
    for i, t in enumerate(model.get_totals_by_payement().items()):
        feuille_bilan.write(line_offset + i, 0, t[0], data_format)
        feuille_bilan.write(line_offset + i, 1, t[1], price_format)
        cell = xl_rowcol_to_cell(line_offset + i, 1)
        feuille_bilan.write_formula(
            line_offset + i,
            2,
            '= '+cell+' $I$5',
            percent_format,
            t[1] / totals 
            )
    #below : seems not work
    #chart = classeur.add_chart({'type': 'line'})
    #chart.add_series({
    #    'values': "=$B$6:$B$9"
    #    })
    #feuille_bilan.insert_chart('A11', chart)

    feuille_bilan.merge_range('E4:G4', "Dépenses par catégorie comptable", header_format)
    for i, t in enumerate(model.get_totals_by_codecompta().items()):
        feuille_bilan.write(line_offset + i, 4, t[0], data_format)
        feuille_bilan.write(line_offset + i, 5, t[1], price_format)
        cell = xl_rowcol_to_cell(line_offset + i, 5)
        feuille_bilan.write_formula(
            line_offset + i,
            6,
            '= '+cell+' / $I$5',
            percent_format,
            t[1] / totals
            )
    
    feuille_bilan.set_column('A:A', 18)
    feuille_bilan.set_column('E:E', 25)
    feuille_bilan.set_column('I:I', 15)

    classeur.close()

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
