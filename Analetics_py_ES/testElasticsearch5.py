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
import pandas as pd
from IPython import display
import numpy as np
from matplotlib_venn import venn3
from matplotlib import pyplot as plt

# Define a default Elasticsearch client
elasticServer = 'http://172.20.30.70:9200/'		#prod
#elasticServer = 'http://172.20.31.19:9200/'	#dev

client = Elasticsearch(hosts=[elasticServer])


q = Q('match', id='_search')
s = Search(using=client, index="propertypriceregister", doc_type="propertypriceregister").query()


print("processing")

inPerfectMatch = []
for hit in s.scan():
	if hit["hasPerfectMatch"] == True:
		
		for field in hit["perfectMatches"]:
			if field not in inPerfectMatch:
				inPerfectMatch.append(field)
print("processing finished")
print()

for field in inPerfectMatch:
	print(str(field))
