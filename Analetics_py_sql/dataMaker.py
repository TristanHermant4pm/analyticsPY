
import os
import sys
import pyodbc
import string

import re
from collections import OrderedDict





def countMatches(c):
	sqlquery = """
		SELECT count(*) 
		FROM PppMatch
		"""

	c.execute(sqlquery)
	rows = cursor.fetchall()



if __name__=="__main__":

	#indicate a user
	if "-u" in sys.argv :
		username = sys.argv[sys.argv.index("-u")+1]

		#indicate a password only if there is a user
		if "-p" in sys.argv :
			password = sys.argv[sys.argv.index("-p")+1]
		else:
			print("You indicated a user but forgot to indicate the password.\nPlease use this syntax : python testpyodbc.py (-u user -p password) (-d) (-dp databaseName)")
			quit()

	else:
		username = 'tristan'
		password = 'PD%Sq3=8'
		#password = '$s4pG0o4!*M'


	if "-d" in sys.argv :
		if sys.argv[sys.argv.index("-d")+1] == 'copy':
			database = 'analyticscopy'
		else:
			database = 'analytics'
	else:
		database = 'analytics'

	if "-dp" in sys.argv :
		database = sys.argv[sys.argv.index("-dp")+1] 

	#****************************************************************************************************************************
	#connect to server
	#****************************************************************************************************************************
	server = '172.20.30.7'

	cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
	cursor = cnxn.cursor()
	#****************************************************************************************************************************


	#****************************************************************************************************************************
	#do the wanted queries
	#****************************************************************************************************************************
	#countMatches(cursor)

	#checkCountyRS(cursor)
	checkCounty(cursor)

	#****************************************************************************************************************************

	#****************************************************************************************************************************
	#close the connection
	#****************************************************************************************************************************
	cnxn.close()
	#****************************************************************************************************************************