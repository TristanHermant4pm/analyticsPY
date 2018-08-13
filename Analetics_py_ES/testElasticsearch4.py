#Copyright © 2018 4propertyLabs. 
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#		http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.


from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, connections, query, Q
import logging
import numpy as np
from datetime import date, timedelta


#***********************************************************************************************************************************
#functions
#***********************************************************************************************************************************

"""
This is a mock process function
it normally return a dictionary of the informations I want to keep
"""
def process(response):

	nbhit = 0

	for hit in response:
		nbhit += 1

	return nbhit

"""
This is a mock processByDate function

it normally return a dictionnary that is a summ of all the dictionary
"""
def processByDate(ns, search, date_min, date_max, timeDelta):
	total_summed = 0 	

	for i in range(0, ns):

		s_filtered = search.filter('range', saleDate = {"gte": date_min, "lte" : date_max})

		total_summed += process(s_filtered.execute())

		date_min -= timeDelta
		date_max -= timeDelta

	return total_summed

#***********************************************************************************************************************************



#***********************************************************************************************************************************
#main
#***********************************************************************************************************************************

# Define a default Elasticsearch client
elasticServer = 'http://172.20.30.70:9200/'	#prod
#elasticServer = 'http://172.20.31.19:9200/' #dev

client = Elasticsearch(hosts=[elasticServer])

q = Q('match', id='_search')

s = Search(using=client, index="propertypriceregister", doc_type="propertypriceregister").query()

numbersSteps = 106 #(52 weeks/years * 8 years / 4 ) + 2  // which is way before the first data's saleDate => I should have all the data
t = timedelta(weeks = 4)


d_max = date.today() 
d_min = d_max - timedelta(weeks = 3, days = 6)


total_summed = processByDate(numbersSteps, s, d_min, d_max, t)


print("******************************************************************")
print("Total (summed) : " + str(total_summed))
print("******************************************************************")
print()
print("******************************************************************")
print("Total (real) : " + str(process(s.scan())))
print("******************************************************************")
print()
print("******************************************************************")
print("Total (count) : " + str(s.count()))
print("******************************************************************")