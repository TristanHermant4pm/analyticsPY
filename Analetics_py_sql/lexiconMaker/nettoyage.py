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
file_pointer = open(".\\lexicons\\censusTownList.txt", "r")

for line in file_pointer.read().split("\n"):
	ctListIn.append(str(line))


file_pointer.close()


print(str(len(ctListIn)))

for line in ctListIn:
	line = re.sub("\((.)*\)", r"", line)

	line = re.sub(",(\s)*(County|Co.){0,1} (\w+(\s){0,1})*\|\w+", r"", line)

	line2 = ""
	for sent in line.split(";"):


		m = re.search("(?!(County|Co.) )\w+(?=\|)", sent)

		if m == None:
			County = ""
		else:
			County = m.group(0) 

		sent = re.sub("(County|Co.) \w+\|\w+", str(County), sent)
		line2 += sent + ";"

	line2 = re.sub(" ", r"", line2)

	if line2.endswith(";"):
		line2 = line2[:-1]

	line2 = re.sub("\|\w+", r"", line2)

	ctListOut.append(str(line2))

print(str(len(ctListOut)))

ctListOut = sorted(ctListOut)

with open(".\\lexicons\\censusTownListN.txt", "w+") as filepointer:
	for line in ctListOut:
		filepointer.write(str(line)+ "\n")