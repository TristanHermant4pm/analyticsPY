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
#connections.create_connection(hosts=['http://172.20.30.70:9200/'])

#elasticServer = 'http://172.20.30.70:9200/'	#prod
elasticServer = 'http://172.20.31.19:9200/'		#dev

client = Elasticsearch(hosts=[elasticServer])


#q = Q('bool', must=[Q('match', index='propertypriceregister'), Q('match', Type='propertypriceregister')])
q = Q('match', id='_search')
s = Search(using=client, index="propertypriceregister", doc_type="propertypriceregister").query()

s2 = Search(using=client, index="daft", doc_type="daftproperty").query()
s3 = Search(using=client, index="myhome", doc_type="myhomeproperty").query()
s4 = Search(using=client, index="daftdrop", doc_type="daftdropproperty").query()

'''
count = s.count()
for i in range(0, (count / 1000) + 1):

response = s[(i*1000):((i+1)*1000)].execute()
#response = s.execute()

print('Total %d hits found.' % response.hits.total)
'''

nbhit = 0
nbPerfectMatch = 0
nbNotPerfectMatch = 0
nbDaftPerfectMacth = 0
nbDaftdropPerfectMacth = 0
nbMyHomePefectMacth = 0
nbHasPerfectMatchPrice = 0
nbHasnoPerfectMatchPrice = 0
nbPriceDiffer = 0
nbPriceSame = 0

DaftAndDatfdropAndMyhome = 0
DaftAndDatfdropAndNotMyhome = 0
DaftAndNotDatfdropAndMyhome = 0
DaftAndNotDatfdropAndNotMyhome = 0
NotDaftAndDatfdropAndMyhome = 0
NotDaftAndDatfdropAndNotMyhome = 0
NotDaftAndNotDatfdropAndMyhome = 0
NotDaftAndNotDatfdropAndNotMyhome = 0


averagePriceDiff = []

for hit in s.scan():
	if hit["hasPerfectMatch"] == True:
		nbPerfectMatch += 1
		if "price" in hit["perfectMatches"]:
			nbHasPerfectMatchPrice += 1
			if hit["price"] != hit["perfectMatches"].price:
				nbPriceDiffer += 1
			else:
				nbPriceSame += 1

			averagePriceDiff.append(hit["perfectMatches"].price/hit["price"])


		else:
			nbHasnoPerfectMatchPrice += 1

		if "daftPerfectMatch" in hit["perfectMatches"]:
			nbDaftPerfectMacth += 1
		if "myhomePerfectMatch" in hit["perfectMatches"]:
			nbMyHomePefectMacth += 1
		if "daftdropPerfectMatch" in hit["perfectMatches"]:
			nbDaftdropPerfectMacth += 1

		if "daftPerfectMatch" in hit["perfectMatches"] :
			if "daftdropPerfectMatch" in hit["perfectMatches"]:
				if "myhomePerfectMatch" in hit["perfectMatches"]:
					DaftAndDatfdropAndMyhome += 1
				else:
					DaftAndDatfdropAndNotMyhome += 1
			else:
				if "myhomePerfectMatch" in hit["perfectMatches"]:
					DaftAndNotDatfdropAndMyhome += 1
				else:
					DaftAndNotDatfdropAndNotMyhome += 1
		else:
			if "daftdropPerfectMatch" in hit["perfectMatches"]:
				if "myhomePerfectMatch" in hit["perfectMatches"]:
					NotDaftAndDatfdropAndMyhome += 1
				else:
					NotDaftAndDatfdropAndNotMyhome += 1
			else:
				if "myhomePerfectMatch" in hit["perfectMatches"]:
					NotDaftAndNotDatfdropAndMyhome += 1
				else:
					NotDaftAndNotDatfdropAndNotMyhome += 1

	else:
		nbNotPerfectMatch += 1
	nbhit += 1
	

print("nb total in propertypriceregister : " + str(nbhit))
print("has perfect match : " + str(nbPerfectMatch))
print("has not a perfect match : " + str(nbNotPerfectMatch))
print("check sum : " + str((nbPerfectMatch + nbNotPerfectMatch) == nbhit))

print("has perfect match price : " +  str(nbHasPerfectMatchPrice))
print("has not a perfect match price : " + str(nbHasnoPerfectMatchPrice))
print("check sum : " + str((nbHasPerfectMatchPrice + nbHasnoPerfectMatchPrice) == nbPerfectMatch))

print("has same perfect match price and price : " + str(nbPriceSame))
print("has different perfect match price and price : " + str(nbPriceDiffer))
print("check sum : " + str((nbPriceSame + nbPriceDiffer) == nbHasPerfectMatchPrice))

print("proportion of hasPerfectMatch : " + str( (100 * nbPerfectMatch/nbhit)) + "%")
print("proportion of hasNotPerfectMatch : " + str( (100 * nbNotPerfectMatch/nbhit)) + "%")
print("proportion of hasPerfectMatchPrice : " + str( (100 * nbHasPerfectMatchPrice/nbhit)) + "% ; "  + str( (100 * nbHasPerfectMatchPrice/nbPerfectMatch)) + "%")
print("proportion of hasNotPerfectMatchPrice : " + str( (100 * nbHasnoPerfectMatchPrice/nbhit)) + "% ; "  + str( (100 * nbHasnoPerfectMatchPrice/nbPerfectMatch)) + "%")
print("proportion of has same PerfectMatchPrice and price: " + str( (100 * nbPriceSame/nbhit)) + "% ; "  + str( (100 * nbPriceSame/nbPerfectMatch)) + "% ; " + str( (100 * nbPriceSame/nbHasPerfectMatchPrice)) + "%")
print("proportion of has different PerfectMatchPrice and price: " + str( (100 * nbPriceDiffer/nbhit)) + "% ; "  + str( (100 * nbPriceDiffer/nbPerfectMatch)) + "% ; " + str( (100 * nbPriceDiffer/nbHasPerfectMatchPrice)) + "%")
print()
print()

