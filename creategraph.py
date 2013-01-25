import sys
import sqlite3
import matplotlib.pyplot as plt
import matplotlib
import os
BIG = 300
THUMB = 50
COLOR = ('b' , 'g' , 'r' , 'c' , 'm' ,  'y' ,  'k'  ,'#A0A0A0','#3399FF','#CC33FF')

def createGraph(listTime,listReadings,filepath,title,dotsperinch,xMax=None):
    plt.cla()
    plt.plot(listTime,listReadings)
    plt.grid(True)
    plt.ylim(ymin=0);
    if(xMax != None):
        plt.xlim(xmax=xMax)
    plt.ylabel('Pressure in psi')
    plt.xlabel('Time in Milliseconds')
    plt.title(title)
    plt.savefig(filepath,dpi=dotsperinch)

def createMultiShotGraph(dicttimes,filepath,title,dotsperinch,xMax=None):
    plt.cla()
    colorindex = 0
    for key in dicttimes.keys():
        plt.plot(dicttimes[key],COLOR[colorindex],label=key)
        colorindex = colorindex + 1
    plt.grid(True)
    plt.ylim(ymin=0);
    if(xMax != None):
       plt.xlim(xmax=xMax)
    plt.ylabel('Pressure in psi')
    plt.xlabel('Time in Milleseconds')
    plt.title(title)
    plt.legend(loc=4)
    plt.savefig(filepath,dpi=dotsperinch)

def createSingleShot(title,listTimes,listReadings,filePath,regid):
    paths = []
    paths.append(filePath+'.png')
    paths.append(filePath+'_thumb.png')
    if len(listTimes) != 0:
        createGraph(listTimes,listReadings,filePath,title,BIG,listTimes[0] + 150)
        createGraph(listTimes,listReadings,filePath+'_thumb',title,THUMB,listTimes[0] + 150)
    else:
        createGraph(listTimes,listReadings,filePath,title,BIG)
        createGraph(listTimes,listReadings,filePath+'_thumb',title,THUMB)
    return paths
def createCSVData(filepath,header,listvalues):
    write = open(filepath+'.csv','w')
    write.write(header+'\n')
    for value in listvalues:
        write.write(str(value)+'\n')
    write.close()
    
'''
conn = sqlite3.connect('regtesting.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute('select * from reg where regid = 1')
row = cursor.fetchone()
path = str(row['regid']) + '_' + str(row['regname'])
if os.access(path,os.F_OK) ==False:
    os.mkdir(path)
createSingleShot(path + '/' + path + '_single',1)
createSpread(path + '/' + path + '_spread',1)
results = {}
resCursor = conn.cursor()
resCursor.execute('select * from results where regid = ' + str(row['regid']))
for row in resCursor:
    results[row['millesecond']] = row['reading']
listClean = []
listSortedKeys = results.keys()
listSortedKeys.sort()
for key in listSortedKeys:
    listClean.append(results[key])
createCSVData(path+'/'+path,path,listClean)
'''

