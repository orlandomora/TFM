import csv
import json

csvfile = open('JCR-2018.reducido.revisado.csv', 'r')
jsonfile = open('jcr.json', 'w', encoding='UTF-8')

reader = csv.DictReader( csvfile, delimiter=';')
for row in reader:
    row['CATEGORIAS'] = row['CATEGORIAS'].strip('][').split(', ')
    json.dump(row, jsonfile,indent=4)