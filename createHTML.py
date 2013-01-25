import sqlite3
import creategraph
import os

def CreateHTML(regid):
    template = open('template.html','r').read()
    conn = sqlite3.connect('regtesting.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('select * from reg where regid = ' + str(regid))
    row = cursor.fetchone()
    path = str(row['regid']) + '_' + str(row['regname'])
    description = row['description']
    if os.access(path,os.F_OK) ==False:
        os.mkdir(path)
    listSingleShot = creategraph.createSingleShot(path + '/' + path + '_single',row['regid'])
    listSpread = creategraph.createSpread(path + '/' + path + '_spread',row['regid'])
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
    creategraph.createCSVData(path+'/'+path,path,listClean)
    title = path
    rawDataLink = path+'/'+path+'.csv'
    folder =path
    fullSpreadThumb=listSpread[1]
    fullSpread=listSpread[0]
    singleThumb=listSingleShot[1]
    single=listSingleShot[0]
    #Dictionary holding the formatting strings
    formatDict = {}
    formatDict['summary'] = title 
    formatDict['description'] = description
    formatDict['dataurl'] = rawDataLink
    formatDict['folder'] = folder
    formatDict['spreadpng'] = fullSpread
    formatDict['spreadpngthumb'] = fullSpreadThumb
    formatDict['singlepng'] = single
    formatDict['singlepngthumb'] = singleThumb
    newTemplate = template % formatDict
    write = open(title+'.html','w')
    write.write(newTemplate)
    write.close()
    return title+'.html'

conn = sqlite3.connect('regtesting.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute('select * from reg')
files = []
for row in cursor:
    print str(row['regid'])
    files.append(CreateHTML(row['regid']))
#Create the grouping shtml files
groupFiles = {}
cursor.execute('select * from reggroup')
for row in cursor:
    groupid = row['groupid']
    groupname = row['groupname']
    testdate = row['testdate']
    setup = row['setup']
    results = open(groupname+'.shtml','w')
    results.write('<html>\n')
    results.write('<body>\n')
    results.write('<style type="text/css"><!--@import url("test.css");--></style>\n')
    results.write('<h1><span style="font-family: Helvetica,Arial,sans-serif;text-align: center;"><a href="howto.html">How to read these graphs</a></span></h1>')
    results.write('<h1><span style="font-family: Helvetica,Arial,sans-serif;text-align: center;">Test Name: %s</span></h1>' % groupname)
    results.write('<h1><span style="font-family: Helvetica,Arial,sans-serif;text-align: center;">Test Setup: %s</span></h1>' % setup)
    results.write('<h1><span style="font-family: Helvetica,Arial,sans-serif;text-align: center;">Test Date: %s</span></h1>' % testdate)
    regcursor = conn.cursor()
    regcursor.execute('select * from reg where groupid =' + str(groupid))
    for regrow in regcursor:
        path = str(regrow['regid']) + '_' + str(regrow['regname']) + '.html'
        results.write('<!--#include virtual="%s" --> \n' % path )
    groupFiles[groupname+'.shtml'] = groupname
    results.write('</html>\n')
    results.write('</body>\n')
    results.close()
results = open('results.shtml','w')
results.write('<html>\n')
results.write('<body>\n')
results.write('<style type="text/css"><!--@import url("test.css");--></style>\n')
results.write('<h1><span style="font-family: Helvetica,Arial,sans-serif;text-align: center;"><a href="howto.html">How to read these graphs</a></span></h1>')
results.write('<h1><span style="font-family: Helvetica,Arial,sans-serif;text-align: center;">These results are all the collected results and as such are not directly comparable, individual groupings are available at the below links.</span></h1>')
for groupFile in groupFiles.keys():
    results.write('<h1><span style="font-family: Helvetica,Arial,sans-serif;text-align: center;"><a href="%s">%s</a></span></h1>' % (groupFile,groupFiles[groupFile]))
for thefile in files:
    results.write('<!--#include virtual="%s" --> \n' % thefile )
results.write('</html>\n')
results.write('</body>\n')
results.close()

