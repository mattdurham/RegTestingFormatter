import sys
import re

inputFile = open('input.txt','r')
lines = inputFile.readlines()
counter = 0;
outFile = open('output.csv','w')
for line in lines:
    if line.strip() != '':
        outFile.write(str(counter)+','+str(float(line)*200)+'\n')
        counter = counter + 1
outFile.close()
    
        