import os
import sys
import pyodbc
import string

import re
from collections import OrderedDict



ctListIn = []
ctListOut = []


'''
import codecs
types_of_encoding = ["utf8", "cp1252"]
for encoding_type in types_of_encoding:
	with codecs.open(".\\lexicons\\censusTownList.txt", encoding = encoding_type, errors ='replace') as file_pointer:
		for line in file_pointer.readlines():
			ctList.append(line)

'''
file_pointer = open(".\\lexicons\\niPostalcodeRaw.txt", "r")

for line in file_pointer.read().split("\n"):
	ctListIn.append(str(line))


file_pointer.close()


print(str(len(ctListIn)))

i = 0
currentTown = ""

for line in ctListIn:
	g = re.search("[a-z]", line)
	if g != None:
		currentTown = line
	else:
		i += 1
		if currentTown != "":
			ctListOut.append((line, currentTown))
		else:
			print("debug 1")


print(str(len(ctListOut)))

'''
for key, value in ctListOut:
	print(key + " : " + value)
'''
'''
ctListOut = sorted(ctListOut)
'''

with open(".\\lexicons\\niPostalcode.txt", "w+") as filepointer:
	filepointer.write("Postal code;City Name\n")
	for el in ctListOut:
		filepointer.write(el[0] + ";" + el[1] +  "\n")
