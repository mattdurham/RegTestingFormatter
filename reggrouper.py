import sys
import sqlite3
import matplotlib.pyplot as plt
import matplotlib
import os
import creategraph

BIG = 300
THUMB = 50
REG_TESTING = 'regtesting/'
#REG_TESTING = ''

class reggroup:
    def __init__(self,groupid):
        self.groupid = groupid
        conn = sqlite3.connect('regtesting.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('select * from reggroup where groupid = ' + str(self.groupid))
        row = cursor.fetchone()
        self.groupname = row['groupname']
        self.testdate = row['testdate']
        self.setup = row['setup']
        cursor.execute('select * from reg where groupid =' + str(self.groupid))
        self.someregs = []
        if os.access(REG_TESTING+self.groupname,os.F_OK) ==False:
            os.mkdir(REG_TESTING+self.groupname)
        for row in cursor:
            thereg = regresult(row['regid'])
            self.someregs.append(thereg)
        if os.access(REG_TESTING+self.groupname,os.F_OK) ==False:
            os.mkdir(REG_TESTING+self.groupname)
        self.createGroupGraph()
        
    def createGroupGraph(self):
        listAllReadings = {}
        for reg in self.someregs:
            listAllReadings[reg.regname]=reg.results.values()
        creategraph.createMultiShotGraph(listAllReadings,REG_TESTING+self.groupname+'/'+self.groupname + '.png',self.groupname,BIG)
        creategraph.createMultiShotGraph(listAllReadings,REG_TESTING+self.groupname+'/'+self.groupname + '_thumb.png',self.groupname,THUMB)
        listAllReadings = {}
        for reg in self.someregs:
            listAllReadings[reg.regname + '_firstshot'] = reg.singleshotreadings
        creategraph.createMultiShotGraph(listAllReadings,REG_TESTING+self.groupname+'/'+self.groupname + '_firstshot.png',self.groupname+' First Shot',BIG)
        creategraph.createMultiShotGraph(listAllReadings,REG_TESTING+self.groupname+'/'+self.groupname + '_firstshotthumb.png',self.groupname+ ' First Shot',THUMB)
        
    def createHTML(self):
        results = open(REG_TESTING+self.groupname+'.shtml','w')
        results.write('<html>\n')
        results.write('<body>\n')
        results.write('<style type="text/css"><!--@import url("test.css");--></style>\n')
        results.write('<h1><span style="font-family: Helvetica,Arial,sans-serif;text-align: center;"><a href="howto.html">How to read these graphs</a></span></h1>')
        results.write('<h1><span style="font-family: Helvetica,Arial,sans-serif;text-align: center;">Test Name: %s</span></h1>' % self.groupname)
        results.write('<h1><span style="font-family: Helvetica,Arial,sans-serif;text-align: center;">Test Setup: %s</span></h1>' % self.setup)
        results.write('<h1><span style="font-family: Helvetica,Arial,sans-serif;text-align: center;">Test Date: %s</span></h1>' % self.testdate)
        results.write('<a href="%s/%s" target="_blank"><img src="%s/%s"/></a>' % (self.groupname,self.groupname+'.png',self.groupname,self.groupname+'_thumb.png'))
        results.write('<a href="%s/%s" target="_blank"><img src="%s/%s"/></a>' % (self.groupname,self.groupname+'_firstshot.png',self.groupname,self.groupname+'_firstshotthumb.png'))
        regcursor = conn.cursor()
        regcursor.execute('select * from reg where groupid =' + str(self.groupid))
        for regrow in regcursor:
            path = str(regrow['regid']) + '_' + str(regrow['regname']) + '.html'
            results.write('<!--#include virtual="%s" --> \n' % path )
        results.write('</html>\n')
        results.write('</body>\n')
        results.close()
        
class regresult:
    def __init__(self,regid):
        self.regid = regid
        conn = sqlite3.connect('regtesting.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('select * from reg where regid = ' + str(self.regid))
        row = cursor.fetchone()
        name = str(row['regid']) + '_' + str(row['regname'])
        self.path = name
        self.description = row['description']
        self.regname = row['regname']
        self.groupid = row['groupid']
        self.results = {}
        if os.access(REG_TESTING+self.path,os.F_OK) ==False:
           os.mkdir(REG_TESTING+self.path)
        resCursor = conn.cursor()
        resCursor.execute('select * from results where regid = ' + str(row['regid']))
        print('Regid:' + str(row['regid']))
        self.singleshottitle =  str(self.regid)+'_FirstShot_'+self.regname
        for row in resCursor:
            self.results[row['millesecond']] = row['reading']            
        print('number of rows: '  + str(len(self.results)))
        self.startingPoint  = 0.0
        self.lowerBound = 0.0
        resCursor.execute(' select min(millesecond) as minimum from results where regid = ' +  str(row['regid']))
        min = resCursor.fetchone()['minimum']
        self.startingPoint = self.results[min]
        self.lowerBound = self.startingPoint *.90 # 5% lower bound
        self.boundToReturn = self.startingPoint * .95
        self.shotStarted = 0
        self.shotEnded = 0
        inShot = False
        filtered = {}
        for key in self.results.keys():
          item = self.results[key]
          if item <= self.lowerBound and inShot == False:
              filtered[key-1] = self.results[key-1]
              self.shotStarted = key
              filtered[key] = item
              inShot = True
              continue
          if inShot:
              filtered[key] = item
              if item > self.boundToReturn:
                  self.shotEnded = key
                  break
        listtimes = filtered.keys()
        listtimes.sort()
        self.singletimes = listtimes
        self.singleshotreadings = []
        for key in self.singletimes:
            self.singleshotreadings.append( filtered[key])

    def createCSVData(self,filepath):
        write = open(filepath+'.csv','w')
        write.write(self.path+'\n')
        for value in self.listClean:
            write.write(str(value)+'\n')
        write.close()
    
    def createHTML(self):
        template = open('template.html','r').read()
        conn = sqlite3.connect('regtesting.db')
        conn.row_factory = sqlite3.Row
        if os.access(REG_TESTING+self.path,os.F_OK) ==False:
           os.mkdir(REG_TESTING+self.path)
        listSingleShot = creategraph.createSingleShot(self.path,self.singletimes,self.singleshotreadings,self.path + '/' + self.path + '_single',self.regid)
        listSpread = self.createSpread()
        self.listClean = []
        listSortedKeys = self.results.keys()
        listSortedKeys.sort()
        for key in listSortedKeys:
           self.listClean.append(self.results[key])
        self.createCSVData(REG_TESTING+self.path+'/'+self.path)
        title = self.path
        rawDataLink = self.path+'/'+self.path+'.csv'
        folder =self.path
        fullSpreadThumb=listSpread[1]
        fullSpread=listSpread[0]
        singleThumb=listSingleShot[1]
        single=listSingleShot[0]
        #Dictionary holding the formatting strings
        formatDict = {}
        formatDict['summary'] = title 
        formatDict['description'] = self.description
        formatDict['dataurl'] = rawDataLink
        formatDict['folder'] = folder
        formatDict['spreadpng'] = fullSpread
        formatDict['spreadpngthumb'] = fullSpreadThumb
        formatDict['singlepng'] = single
        formatDict['singlepngthumb'] = singleThumb
        newTemplate = template % formatDict
        write = open(REG_TESTING+title+'.html','w')
        write.write(newTemplate)
        write.close()
        return title+'.html'
    def createSpread(self):
        paths = []
        paths.append(self.path+'/'+self.path+'.png')
        paths.append(self.path+'/'+self.path+'_thumb.png')
        creategraph.createGraph(self.results.keys(),self.results.values(),REG_TESTING+self.path + '/' + self.path,self.path,BIG)
        creategraph.createGraph(self.results.keys(),self.results.values(),REG_TESTING+self.path + '/' + self.path+'_thumb',self.path,THUMB)
        return paths
    
if __name__ == "__main__":
    conn = sqlite3.connect('regtesting.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('select * from reg')
    regs = []
    for row in cursor:
        print str(row['regid'])
        regres = regresult(row['regid'])
        regres.createHTML()
        regs.append(regres)
    #Create the grouping shtml files
    groupFiles = {}
    cursor.execute('select * from reggroup')
    for row in cursor:
        group = reggroup(row['groupid'])
        groupFiles[group.groupname+'.shtml'] = group
        group.createHTML()
    results = open('regtesting/results.shtml','w')
    results.write('<html>\n')
    results.write('<body>\n')
    results.write('<style type="text/css"><!--@import url("test.css");--></style>\n')
    results.write('<h1><span style="font-family: Helvetica,Arial,sans-serif;text-align: center;"><a href="howto.html">How to read these graphs</a></span></h1>')
    results.write('<h1><span style="font-family: Helvetica,Arial,sans-serif;text-align: center;">These results are all the collected results and as such are not directly comparable, individual groupings are available at the below links.</span></h1>')
    for groupFile in groupFiles.keys():
        results.write('<h1><span style="font-family: Helvetica,Arial,sans-serif;text-align: center;"><a href="%s">%s</a></span></h1>' % (groupFile,groupFiles[groupFile].groupname))
    for reg in regs:
        results.write('<!--#include virtual="%s" --> \n' % (reg.path +'.html') )
    results.write('</html>\n')
    results.write('</body>\n')
    results.close()
