#!/usr/bin/python3

from xlsxwriter import Workbook

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
    write_sheet(model.get_pieces_comptables(), names, feuille2)

    feuille3 = classeur.add_worksheet("Subdivisions comptables")
    names = ['id','Désignation','Pièce comptable ID','Code compta','Code analytique', 'montant']
    write_sheet(model.get_(
        ['id',
        'designation',
        'piece_comptable_id',
        'code_compta_id',
        'code_analytique_id',
        'prix'],
        'subdivisions'), names, feuille3)

def write_sheet(array, names, feuille):
    for i, name in enumerate(names):
        feuille.write(0, i, name)
    for i, row in enumerate(array):
        for j, cell in enumerate(row):
            feuille.write(i+1, j, cell)

if __name__ == '__main__':
    import model
    import sys
    sqlmodel = model.Model()
    sqlmodel.connect_db(sys.argv[1])
    create_xlsx(model=sqlmodel)
