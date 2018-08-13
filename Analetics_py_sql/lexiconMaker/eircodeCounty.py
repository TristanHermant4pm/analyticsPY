import os
import sys
import pyodbc
import string

import re
from collections import OrderedDict
import collections



ctListw1c = {}
ctListwmc = {}
ctListwsc = {}


file_pointer = open(".\\lexicons\\censusTownListWCounty.txt", "r")

#compteur = 0

for line in file_pointer.readlines():
	sents = line.split(";")

	if len(sents) < 2:
		print(sents)

	if len(sents) == 2:
		#compteur += 1
		if sents[0] in ctListw1c:
			if sents[0] in ctListwsc:
				ctListwsc[sents[0]].append(sents[1][:-1] if sents[1].endswith("\n") else sents[1])
			else:
				ctListwsc[sents[0]] = [sents[1][:-1] if sents[1].endswith("\n") else sents[1]]
			#print(sents)
		else:
			ctListw1c[sents[0]] = sents[1][:-1] if sents[1].endswith("\n") else sents[1]

	else:
		if sents[0] in ctListwmc:
			listToAdd = ctListwsc
			if sents[0] in ctListwsc:
				ctListwsc[sents[0]].append(sents[1][:-1] if sents[1].endswith("\n") else sents[1])
			else:
				ctListwsc[sents[0]] = [sents[1][:-1] if sents[1].endswith("\n") else sents[1]]
			#print(sents)
		else:
			listToAdd = ctListwmc
			ctListwmc[sents[0]] = []

		for sent in sents[1:]:
			#compteur += 1
			listToAdd[sents[0]].append(sent[:-1] if sent.endswith("\n") else sent)

	for key in ctListwsc.keys():
		if key in ctListw1c:
			ctListwsc[key].append(ctListw1c[key])
			del ctListw1c[key]
		if key in ctListwmc:
			ctListwsc[key].append(ctListwmc[key])
			del ctListwmc[key]
file_pointer.close()

'''
totalCities = len(ctListw1c) + len(ctListwmc)
for e in ctListwsc.values():
	totalCities += len(e)

print(str(totalCities))

realCompteur = len(ctListw1c)
for e in ctListwmc.values():
	realCompteur += len(e)
for e in ctListwsc.values():
	if isinstance(e, collections.Iterable):
		realCompteur += len(e)
	else:
		realCompteur += 1
	#realCompteur += len(e)

print(str(realCompteur) + " : " + str(compteur))
'''

i = 0
hasCountiesAlready = 0

res = []

file_pointer = open("..\\lexicons\\eircodedescriptor.csv", "r")

c1 = 0
c2 = 0
c3 = 0
mismatchOnCountiesNumber = []
mismatchOnCounties = []
ctIsAmbiguousButHasCounties = []
notInAnyDictButHasCounty = []
ctIsAmbiguous = []
notInAnyDictAndHasNoCounty = []
pbHasNoCity = []


lines = file_pointer.readlines()
fields = (lines[0][:-1] if lines[0].endswith("\n") else lines[0])

