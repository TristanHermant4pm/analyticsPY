# -*- coding: utf-8 -*-

import sqlite3


try:
	#conn = sqlite3.connect('172.20.30.7/analytics.db')
	conn = sqlite3.connect('172.20.30.7/analyticscopy.db')

	sqlquery = """
			SELECT count(*) 
			FROM PppMatch
			"""

	cursor.execute(sqlquery)
	rows = cursor.fetchall()

	print(rows)
	'''
	for row in rows:
	    print('{0} : {1} - {2}'.format(row[0], row[1], row[2]))
	'''
except Exception as e:
    print("Erreur : " + str(e))
finally:
    conn.close()