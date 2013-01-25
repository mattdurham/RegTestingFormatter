import sys
import sqlite3
import matplotlib.pyplot as plt
import matplotlib

def createGraph(resultDict,title,addText):
    listTime = []
    listReadings = []
    keyList = resultDict.keys()
    keyList.sort()
    for key in keyList:
        listTime.append(key)
        listReadings.append(resultDict[key])
    plt.cla()
    plt.plot(listTime,listReadings)
    plt.ylabel('Pressure in psi')
    plt.xlabel('Time in Milleseconds')
    plt.title(title + '-' + addText)
    plt.savefig('images/'+title.replace('/',''),dpi=300)

conn = sqlite3.connect('regtesting.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute('select * from reg')
title =''
for row in cursor:
    title = str(row['regid'])+'_FirstShot_'+row['regname']
    results = {}
    resCursor = conn.cursor()
    resCursor.execute('select * from results where regid = ' + str(row['regid']))
    for row in resCursor:
        results[row['millesecond']] = row['reading']
    startingPoint  = 0.0
    lowerBound = 0.0
    startingPoint = results[0]
    lowerBound = startingPoint *.90 # 5% lower bound
    boundToReturn = startingPoint * .95
    shotStarted = 0
    shotEnded = 0
    inShot = False
    filtered = {}
    for key in results.keys():
        item = results[key]
        if item <= lowerBound and inShot == False:
            filtered[key-1] = results[key-1]
            shotStarted = key
            filtered[key] = item
            inShot = True
            continue
        if inShot:
            filtered[key] = item
            if item > boundToReturn:
                shotEnded = key
                break
    createGraph(filtered,title,'Ms to reach 95% of starting: ' + str(shotEnded - shotStarted))
    print 'Title: ' + title
    print 'Starting Point: ' + str(startingPoint)
    print 'Lower Bound: ' + str(lowerBound)
    print 'Shot Started: ' + str(shotStarted)
    print 'Shot Ended: ' + str(shotEnded)
    print 'Milleseconds to reach 95% of starting: ' + str(shotEnded - shotStarted)
    print ''
print 'done'
