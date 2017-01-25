#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Module for exporting reports
"""

from PyQt5.QtCore import QDateTime, QDate
from PyQt5.QtGui import QTextDocument
from PyQt5.QtPrintSupport import QPrinter
import model

def html_2col_table(dic):
    html = '<table border="1"><tr>'
    for key in dic.keys():
        html += '<th>'+key+'</th>'
    html += '</tr>'
    html += '<tr>'
    for value in dic.values():
        html += '<th>'+str(value)+'</th>'
    html += '</tr></table>'
    return html

def create_infos_table(model):
    infos = model.get_infos()
    html = '<table border="1"><tr>'
    html += '<th> Nom du directeur</th>'
    html += '<th> Lieu</th>'
    html += "<th> Nombre d'enfants</th>"
    html += "<th> Début du séjour</th>"
    html += "<th> Fin du séjour</th>"
    html += "<th> Jours</th>"
    html += "</tr><tr>"
    html += "<th>"+infos['directeur_nom']+"</th>"
    html += "<th>"+infos['place']+"</th>"
    html += "<th>"+str(infos['nombre_enfants'])+"</th>"
    start_date = QDate.fromString(infos['startdate'],'yyyy-MM-dd')
    end_date = QDate.fromString(infos['enddate'],'yyyy-MM-dd')
    html += "<th>"+start_date.toString('dd/MM/yyyy')+"</th>"
    html += "<th>"+end_date.toString('dd/MM/yyyy')+"</th>"
    html += '<th>'+str(model.get_days())+'</th>'
    html += '</tr></table>'
    return html

def create_about():
    html = 'Généré par DiabolikCompta le <span id="date">'
    html += QDateTime.currentDateTime().toString('dd/MM/yyyy à HH:mm')
    html += '</span>'
    return html

def create_general_infos(model):
    html = '<h2>Informations comptables générales</h2>'
    html += '<table border="1"><tr>'
    html += '<th>Total du centre</th>'
    html += '<th>Coût moyen par enfant</th>'
    html += '<th>Coût journalier moyen par enfant</th>'
    html += '</tr><tr>'
    html += '<th>'+'{:0.2f}'.format(model.get_general_totals())+'</th>'
    html += '<th>'+'{:0.2f}'.format(model.get_price_by_child())+'</th>'
    html += '<th>'+'{:0.2f}'.format(model.get_price_by_child_by_day())+'</th>'
    html += '</tr></table>'
    return html

def create_general(model):
    html = '<h2>Totaux par moyen de payement</h2>'
    html += html_2col_table(model.get_totals_by_payement())
    html += '<h2>Totaux par code de comptabilité</h2>'
    html += html_2col_table(model.get_totals_by_codecompta())
    html += '<h2>Totaux par code analytique</h2>'
    html += html_2col_table(model.get_totals_by_code_analytique())
    html += '<h2>Totaux par fournisseur</h2>'
    html += html_2col_table(model.get_totals_by_fournisseur())
    return html

def create_pdf(filename='foo.pdf', model=None):
    infos_centre = model.get_infos()
    doc = QTextDocument()
    title = '<h1>Rapport comptable du séjour '+infos_centre['centre']+'</h1>'
    about = '<div id="about">'+create_about()+'</div>'
    logo = '<img src="design/logo.png" align="right"/>'
    infos = '<div id="infos">'+create_infos_table(model)+'</div>'
    general = '<div id="general">'+create_general_infos(model)
    general += create_general(model)+'</div>'
    html = '<body>'+logo+title+about+infos+general+'</body>'
    doc.setHtml(html)
    printer = QPrinter()
    printer.setOutputFileName(filename)
    printer.setOutputFormat(QPrinter.PdfFormat)
    printer.setPageSize(QPrinter.A4)
    doc.print_(printer)

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    sqlmodel = model.Model()
    sqlmodel.connect_db(sys.argv[1])
    app = QApplication(sys.argv)
    create_pdf(model=sqlmodel)
