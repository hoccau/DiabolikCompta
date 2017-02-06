#!/usr/bin/python3

from xlsxwriter import Workbook
from xlsxwriter.utility import xl_rowcol_to_cell

def create_xlsx(filename='foo.xlsx', model=None):
    infos_centre = model.get_infos()
    classeur = Workbook(filename)
    bold = classeur.add_format({'bold': True})
    feuille1 = classeur.add_worksheet("Informations diverses")
    for i, k in enumerate(list(infos_centre.keys())):
        feuille1.write(0, i, str(k))
    for i, k in enumerate(list(infos_centre.values())):
        feuille1.write(1, i, str(k))

    feuille2 = classeur.add_worksheet("Pièces comptables")
    names = ['id','fournisseur','date','total','moyen de payement']
    write_sheet(names, model.get_pieces_comptables(), feuille2)

    feuille3 = classeur.add_worksheet("Subdivisions comptables")
    names = [
        'Numéro de pièce',
        'Fournisseur',
        'Date',
        'Montant',
        'Cumul',
        'Code comptable']
    subdivisions = model.get_subdivisions_for_export()
    write_subdivisions_sheet(names, subdivisions, feuille3)

def headersheet(f):
    def wrapper(*args, **kwargs):
        names = args[0]
        for i, name in enumerate(names):
            args[2].write(0, i, name)
        return f(*args, **kwargs)
    return wrapper

@headersheet
def write_sheet(names, array, feuille):
    for i, row in enumerate(array):
        for j, cell in enumerate(row):
            feuille.write(i+1, j, cell)

@headersheet
def write_subdivisions_sheet(names, array, feuille):
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
            else:
                feuille.write(i+1, j, row[idx])
                idx += 1
            j += 1

if __name__ == '__main__':
    import model
    import sys
    sqlmodel = model.Model()
    sqlmodel.connect_db(sys.argv[1])
    create_xlsx(model=sqlmodel)
