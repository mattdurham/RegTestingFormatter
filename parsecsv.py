import csv
import sys
import sqlite3
import os
#Get the csv input file
def parse(name,description,inputFile):
    #nameList = inputFile.split('-')
    #name = nameList[0]
    #description = nameList[1] + ' ' + nameList[2]#raw_input('Enter description of regulator: ')
    conn = sqlite3.connect('regtesting.db')
    cursor = conn.cursor()
    cursor.execute('select max(regid) as max from reg')
    regid = 0
    for row in cursor:
        print row
        if row[0] <> None:
            regid = row[0]
    regid = regid + 1
    insertReg = 'insert into reg (regid,regname,description) values (' + str(regid) + " , '" + name + "' , " + "'" + description + "')"
    print insertReg
    cursor.execute(insertReg)
    reader = csv.reader(open("rawoutput/"+ inputFile,'rb'),delimiter='\t')
    first = True
    for row in reader:
        if first == True:
            first = False
            continue
        if row[1].strip() <> '':
            cursor.execute('insert into results (regid,millesecond,reading) values (' + str(regid) + "," + row[0] + "," + row[1] + ")")
    conn.commit()
    cursor.close()
for root, dirs, files in os.walk('rawoutput'):
    for filename in files:
        if '032409' in filename:
            nameList = filename.split('-')
            #output-2liter-15bps-031309.txt.txt
            name = nameList[1]
            description = nameList[2] + " Date: " + nameList[3][0:7] + " on DM7"
            parse(name,description,filename) 
            