for line in lines[1:]:
	i += 1
	sents = line.strip("\n").split(";")

	ssents = len(sents)
	if ssents > 2:
		c1 += 1
		pb = False

		key = (sents[1][:-1] if sents[1].endswith("\n") else sents[1])

		if key in ctListw1c:
			if ssents == 3:
				res.append((line[:-1] if line.endswith("\n") else line))
				hasCountiesAlready += 1
				continue
			else:
				#print("mismatch on counties number : " + str(i) + " : " + line)
				mismatchOnCountiesNumber.append(str(i) + " : " + line)
				pb = True

		if key in ctListwmc:
			nbCountiesForCT = len(ctListwmc[key])
			if ssents == nbCountiesForCT + 2:
				if sents[2:] == ctListwmc[key]:
					res.append((line[:-1] if line.endswith("\n") else line))
					hasCountiesAlready += 1
					continue
				else:
					#print("mismatch on counties : " + str(i) + " : " + line)
					mismatchOnCounties.append(str(i) + " : " + line)
					pb = True
			else:
				#print("mismatch on counties number : " + str(i) + " : " + line)
				mismatchOnCountiesNumber.append(str(i) + " : " + line)
				pb = True

		if pb:
			temp = sents[0] + ";" + (sents[1][:-1] if sents[1].endswith("\n") else sents[1]) 
			for e in ctListwmc[key]:
				temp += ";" + (e[:-1] if e.endswith("\n") else e)
			#temp += "\n"
			res.append(temp)
			continue

		if key in ctListwsc:
			res.append((line[:-1] if line.endswith("\n") else line))
			#print("may be a pb : " + str(i) + " ; " + line)
			ctIsAmbiguousButHasCounties.append(str(i) + " ; " + line)
			continue

		res.append((line[:-1] if line.endswith("\n") else line))
		#print("not in any dict but has a county: " + key + " ; " + str(i) + " : " + line)
		notInAnyDictButHasCounty.append(str(i) + " , " + key + " : " + line)

	if ssents == 2:
		c2 += 1
		#key = (sents[1][:-1] if sents[1].endswith("\n") else sents[1]).lower().capitalize()
		key = (sents[1][:-1] if sents[1].endswith("\n") else sents[1])

		if key in ctListw1c:
			res.append((line[:-1] if line.endswith("\n") else line) + ";" + ctListw1c[key] + "\n")
			continue
		
		if key in ctListwmc:
			temp = (line[:-1] if line.endswith("\n") else line)
			#res += (line[:-1] if line.endswith("\n") else line)
			for e in ctListwmc[key]:
				temp += ";" + (e[:-1] if e.endswith("\n") else e)
			temp += "\n"
			res.append(temp)
			continue

		if key in ctListwsc:
			res.append((line[:-1] if line.endswith("\n") else line))
			#print(str(i) + " : " + line)
			ctIsAmbiguous.append(str(i) + " : " + line)
			continue

		res.append((line[:-1] if line.endswith("\n") else line))
		#print("not in any dict and have no county: " + key + " ; " + str(i) + " : " + line)
		notInAnyDictAndHasNoCounty.append(str(i) + " , " + key + " : " + line)
	
	if ssents < 2:
		c3 += 1
		res.append((line[:-1] if line.endswith("\n") else line))
		#print("PB no city: " + str(i) + " : " + line)
		pbHasNoCity.append(str(i) + " : " + line)
file_pointer.close()



print("\n******************************************************************************************************")
print("line where number of counties do not match with the number of ct counties : " + str(len(mismatchOnCountiesNumber)))
for e in mismatchOnCountiesNumber:
	print(e)

print("\n******************************************************************************************************")
print("line where counties do not match with ct counties : " + str(len(mismatchOnCounties)))
for e in mismatchOnCounties:
	print(e)

print("\n******************************************************************************************************")
print("ct is ambiguous but line has counties: " + str(len(ctIsAmbiguousButHasCounties)))
for e in ctIsAmbiguousButHasCounties:
	print(e)


print("\n******************************************************************************************************")
print("city is not a census town but has counties: " + str(len(notInAnyDictButHasCounty)))
for e in notInAnyDictButHasCounty:
	print(e)

print("\n******************************************************************************************************")
print("ct is ambiguous and line has no counties: " + str(len(ctIsAmbiguous)))
for e in ctIsAmbiguous:
	print(e)

print("\n******************************************************************************************************")
print("city is not a census town and has no counties: " + str(len(notInAnyDictAndHasNoCounty)))
for e in notInAnyDictAndHasNoCounty:
	print(e)

print("\n******************************************************************************************************")
print("line has no city: " + str(len(pbHasNoCity)))
for e in pbHasNoCity:
	print(e)


res = sorted(res)

'''
res2 = []
for line in res:
	sents = line.split(";")
	sents[1] = sents[1].lower().capitalize()

	temp = ""
	for sent in sents:
		temp += (sent[:-1] if sent.endswith("\n") else sent) + ";"

	res2.append(temp[:-1] if temp.endswith(";") else temp)
'''


with open(".\\lexicons\\eircodedescriptor.csv", "w+") as filepointer:
	filepointer.write(fields + "\n")
	for line in res:
		filepointer.write(line + "\n")


print(str(c1) + " + " + str(c2) + " + " + str(c3) + " = " +str(c1+c2+c3))