averagePriceDiff_serie = pd.Series(averagePriceDiff)
display.display(averagePriceDiff_serie.describe())
print()

averageAbsPriceDiff = np.absolute(averagePriceDiff)

averageAbsPriceDiff_serie = pd.Series(averageAbsPriceDiff)
display.display(averageAbsPriceDiff_serie.describe())


print()
print()
print("nb total in daft : " + str(s2.count()))
print("nb total in daftdrop : " + str(s4.count()))
print("nb total in myhome : " + str(s3.count()))

print("has perfect match : " + str(nbPerfectMatch))
print()
print("Daft And Datfdrop And Myhome : " + str(DaftAndDatfdropAndMyhome))
print("Daft And Datfdrop Andnot Myhome : " + str(DaftAndDatfdropAndNotMyhome))
print("Daft Andnot Datfdrop And Myhome : " + str(DaftAndNotDatfdropAndMyhome))
print("Daft Andnot Datfdrop Andnot Myhome : " + str(DaftAndNotDatfdropAndNotMyhome))
print("not Daft And Datfdrop And Myhome : " + str(NotDaftAndDatfdropAndMyhome))
print("not Daft And Datfdrop Andnot Myhome : " + str(NotDaftAndDatfdropAndNotMyhome))
print("not Daft Andnot Datfdrop And Myhome : " + str(NotDaftAndNotDatfdropAndMyhome))
print("not Daft Andnot Datfdrop Andnot Myhome : " + str(NotDaftAndNotDatfdropAndNotMyhome))

mysum = (DaftAndDatfdropAndMyhome 
	+ DaftAndDatfdropAndNotMyhome 
	+ DaftAndNotDatfdropAndMyhome 
	+ DaftAndNotDatfdropAndNotMyhome 
	+ NotDaftAndDatfdropAndMyhome
	+ NotDaftAndDatfdropAndNotMyhome
	+ NotDaftAndNotDatfdropAndMyhome
	+ NotDaftAndNotDatfdropAndNotMyhome)

print("check sum : " + str(mysum) + " == " + str(nbPerfectMatch) + " : " + str(mysum  ==  nbPerfectMatch))


print()
print("is a daft perfectMatch : " + str(nbDaftPerfectMacth))
print("is a daftdrop perfectMatch : " + str(nbDaftdropPerfectMacth))
print("is a myhome perfectMatch : " + str(nbMyHomePefectMacth))
print("check sum : " + str((nbDaftPerfectMacth + nbMyHomePefectMacth + nbDaftdropPerfectMacth)) + " == "  + str(nbPerfectMatch) + " : " + str((nbDaftPerfectMacth + nbMyHomePefectMacth + nbDaftdropPerfectMacth ) == nbPerfectMatch))


v = venn3(
	subsets = (
		DaftAndNotDatfdropAndNotMyhome,
		NotDaftAndDatfdropAndNotMyhome,
		DaftAndDatfdropAndNotMyhome,
		NotDaftAndNotDatfdropAndMyhome,
		DaftAndNotDatfdropAndMyhome,
		NotDaftAndDatfdropAndMyhome,
		DaftAndDatfdropAndMyhome
		),
	set_labels = ('Daft', 'DaftDrop', 'MyHome'))

v.get_label_by_id('100').set_text('Daft : ' + str(DaftAndNotDatfdropAndNotMyhome))
v.get_label_by_id('010').set_text('DaftDrop : ' + str(NotDaftAndDatfdropAndNotMyhome))
v.get_label_by_id('110').set_text('Daft ∩ DaftDrop : ' + str(DaftAndDatfdropAndNotMyhome))
v.get_label_by_id('001').set_text('MyHome : ' + str(NotDaftAndNotDatfdropAndMyhome))
v.get_label_by_id('101').set_text('Daft ∩ MyHome : ' + str(DaftAndNotDatfdropAndMyhome))
v.get_label_by_id('011').set_text('DaftDrop ∩ MyHome : ' + str(NotDaftAndDatfdropAndMyhome))
v.get_label_by_id('111').set_text('Daft ∩ DaftDrop ∩ MyHome : ' + str(DaftAndDatfdropAndMyhome))

plt.show()


'''
response = s.execute()

print(response.success())
# True

print(response.took)
# 12

#print(response.to_dict())

nbhit = 0
for h in response.hits.hits:
	nbhit += 1
	#print(h)
	#print(str(key) + " : " + str(value) + "\n")

print("nb hits dispo " + str(nbhit) + " ...")
'''

'''
client = Elasticsearch()

s = Search(using=client, index="my-index") \
		.filter("term", category="search") \
		.query("match", title="python")	 \
		.exclude("match", description="beta")

s.aggs.bucket('per_tag', 'terms', field='tags') \
		.metric('max_lines', 'max', field='lines')

response = s.execute()

for hit in response:
		print(hit.meta.score, hit.title)

for tag in response.aggregations.per_tag.buckets:
		print(tag.key, tag.max_lines.value)
'''