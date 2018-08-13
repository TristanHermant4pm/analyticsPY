from datetime import datetime
from elasticsearch import Elasticsearch

# by default we connect to localhost:9200
es = Elasticsearch(hosts=['http://172.20.30.70:9200/'])

'''
# datetimes will be serialized
es.index(index="my-index", doc_type="test-type", id=42, body={"any": "data", "timestamp": datetime.now()})
{u'_id': u'42', u'_index': u'my-index', u'_type': u'test-type', u'_version': 1, u'ok': True}
'''

# but not deserialized
response = es.get(index="propertypriceregister", doc_type="propertypriceregister", id="_search")


print(response["hits"]["total"])


nbhit = 0
for h in response["hits"]["hits"]:
	nbhit += 1
	#print(h)
	#print(str(key) + " : " + str(value) + "\n")

print("nb hits dispo " + str(nbhit) + " ...")
