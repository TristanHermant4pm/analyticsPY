# -*- coding: utf-8 -*-

import os
import sys
import pyodbc
import string
from IPython import display
import pandas as pd

import re
from collections import OrderedDict

def getCountiesList():
	file_pointer = open(".\\lexicons\\roiCountiesList.txt", "r")
	countiesList = []
	for county in file_pointer.readlines():
		countiesList.append(str(county).strip("\n"))
	file_pointer.close()
	return countiesList

"""
return a dictionary using the eircodeRoutingKey as hash and a tuple of Descriptor (as design by eircode) and a list of counties (can be only 1 element) that were match using lexicons
"""
def getEircodeDescriptor():
	file_pointer = open(".\\lexicons\\eircodedescriptor.csv", "r")
	eircodeDescriptorDict = {}
	for line in file_pointer.readlines():
		line = line.split(";")
		eircodeDescriptorDict[str(line[0])] = (str(line[1]), [])
		for e in line[2:]:
			eircodeDescriptorDict[str(line[0])][1].append(e)
	file_pointer.close()
	return eircodeDescriptorDict


def getNorthernIrelandList():
	file_pointer = open(".\\lexicons\\niPostalcode.txt", "r")
	countiesList = []
	for county in file_pointer.readlines():
		countiesList.append(str(county).strip("\n"))
	file_pointer.close()
	return countiesList


def parseRawAdressToGetCounty(ra):
	global listCounties
	global listParsedCounties
	global nbCoFound
	global eircodeDescriptor

	county = ""
	
	#**********************************************************************************************************************
	#find raw address that have an eircode
	#**********************************************************************************************************************
	countyFoundByEircode = ""
	regexERCK = "|".join(eircodeDescriptor.keys()) + "(?!( ){0,1}([a-zA-Z1-9]){4})"

	#([a-zA-Z1-9]){1}( ){0,1}([a-zA-Z1-9]){3}

	g = re.search(regexERCK, ra)
	if g != None:
		parsedECRK = g.group(0)

		if parsedECRK in eircodeDescriptor:
			#if there is only on county for 
			if len(eircodeDescriptor[parsedECRK][1]) == 1:
				#return eircodeDescriptor[parsedECRK][1][0].replace("\n", "").replace(" ", "")
				countyFoundByEircode = eircodeDescriptor[parsedECRK][1][0].replace("\n", "").replace(" ", "")
	#**********************************************************************************************************************


	#**********************************************************************************************************************
	#find county searching for Co.
	#**********************************************************************************************************************
	CountyFoundByCo = []
	countyTemp = ""
	coseenlast = False
	InvalidCountyError = False

	''' #raw address that have either County/county or co. seems to already have Co. ; it doesn't increase the coverage
	reglistCounties = "(" +"|".join(listCounties) + ")"
	g = re.search("(?!^\W)co\.(?= "+reglistCounties +")", ra)
	if g != None:
		ra = re.sub("(?!^\W)co\.(?= "+reglistCounties +")", "Co.", ra)
		
		print()
		print()
		print(ra)
		print(re.sub("(?!^\W)co\.(?= "+reglistCounties +")", "Co.", ra))

	
	g = re.search("(?!^\W)(c|C)ounty(?= "+reglistCounties +")", ra)
	if g != None:
		ra = re.sub("(?!^\W)(c|C)ounty(?= "+reglistCounties +")", "Co.", ra)
		print()
		print()
		print(ra)
		print(re.sub("(?!^\W)(c|C)ounty(?= "+reglistCounties +")", "Co.", ra))
	'''
	ra = ra.replace(" Co.", " ,Co.")
	sentList = ra.split(",")

	for sent in sentList:
		if "Co." in sent or coseenlast:
			#reinit
			coseenlast = False

			nbCoFound += 1
			#countyTemp = sent.replace("Co. ", "")
			countyTemp = sent.replace("Co.", "")

			while countyTemp.startswith(" ") or countyTemp.startswith("."):
				countyTemp = countyTemp[1:]

			while countyTemp.endswith(" ") or countyTemp.endswith("."):
				countyTemp = countyTemp[:-1]

			countyTemp = countyTemp.capitalize()

			if countyTemp == "":
				coseenlast = True
				continue

			if countyTemp in listCounties:
				CountyFoundByCo.append(countyTemp)
				#return countyTemp
			else:
				for c in listCounties:
					if c in countyTemp or c.lower() in countyTemp:
						#return c
						CountyFoundByCo.append(c)

				'''
				used to debug
				'''
				if county not in listParsedCounties:
					listParsedCounties[county] = 1
				else:
					listParsedCounties[county] += 1

				InvalidCountyError = True


	#**********************************************************************************************************************


	#**********************************************************************************************************************
	#find the right county
	#**********************************************************************************************************************
	numCountyFoundByCo = len(CountyFoundByCo)
	if numCountyFoundByCo == 0:
		if countyFoundByEircode != "":
			#county = countyFoundByEircode
			return countyFoundByEircode
		else:
			if InvalidCountyError:
				#if we are here, the county found was not a valid county
				#throwing an error should be done, but since it is just a test...
				return "InvalidCountyError"
	else:
		ambiguous = False
		if numCountyFoundByCo == 1:
			county = CountyFoundByCo[0]
		if numCountyFoundByCo > 1:
			#we look we found the same county multiple times or not
			temp = CountyFoundByCo[0]
			for i in range(1, numCountyFoundByCo):
				if temp != CountyFoundByCo[i]:
					ambiguous = True
			if not ambiguous:
				county = temp

		if (countyFoundByEircode != "" and countyFoundByEircode != county) or ambiguous:
			county == "MultipleCountyError"

	return county


def attic(desc):
	regex = "(A|a)(ttic|TTIC)"

	g = re.search(regex, desc)
	if g != None:
		return True
	else: 
		return False

def alarm(desc):
	regex = "(A|a)(larm|LARM)"

	g = re.search(regex, desc)
	if g != None:
		return True
	else: 
		return False

def parking(desc):
	regex = "(P|p)(arking|ARKING)"

	g = re.search(regex, desc)
	if g != None:
		return True
	else: 
		return False

def ensuite(desc):
	regex = "(E|e)(suite|SUITE)"

	g = re.search(regex, desc)
	if g != None:
		return True
	else: 
		return False


def centralHeating(desc):
	regex = "(c|C)(entral|ENTRAL)( |-){0,1}(h|H)(eating|EATING)"

	g = re.search(regex, desc)
	if g != None:
		return True
	else: 
		return False

def oilHeating(desc):
	regex = "(o|O)(il|IL)( |-){0,1}(h|H)(eating|EATING)"

	g = re.search(regex, desc)
	if g != None:
		return True
	else: 
		return False

def gazHeating(desc):
	regex = "(g|G)(az|AZ)( |-){0,1}(h|H)(eating|EATING)"

	g = re.search(regex, desc)
	if g != None:
		return True
	else: 
		return False



#****************************************************************************************************************************
# queries functions
#****************************************************************************************************************************
def dataMaker(cnxn):
	c = cnxn.cursor()

	sqlquery = """
		SELECT PropertyPriceRegister.Id, PropertyPriceRegister.SaleDate, PropertyPriceRegister.Price, PropertyPriceRegister.PostalCode, PropertyPriceRegister.NotFullMarketPrice, PropertyPriceRegister.PropertyDescription, PropertyPriceRegister.County, PropertyPriceRegister.PropertySizeDescription, PropertyPriceRegister.Area, PropertyPriceRegister.Region, PropertyPriceRegister.Latitude, PropertyPriceRegister.Longitude, PropertyPriceRegister.Neighborhood, PropertyPriceRegister.InconsistentAddress, PropertyPriceRegister.GeocodePrecision, PropertyPriceRegister.FixedAddress, PropertyPriceRegister.DeclaredCounty, PropertyPriceRegister.PresentPrice, PppMatchDaftProperty.PppId, PppMatchDaftProperty.DaftPerfectMatchId, PppMatchDaftProperty.Id, PppMatchDaftProperty.Area, PppMatchDaftProperty.Region, PppMatchDaftProperty.Price, PppMatchDaftProperty.MarketType, PppMatchDaftProperty.Beds, PppMatchDaftProperty.Baths, PppMatchDaftProperty.Description, PppMatchDaftProperty.DateEntered, PppMatchDaftProperty.LastUpdate, PppMatchDaftProperty.Latitude, PppMatchDaftProperty.Longitude, PppMatchDaftProperty.Ber, PppMatchDaftProperty.RawAddress, PppMatchDaftProperty.PostalCode, PppMatchDaftProperty.SqrMetres, PppMatchDaftProperty.SaleAgreed, PppMatchDaftProperty.SaleAgreedDate
		FROM PropertyPriceRegister
		INNER JOIN (
			SELECT m.PppId as PppId, m.DaftPerfectMatchId as DaftPerfectMatchId, d.Id as Id, d.Area as Area, d.Region as Region, d.Price as Price, d.MarketType as MarketType, d.Beds as Beds, d.Baths as Baths, d.Description as Description, d.DateEntered as DateEntered, d.LastUpdate as LastUpdate, d.Latitude as Latitude, d.Longitude as Longitude, d.Ber as Ber, d.RawAddress as RawAddress, d.PostalCode as PostalCode, d.SqrMetres as SqrMetres, d.SaleAgreed as SaleAgreed, d.SaleAgreedDate as SaleAgreedDate
			FROM PppMatch as m
			INNER JOIN DaftProperty as d
			ON m.DaftPerfectMatchId = d.Id
			WHERE DaftPerfectMatchId IS NOT NULL
			) as PppMatchDaftProperty
		ON PppMatchDaftProperty.PppId = PropertyPriceRegister.Id
		"""

	c.execute(sqlquery)
	rows = c.fetchall()

	result1 = []

	'''
	col = [
		'PropertyPriceRegister_Id',
		'PropertyPriceRegister_SaleDate',
		'PropertyPriceRegister_Price',
		'PropertyPriceRegister_PostalCode',
		'PropertyPriceRegister_NotFullMarketPrice',
		'PropertyPriceRegister_PropertyDescription',
		'PropertyPriceRegister_County',
		'PropertyPriceRegister_PropertySizeDescription',
		'PropertyPriceRegister_Area',
		'PropertyPriceRegister_Region',
		'PropertyPriceRegister_Latitude',
		'PropertyPriceRegister_Longitude',
		'PropertyPriceRegister_Neighborhood',
		'PropertyPriceRegister_InconsistentAddress',
		'PropertyPriceRegister_GeocodePrecision',
		'PropertyPriceRegister_FixedAddress',
		'PropertyPriceRegister_DeclaredCounty',
		'PropertyPriceRegister_PresentPrice',
		'PppMatchDaftProperty_PppId',
		'PppMatchDaftProperty_DaftPerfectMatchId',
		'PppMatchDaftProperty_Id',
		'PppMatchDaftProperty_Area',
		'PppMatchDaftProperty_Region',
		'PppMatchDaftProperty_Price',
		'PppMatchDaftProperty_MarketType',
		'PppMatchDaftProperty_Beds',
		'PppMatchDaftProperty_Baths',
		'PppMatchDaftProperty_Description',
		'PppMatchDaftProperty_DateEntered',
		'PppMatchDaftProperty_LastUpdate',
		'PppMatchDaftProperty_Latitude',
		'PppMatchDaftProperty_Longitude',
		'PppMatchDaftProperty_Ber',
		'PppMatchDaftProperty_RawAddress',
		'PppMatchDaftProperty_PostalCode',
		'PppMatchDaftProperty_SqrMetres',
		'PppMatchDaftProperty_SaleAgreed',
		'PppMatchDaftProperty_SaleAgreedDate'
	]
	data = pd.DataFrame.from_records(rows, columns=col)
	display.display(data.describe())
	'''


	nbHaveNone = 0

	PropertyPriceRegister_Id_nbNone = 0
	PropertyPriceRegister_SaleDate_nbNone = 0
	PropertyPriceRegister_Price_nbNone = 0
	PropertyPriceRegister_PostalCode_nbNone = 0
	PropertyPriceRegister_NotFullMarketPrice_nbNone = 0
	PropertyPriceRegister_PropertyDescription_nbNone = 0
	PropertyPriceRegister_County_nbNone = 0
	PropertyPriceRegister_PropertySizeDescription_nbNone = 0
	PropertyPriceRegister_Area_nbNone = 0
	PropertyPriceRegister_Region_nbNone = 0
	PropertyPriceRegister_Latitude_nbNone = 0
	PropertyPriceRegister_Longitude_nbNone = 0
	PropertyPriceRegister_Neighborhood_nbNone = 0
	PropertyPriceRegister_InconsistentAddress_nbNone = 0
	PropertyPriceRegister_GeocodePrecision_nbNone = 0
	PropertyPriceRegister_FixedAddress_nbNone = 0
	PropertyPriceRegister_DeclaredCounty_nbNone = 0
	PropertyPriceRegister_PresentPrice_nbNone = 0
	PppMatchDaftProperty_PppId_nbNone = 0
	PppMatchDaftProperty_DaftPerfectMatchId_nbNone = 0
	PppMatchDaftProperty_Id_nbNone = 0
	PppMatchDaftProperty_Area_nbNone = 0
	PppMatchDaftProperty_Region_nbNone = 0
	PppMatchDaftProperty_Price_nbNone = 0
	PppMatchDaftProperty_MarketType_nbNone = 0
	PppMatchDaftProperty_Beds_nbNone = 0
	PppMatchDaftProperty_Baths_nbNone = 0
	PppMatchDaftProperty_Description_nbNone = 0
	PppMatchDaftProperty_DateEntered_nbNone = 0
	PppMatchDaftProperty_LastUpdate_nbNone = 0
	PppMatchDaftProperty_Latitude_nbNone = 0
	PppMatchDaftProperty_Longitude_nbNone = 0
	PppMatchDaftProperty_Ber_nbNone = 0
	PppMatchDaftProperty_RawAddress_nbNone = 0
	PppMatchDaftProperty_PostalCode_nbNone = 0
	PppMatchDaftProperty_SqrMetres_nbNone = 0
	PppMatchDaftProperty_SaleAgreed_nbNone = 0
	PppMatchDaftProperty_SaleAgreedDate_nbNone = 0


	countNone_list = []
	Sales_Id_countNone = 0
	Sales_date_countNone = 0
	Sales_price_countNone = 0
	Sales_property_type_countNone = 0
	Sales_surface_countNone = 0
	Sales_longitude_countNone = 0
	Sales_latitude_countNone = 0
	Sales_postcodes_countNone = 0
	Sales_area_countNone = 0
	Sales_bathrooms_countNone = 0
	Sales_beds_countNone = 0
	Sales_ber_id_countNone = 0
	Sales_parking_countNone = 0
	Sales_description_countNone = 0
	Sales_central_heating_countNone = 0
	Sales_alarm_countNone = 0
	Sales_gas_heating_countNone = 0
	Sales_oil_heating_countNone = 0
	attic_conversion_countNone = 0
	ensuites_countNone = 0



	PropertyPriceRegister_Id_list = []
	PppMatchDaftProperty_PppId_List = []
	PppMatchDaftProperty_DaftPerfectMatchId_list = []
	PppMatchDaftProperty_Id_list = []

	PropertyPriceRegister_SaleDate_dict = {}
	PropertyPriceRegister_Price_dict = {}
	PropertyPriceRegister_PostalCode_dict = {}
	PropertyPriceRegister_NotFullMarketPrice_dict = {}
	PropertyPriceRegister_PropertyDescription_dict = {}
	PropertyPriceRegister_County_dict = {}
	PropertyPriceRegister_PropertySizeDescription_dict = {}
	PropertyPriceRegister_Area_dict = {}
	PropertyPriceRegister_Region_dict = {}
	PropertyPriceRegister_Latitude_dict = {}
	PropertyPriceRegister_Longitude_dict = {}
	PropertyPriceRegister_Neighborhood_dict = {}
	PropertyPriceRegister_InconsistentAddress_dict = {}
	PropertyPriceRegister_GeocodePrecision_dict = {}
	PropertyPriceRegister_FixedAddress_dict = {}
	PropertyPriceRegister_DeclaredCounty_dict = {}
	PropertyPriceRegister_PresentPrice_dict = {}
	PppMatchDaftProperty_Area_dict = {}
	PppMatchDaftProperty_Region_dict = {}
	PppMatchDaftProperty_Price_dict = {}
	PppMatchDaftProperty_MarketType_dict = {}
	PppMatchDaftProperty_Beds_dict = {}
	PppMatchDaftProperty_Baths_dict = {}
	PppMatchDaftProperty_Description_dict = {}
	PppMatchDaftProperty_DateEntered_dict = {}
	PppMatchDaftProperty_LastUpdate_dict = {}
	PppMatchDaftProperty_Latitude_dict = {}
	PppMatchDaftProperty_Longitude_dict = {}
	PppMatchDaftProperty_Ber_dict = {}
	PppMatchDaftProperty_RawAddress_dict = {}
	PppMatchDaftProperty_PostalCode_dict = {}
	PppMatchDaftProperty_SqrMetres_dict = {}
	PppMatchDaftProperty_SaleAgreed_dict = {}
	PppMatchDaftProperty_SaleAgreedDate_dict = {}

	nbNone = []

	i = 0

	sizeBiggestNumOfPriceHistory = 0

	for row in rows:
		temp = 0
		
		for e in row:
			if e is None: 
				temp += 1

		if temp > 0:
			nbHaveNone += 1

		nbNone.append(temp)


		PropertyPriceRegister_Id, PropertyPriceRegister_SaleDate, PropertyPriceRegister_Price, PropertyPriceRegister_PostalCode, PropertyPriceRegister_NotFullMarketPrice, PropertyPriceRegister_PropertyDescription, PropertyPriceRegister_County, PropertyPriceRegister_PropertySizeDescription, PropertyPriceRegister_Area, PropertyPriceRegister_Region, PropertyPriceRegister_Latitude, PropertyPriceRegister_Longitude, PropertyPriceRegister_Neighborhood, PropertyPriceRegister_InconsistentAddress, PropertyPriceRegister_GeocodePrecision, PropertyPriceRegister_FixedAddress, PropertyPriceRegister_DeclaredCounty, PropertyPriceRegister_PresentPrice, PppMatchDaftProperty_PppId, PppMatchDaftProperty_DaftPerfectMatchId, PppMatchDaftProperty_Id, PppMatchDaftProperty_Area, PppMatchDaftProperty_Region, PppMatchDaftProperty_Price, PppMatchDaftProperty_MarketType, PppMatchDaftProperty_Beds, PppMatchDaftProperty_Baths, PppMatchDaftProperty_Description, PppMatchDaftProperty_DateEntered, PppMatchDaftProperty_LastUpdate, PppMatchDaftProperty_Latitude, PppMatchDaftProperty_Longitude, PppMatchDaftProperty_Ber, PppMatchDaftProperty_RawAddress, PppMatchDaftProperty_PostalCode, PppMatchDaftProperty_SqrMetres, PppMatchDaftProperty_SaleAgreed, PppMatchDaftProperty_SaleAgreedDate = row


		if PropertyPriceRegister_Id == None :
			PropertyPriceRegister_Id_nbNone += 1
			if PropertyPriceRegister_Id in PropertyPriceRegister_Id_list:
				print("PropertyPriceRegister_Id (" + str(PropertyPriceRegister_Id) + ") is already in list.")
			else:
				PropertyPriceRegister_Id_list.append(PropertyPriceRegister_Id)

		if PppMatchDaftProperty_PppId == None :
			PppMatchDaftProperty_PppId_nbNone += 1 
			if PppMatchDaftProperty_PppId in PppMatchDaftProperty_PppId_list:
				print("PppMatchDaftProperty_PppId (" + str(PppMatchDaftProperty_PppId) + ") is already in list.")
			else:
				PppMatchDaftProperty_PppId_list.append(PppMatchDaftProperty_PppId)

		if PppMatchDaftProperty_DaftPerfectMatchId == None :
			PppMatchDaftProperty_DaftPerfectMatchId_nbNone += 1 
			if PppMatchDaftProperty_DaftPerfectMatchId in PppMatchDaftProperty_DaftPerfectMatchId_list:
				print("PppMatchDaftProperty_DaftPerfectMatchId (" + str(PppMatchDaftProperty_DaftPerfectMatchId) + ") is already in list.")
			else:
				PppMatchDaftProperty_DaftPerfectMatchId_list.append(PppMatchDaftProperty_DaftPerfectMatchId)

		if PppMatchDaftProperty_Id == None :
			PppMatchDaftProperty_Id_nbNone += 1 
			if PppMatchDaftProperty_Id in PppMatchDaftProperty_Id_list:
				print("PppMatchDaftProperty_Id (" + str(PppMatchDaftProperty_Id) + ") is already in list.")
			else:
				PppMatchDaftProperty_Id_list.append(PppMatchDaftProperty_Id)



				
		if PropertyPriceRegister_SaleDate == None :
			PropertyPriceRegister_SaleDate_nbNone += 1 
			if PropertyPriceRegister_SaleDate in PropertyPriceRegister_SaleDate_dict:
				PropertyPriceRegister_SaleDate_dict[PropertyPriceRegister_SaleDate] += 1
			else:
				PropertyPriceRegister_SaleDate_dict[PropertyPriceRegister_SaleDate] = 1
				
		if PropertyPriceRegister_Price == None :
			PropertyPriceRegister_Price_nbNone += 1 
			if PropertyPriceRegister_Price in PropertyPriceRegister_Price_dict:
				PropertyPriceRegister_Price_dict[PropertyPriceRegister_Price] += 1
			else:
				PropertyPriceRegister_Price_dict[PropertyPriceRegister_Price] = 1
				
		if PropertyPriceRegister_PostalCode == None :
			PropertyPriceRegister_PostalCode_nbNone += 1 
			if PropertyPriceRegister_PostalCode in PropertyPriceRegister_PostalCode_dict:
				PropertyPriceRegister_PostalCode_dict[PropertyPriceRegister_PostalCode] += 1
			else:
				PropertyPriceRegister_PostalCode_dict[PropertyPriceRegister_PostalCode] = 1
				
		if PropertyPriceRegister_NotFullMarketPrice == None :
			PropertyPriceRegister_NotFullMarketPrice_nbNone += 1 
			if PropertyPriceRegister_NotFullMarketPrice in PropertyPriceRegister_NotFullMarketPrice_dict:
				PropertyPriceRegister_NotFullMarketPrice_dict[PropertyPriceRegister_NotFullMarketPrice] += 1
			else:
				PropertyPriceRegister_NotFullMarketPrice_dict[PropertyPriceRegister_NotFullMarketPrice] = 1
				
		if PropertyPriceRegister_PropertyDescription == None :
			PropertyPriceRegister_PropertyDescription_nbNone += 1 
			if PropertyPriceRegister_PropertyDescription in PropertyPriceRegister_PropertyDescription_dict:
				PropertyPriceRegister_PropertyDescription_dict[PropertyPriceRegister_PropertyDescription] += 1
			else:
				PropertyPriceRegister_PropertyDescription_dict[PropertyPriceRegister_PropertyDescription] = 1
				
		if PropertyPriceRegister_County == None :
			PropertyPriceRegister_County_nbNone += 1 
			if PropertyPriceRegister_County in PropertyPriceRegister_County_dict:
				PropertyPriceRegister_County_dict[PropertyPriceRegister_County] += 1
			else:
				PropertyPriceRegister_County_dict[PropertyPriceRegister_County] = 1
				
		if PropertyPriceRegister_PropertySizeDescription == None :
			PropertyPriceRegister_PropertySizeDescription_nbNone += 1 
			if PropertyPriceRegister_PropertySizeDescription in PropertyPriceRegister_PropertySizeDescription_dict:
				PropertyPriceRegister_PropertySizeDescription_dict[PropertyPriceRegister_PropertySizeDescription] += 1
			else:
				PropertyPriceRegister_PropertySizeDescription_dict[PropertyPriceRegister_PropertySizeDescription] = 1
				
		if PropertyPriceRegister_Area == None :
			PropertyPriceRegister_Area_nbNone += 1 
			if PropertyPriceRegister_Area in PropertyPriceRegister_Area_dict:
				PropertyPriceRegister_Area_dict[PropertyPriceRegister_Area] += 1
			else:
				PropertyPriceRegister_Area_dict[PropertyPriceRegister_Area] = 1
				
		if PropertyPriceRegister_Region == None :
			PropertyPriceRegister_Region_nbNone += 1 
			if PropertyPriceRegister_Region in PropertyPriceRegister_Region_dict:
				PropertyPriceRegister_Region_dict[PropertyPriceRegister_Region] += 1
			else:
				PropertyPriceRegister_Region_dict[PropertyPriceRegister_Region] = 1
				
		if PropertyPriceRegister_Latitude == None :
			PropertyPriceRegister_Latitude_nbNone += 1 
			if PropertyPriceRegister_Latitude in PropertyPriceRegister_Latitude_dict:
				PropertyPriceRegister_Latitude_dict[PropertyPriceRegister_Latitude] += 1
			else:
				PropertyPriceRegister_Latitude_dict[PropertyPriceRegister_Latitude] = 1
				
		if PropertyPriceRegister_Longitude == None :
			PropertyPriceRegister_Longitude_nbNone += 1 
			if PropertyPriceRegister_Longitude in PropertyPriceRegister_Longitude_dict:
				PropertyPriceRegister_Longitude_dict[PropertyPriceRegister_Longitude] += 1
			else:
				PropertyPriceRegister_Longitude_dict[PropertyPriceRegister_Longitude] = 1
				
		if PropertyPriceRegister_Neighborhood == None :
			PropertyPriceRegister_Neighborhood_nbNone += 1 
			if PropertyPriceRegister_Neighborhood in PropertyPriceRegister_Neighborhood_dict:
				PropertyPriceRegister_Neighborhood_dict[PropertyPriceRegister_Neighborhood] += 1
			else:
				PropertyPriceRegister_Neighborhood_dict[PropertyPriceRegister_Neighborhood] = 1
				
		if PropertyPriceRegister_InconsistentAddress == None :
			PropertyPriceRegister_InconsistentAddress_nbNone += 1 
			if PropertyPriceRegister_InconsistentAddress in PropertyPriceRegister_InconsistentAddress_dict:
				PropertyPriceRegister_InconsistentAddress_dict[PropertyPriceRegister_InconsistentAddress] += 1
			else:
				PropertyPriceRegister_InconsistentAddress_dict[PropertyPriceRegister_InconsistentAddress] = 1
				
		if PropertyPriceRegister_GeocodePrecision == None :
			PropertyPriceRegister_GeocodePrecision_nbNone += 1 
			if PropertyPriceRegister_GeocodePrecision in PropertyPriceRegister_GeocodePrecision_dict:
				PropertyPriceRegister_GeocodePrecision_dict[PropertyPriceRegister_GeocodePrecision] += 1
			else:
				PropertyPriceRegister_GeocodePrecision_dict[PropertyPriceRegister_GeocodePrecision] = 1
				
		if PropertyPriceRegister_FixedAddress == None :
			PropertyPriceRegister_FixedAddress_nbNone += 1 
			if PropertyPriceRegister_FixedAddress in PropertyPriceRegister_FixedAddress_dict:
				PropertyPriceRegister_FixedAddress_dict[PropertyPriceRegister_FixedAddress] += 1
			else:
				PropertyPriceRegister_FixedAddress_dict[PropertyPriceRegister_FixedAddress] = 1
				
		if PropertyPriceRegister_DeclaredCounty == None :
			PropertyPriceRegister_DeclaredCounty_nbNone += 1 
			if PropertyPriceRegister_DeclaredCounty in PropertyPriceRegister_DeclaredCounty_dict:
				PropertyPriceRegister_DeclaredCounty_dict[PropertyPriceRegister_DeclaredCounty] += 1
			else:
				PropertyPriceRegister_DeclaredCounty_dict[PropertyPriceRegister_DeclaredCounty] = 1
				
		if PropertyPriceRegister_PresentPrice == None :
			PropertyPriceRegister_PresentPrice_nbNone += 1 
			if PropertyPriceRegister_PresentPrice in PropertyPriceRegister_PresentPrice_dict:
				PropertyPriceRegister_PresentPrice_dict[PropertyPriceRegister_PresentPrice] += 1
			else:
				PropertyPriceRegister_PresentPrice_dict[PropertyPriceRegister_PresentPrice] = 1
				
		if PppMatchDaftProperty_Area == None :
			PppMatchDaftProperty_Area_nbNone += 1 
			if PppMatchDaftProperty_Area in PppMatchDaftProperty_Area_dict:
				PppMatchDaftProperty_Area_dict[PppMatchDaftProperty_Area] += 1
			else:
				PppMatchDaftProperty_Area_dict[PppMatchDaftProperty_Area] = 1
				
		if PppMatchDaftProperty_Region == None :
			PppMatchDaftProperty_Region_nbNone += 1 
			if PppMatchDaftProperty_Region in PppMatchDaftProperty_Region_dict:
				PppMatchDaftProperty_Region_dict[PppMatchDaftProperty_Region] += 1
			else:
				PppMatchDaftProperty_Region_dict[PppMatchDaftProperty_Region] = 1
				
		if PppMatchDaftProperty_Price == None :
			PppMatchDaftProperty_Price_nbNone += 1 
			if PppMatchDaftProperty_Price in PppMatchDaftProperty_Price_dict:
				PppMatchDaftProperty_Price_dict[PppMatchDaftProperty_Price] += 1
			else:
				PppMatchDaftProperty_Price_dict[PppMatchDaftProperty_Price] = 1
				
		if PppMatchDaftProperty_MarketType == None :
			PppMatchDaftProperty_MarketType_nbNone += 1 
			if PppMatchDaftProperty_MarketType in PppMatchDaftProperty_MarketType_dict:
				PppMatchDaftProperty_MarketType_dict[PppMatchDaftProperty_MarketType] += 1
			else:
				PppMatchDaftProperty_MarketType_dict[PppMatchDaftProperty_MarketType] = 1
				
		if PppMatchDaftProperty_Beds == None :
			PppMatchDaftProperty_Beds_nbNone += 1 
			if PppMatchDaftProperty_Beds in PppMatchDaftProperty_Beds_dict:
				PppMatchDaftProperty_Beds_dict[PppMatchDaftProperty_Beds] += 1
			else:
				PppMatchDaftProperty_Beds_dict[PppMatchDaftProperty_Beds] = 1
				
		if PppMatchDaftProperty_Baths == None :
			PppMatchDaftProperty_Baths_nbNone += 1 
			if PppMatchDaftProperty_Baths in PppMatchDaftProperty_Baths_dict:
				PppMatchDaftProperty_Baths_dict[PppMatchDaftProperty_Baths] += 1
			else:
				PppMatchDaftProperty_Baths_dict[PppMatchDaftProperty_Baths] = 1
				
		if PppMatchDaftProperty_Description == None :
			PppMatchDaftProperty_Description_nbNone += 1 
			if PppMatchDaftProperty_Description in PppMatchDaftProperty_Description_dict:
				PppMatchDaftProperty_Description_dict[PppMatchDaftProperty_Description] += 1
			else:
				PppMatchDaftProperty_Description_dict[PppMatchDaftProperty_Description] = 1
				
		if PppMatchDaftProperty_DateEntered == None :
			PppMatchDaftProperty_DateEntered_nbNone += 1 
			if PppMatchDaftProperty_DateEntered in PppMatchDaftProperty_DateEntered_dict:
				PppMatchDaftProperty_DateEntered_dict[PppMatchDaftProperty_DateEntered] += 1
			else:
				PppMatchDaftProperty_DateEntered_dict[PppMatchDaftProperty_DateEntered] = 1
				
		if PppMatchDaftProperty_LastUpdate == None :
			PppMatchDaftProperty_LastUpdate_nbNone += 1 
			if PppMatchDaftProperty_LastUpdate in PppMatchDaftProperty_LastUpdate_dict:
				PppMatchDaftProperty_LastUpdate_dict[PppMatchDaftProperty_LastUpdate] += 1
			else:
				PppMatchDaftProperty_LastUpdate_dict[PppMatchDaftProperty_LastUpdate] = 1
				
		if PppMatchDaftProperty_Latitude == None :
			PppMatchDaftProperty_Latitude_nbNone += 1 
			if PppMatchDaftProperty_Latitude in PppMatchDaftProperty_Latitude_dict:
				PppMatchDaftProperty_Latitude_dict[PppMatchDaftProperty_Latitude] += 1
			else:
				PppMatchDaftProperty_Latitude_dict[PppMatchDaftProperty_Latitude] = 1
				
		if PppMatchDaftProperty_Longitude == None :
			PppMatchDaftProperty_Longitude_nbNone += 1 
			if PppMatchDaftProperty_Longitude in PppMatchDaftProperty_Longitude_dict:
				PppMatchDaftProperty_Longitude_dict[PppMatchDaftProperty_Longitude] += 1
			else:
				PppMatchDaftProperty_Longitude_dict[PppMatchDaftProperty_Longitude] = 1
				
		if PppMatchDaftProperty_Ber == None :
			PppMatchDaftProperty_Ber_nbNone += 1 
			if PppMatchDaftProperty_Ber in PppMatchDaftProperty_Ber_dict:
				PppMatchDaftProperty_Ber_dict[PppMatchDaftProperty_Ber] += 1
			else:
				PppMatchDaftProperty_Ber_dict[PppMatchDaftProperty_Ber] = 1
				
		if PppMatchDaftProperty_RawAddress == None :
			PppMatchDaftProperty_RawAddress_nbNone += 1 
			if PppMatchDaftProperty_RawAddress in PppMatchDaftProperty_RawAddress_dict:
				PppMatchDaftProperty_RawAddress_dict[PppMatchDaftProperty_RawAddress] += 1
			else:
				PppMatchDaftProperty_RawAddress_dict[PppMatchDaftProperty_RawAddress] = 1
				
		if PppMatchDaftProperty_PostalCode == None :
			PppMatchDaftProperty_PostalCode_nbNone += 1 
			if PppMatchDaftProperty_PostalCode in PppMatchDaftProperty_PostalCode_dict:
				PppMatchDaftProperty_PostalCode_dict[PppMatchDaftProperty_PostalCode] += 1
			else:
				PppMatchDaftProperty_PostalCode_dict[PppMatchDaftProperty_PostalCode] = 1
				
		if PppMatchDaftProperty_SqrMetres == None :
			PppMatchDaftProperty_SqrMetres_nbNone += 1 
			if PppMatchDaftProperty_SqrMetres in PppMatchDaftProperty_SqrMetres_dict:
				PppMatchDaftProperty_SqrMetres_dict[PppMatchDaftProperty_SqrMetres] += 1
			else:
				PppMatchDaftProperty_SqrMetres_dict[PppMatchDaftProperty_SqrMetres] = 1
				
		if PppMatchDaftProperty_SaleAgreed == None :
			PppMatchDaftProperty_SaleAgreed_nbNone += 1 
			if PppMatchDaftProperty_SaleAgreed in PppMatchDaftProperty_SaleAgreed_dict:
				PppMatchDaftProperty_SaleAgreed_dict[PppMatchDaftProperty_SaleAgreed] += 1
			else:
				PppMatchDaftProperty_SaleAgreed_dict[PppMatchDaftProperty_SaleAgreed] = 1
				
		if PppMatchDaftProperty_SaleAgreedDate == None :
			PppMatchDaftProperty_SaleAgreedDate_nbNone += 1 
			if PppMatchDaftProperty_SaleAgreedDate in PppMatchDaftProperty_SaleAgreedDate_dict:
				PppMatchDaftProperty_SaleAgreedDate_dict[PppMatchDaftProperty_SaleAgreedDate] += 1
			else:
				PppMatchDaftProperty_SaleAgreedDate_dict[PppMatchDaftProperty_SaleAgreedDate] = 1
		 

		c2 = cnxn.cursor()

		sqlquery = """
			SELECT DaftProperty, Id, Price, Date
			FROM DaftPropertyPriceHistory
			WHERE DaftProperty = ?
			""" #str(PppMatchDaftProperty_DaftPerfectMatchId)

		c2.execute(sqlquery, (str(PppMatchDaftProperty_DaftPerfectMatchId)))

		#c2.execute(sqlquery)
		rows2 = c2.fetchall()

		priceHistory = []
		currentSize = 0
		for row in rows2:
			DaftProperty, Id, Price, Date = row
			priceHistory.append((Id, Price, Date))
			currentSize += 1

		if currentSize > sizeBiggestNumOfPriceHistory:
			sizeBiggestNumOfPriceHistory = currentSize




		Sales_Id 				= PropertyPriceRegister_Id
		Sales_date 				= PropertyPriceRegister_SaleDate
		Sales_price 			= PropertyPriceRegister_Price
		Sales_property_type 	= PppMatchDaftProperty_MarketType
		Sales_surface 			= PppMatchDaftProperty_SqrMetres 
		#PppMatchDaftProperty.SqrMetres


		Sales_longitude 		= PropertyPriceRegister_Longitude
		Sales_latitude 			= PropertyPriceRegister_Latitude
		Sales_postcodes 		= PropertyPriceRegister_PostalCode
		Sales_area 				= PppMatchDaftProperty_Area
		Sales_bathrooms			= PppMatchDaftProperty_Baths
		Sales_beds 				= PppMatchDaftProperty_Beds
		
		Sales_ber_id 			= PppMatchDaftProperty_Ber

		Sales_parking 			= parking(PropertyPriceRegister_PropertyDescription)
		Sales_description 		= PropertyPriceRegister_PropertyDescription
		Sales_central_heating 	= centralHeating(PropertyPriceRegister_PropertyDescription) 
		Sales_alarm				= alarm(PropertyPriceRegister_PropertyDescription)
		Sales_gas_heating 		= gazHeating(PropertyPriceRegister_PropertyDescription)
		Sales_oil_heating 		= oilHeating(PropertyPriceRegister_PropertyDescription)
		attic_conversion 		= attic(PropertyPriceRegister_PropertyDescription)
		ensuites 				= ensuite(PropertyPriceRegister_PropertyDescription)


		countNone = 0

		if Sales_Id is None:
			countNone += 1
			Sales_Id_countNone += 1

		if Sales_date is None:
			countNone += 1
			Sales_date_countNone += 1

		if Sales_price is None:
			countNone += 1
			Sales_price_countNone += 1

		if Sales_property_type is None:
			countNone += 1
			Sales_property_type_countNone += 1

		if Sales_surface is None:
			countNone += 1
			Sales_surface_countNone += 1

		if Sales_longitude is None:
			countNone += 1
			Sales_longitude_countNone += 1

		if Sales_latitude is None:
			countNone += 1
			Sales_latitude_countNone += 1

		if Sales_postcodes is None:
			countNone += 1
			Sales_postcodes_countNone += 1

		if Sales_area is None:
			countNone += 1
			Sales_area_countNone += 1

		if Sales_bathrooms is None:
			countNone += 1
			Sales_bathrooms_countNone += 1

		if Sales_beds is None:
			countNone += 1
			Sales_beds_countNone += 1

		if Sales_ber_id is None:
			countNone += 1
			Sales_ber_id_countNone += 1

		if Sales_parking is None:
			countNone += 1
			Sales_parking_countNone += 1

		if Sales_description is None:
			countNone += 1
			Sales_description_countNone += 1

		if Sales_central_heating is None:
			countNone += 1
			Sales_central_heating_countNone += 1

		if Sales_alarm is None:
			countNone += 1
			Sales_alarm_countNone += 1

		if Sales_gas_heating is None:
			countNone += 1
			Sales_gas_heating_countNone += 1

		if Sales_oil_heating is None:
			countNone += 1
			Sales_oil_heating_countNone += 1

		if attic_conversion is None:
			countNone += 1
			attic_conversion_countNone += 1

		if ensuites is None:
			countNone += 1
			ensuites_countNone += 1


		countNone_list.append(countNone)

		entry = (Sales_Id, Sales_date, Sales_price, Sales_property_type, Sales_surface, Sales_longitude, Sales_latitude, Sales_postcodes, Sales_area, Sales_bathrooms, Sales_beds, Sales_ber_id, Sales_parking, Sales_description, Sales_central_heating, Sales_alarm, Sales_gas_heating, Sales_oil_heating, attic_conversion, ensuites, priceHistory)

		result1.append(entry)

		i += 1

	'''
	priceHistory = {}
	sizeBiggest = 0

	for daftid in PppMatchDaftProperty_DaftPerfectMatchId:
		priceHistory[daftid] = []

		sqlquery = """
			SELECT *
			FROM daftPriceHistory
			WHERE id =""" + str(daftid)
			

		c.execute(sqlquery)
		rows = cursor.fetchall()

		currentSize = 0
		for row in rows:
			priceHistory[daftid].append(row)
			currentSize += 1

		if currentSize > sizeBiggest:
			sizeBiggest = currentSize
	'''





	print("nbHaveNone : " + str(nbHaveNone) + "(" + str(nbHaveNone/i * 100) + "%)")

	'''
	print("PropertyPriceRegister_Id_nbNone : " + str(PropertyPriceRegister_Id_nbNone) + "(" + str(PropertyPriceRegister_Id_nbNone/i * 100) + "%)")

	print("PropertyPriceRegister_SaleDate_nbNone : " + str(PropertyPriceRegister_SaleDate_nbNone) + "(" + str(PropertyPriceRegister_SaleDate_nbNone/i * 100) + "%)")

	print("PropertyPriceRegister_Price_nbNone : " + str(PropertyPriceRegister_Price_nbNone) + "(" + str(PropertyPriceRegister_Price_nbNone/i * 100) + "%)")
	'''
	print("PropertyPriceRegister_PostalCode_nbNone : " + str(PropertyPriceRegister_PostalCode_nbNone) + "(" + str(PropertyPriceRegister_PostalCode_nbNone/i * 100) + "%)")

	'''
	print("PropertyPriceRegister_NotFullMarketPrice_nbNone : " + str(PropertyPriceRegister_NotFullMarketPrice_nbNone) + "(" + str(PropertyPriceRegister_NotFullMarketPrice_nbNone/i * 100) + "%)")

	
	print("PropertyPriceRegister_PropertyDescription_nbNone : " + str(PropertyPriceRegister_PropertyDescription_nbNone) + "(" + str(PropertyPriceRegister_PropertyDescription_nbNone/i * 100) + "%)")

	print("PropertyPriceRegister_County_nbNone : " + str(PropertyPriceRegister_County_nbNone) + "(" + str(PropertyPriceRegister_County_nbNone/i * 100) + "%)")
	'''

	print("PropertyPriceRegister_PropertySizeDescription_nbNone : " + str(PropertyPriceRegister_PropertySizeDescription_nbNone) + "(" + str(PropertyPriceRegister_PropertySizeDescription_nbNone/i * 100) + "%)")

	'''
	print("PropertyPriceRegister_Area_nbNone : " + str(PropertyPriceRegister_Area_nbNone) + "(" + str(PropertyPriceRegister_Area_nbNone/i * 100) + "%)")

	print("PropertyPriceRegister_Region_nbNone : " + str(PropertyPriceRegister_Region_nbNone) + "(" + str(PropertyPriceRegister_Region_nbNone/i * 100) + "%)")

	print("PropertyPriceRegister_Latitude_nbNone : " + str(PropertyPriceRegister_Latitude_nbNone) + "(" + str(PropertyPriceRegister_Latitude_nbNone/i * 100) + "%)")

	print("PropertyPriceRegister_Longitude_nbNone : " + str(PropertyPriceRegister_Longitude_nbNone) + "(" + str(PropertyPriceRegister_Longitude_nbNone/i * 100) + "%)")
	'''

	print("PropertyPriceRegister_Neighborhood_nbNone : " + str(PropertyPriceRegister_Neighborhood_nbNone) + "(" + str(PropertyPriceRegister_Neighborhood_nbNone/i * 100) + "%)")

	'''
	print("PropertyPriceRegister_InconsistentAddress_nbNone : " + str(PropertyPriceRegister_InconsistentAddress_nbNone) + "(" + str(PropertyPriceRegister_InconsistentAddress_nbNone/i * 100) + "%)")
	'''

	print("PropertyPriceRegister_GeocodePrecision_nbNone : " + str(PropertyPriceRegister_GeocodePrecision_nbNone) + "(" + str(PropertyPriceRegister_GeocodePrecision_nbNone/i * 100) + "%)")

	'''
	print("PropertyPriceRegister_FixedAddress_nbNone : " + str(PropertyPriceRegister_FixedAddress_nbNone) + "(" + str(PropertyPriceRegister_FixedAddress_nbNone/i * 100) + "%)")
	'''

	print("PropertyPriceRegister_DeclaredCounty_nbNone : " + str(PropertyPriceRegister_DeclaredCounty_nbNone) + "(" + str(PropertyPriceRegister_DeclaredCounty_nbNone/i * 100) + "%)")

	print("PropertyPriceRegister_PresentPrice_nbNone : " + str(PropertyPriceRegister_PresentPrice_nbNone) + "(" + str(PropertyPriceRegister_PresentPrice_nbNone/i * 100) + "%)")

	'''
	print("PppMatchDaftProperty_PppId_nbNone : " + str(PppMatchDaftProperty_PppId_nbNone) + "(" + str(PppMatchDaftProperty_PppId_nbNone/i * 100) + "%)")

	print("PppMatchDaftProperty_DaftPerfectMatchId_nbNone : " + str(PppMatchDaftProperty_DaftPerfectMatchId_nbNone) + "(" + str(PppMatchDaftProperty_DaftPerfectMatchId_nbNone/i * 100) + "%)")

	print("PppMatchDaftProperty_Id_nbNone : " + str(PppMatchDaftProperty_Id_nbNone) + "(" + str(PppMatchDaftProperty_Id_nbNone/i * 100) + "%)")

	print("PppMatchDaftProperty_Area_nbNone : " + str(PppMatchDaftProperty_Area_nbNone) + "(" + str(PppMatchDaftProperty_Area_nbNone/i * 100) + "%)")

	print("PppMatchDaftProperty_Region_nbNone : " + str(PppMatchDaftProperty_Region_nbNone) + "(" + str(PppMatchDaftProperty_Region_nbNone/i * 100) + "%)")
	'''

	print("PppMatchDaftProperty_Price_nbNone : " + str(PppMatchDaftProperty_Price_nbNone) + "(" + str(PppMatchDaftProperty_Price_nbNone/i * 100) + "%)")

	'''
	print("PppMatchDaftProperty_MarketType_nbNone : " + str(PppMatchDaftProperty_MarketType_nbNone) + "(" + str(PppMatchDaftProperty_MarketType_nbNone/i * 100) + "%)")
	'''

	print("PppMatchDaftProperty_Beds_nbNone : " + str(PppMatchDaftProperty_Beds_nbNone) + "(" + str(PppMatchDaftProperty_Beds_nbNone/i * 100) + "%)")

	print("PppMatchDaftProperty_Baths_nbNone : " + str(PppMatchDaftProperty_Baths_nbNone) + "(" + str(PppMatchDaftProperty_Baths_nbNone/i * 100) + "%)")

	'''
	print("PppMatchDaftProperty_Description_nbNone : " + str(PppMatchDaftProperty_Description_nbNone) + "(" + str(PppMatchDaftProperty_Description_nbNone/i * 100) + "%)")

	print("PppMatchDaftProperty_DateEntered_nbNone : " + str(PppMatchDaftProperty_DateEntered_nbNone) + "(" + str(PppMatchDaftProperty_DateEntered_nbNone/i * 100) + "%)")

	print("PppMatchDaftProperty_LastUpdate_nbNone : " + str(PppMatchDaftProperty_LastUpdate_nbNone) + "(" + str(PppMatchDaftProperty_LastUpdate_nbNone/i * 100) + "%)")

	print("PppMatchDaftProperty_Latitude_nbNone : " + str(PppMatchDaftProperty_Latitude_nbNone) + "(" + str(PppMatchDaftProperty_Latitude_nbNone/i * 100) + "%)")

	print("PppMatchDaftProperty_Longitude_nbNone : " + str(PppMatchDaftProperty_Longitude_nbNone) + "(" + str(PppMatchDaftProperty_Longitude_nbNone/i * 100) + "%)")
	'''

	print("PppMatchDaftProperty_Ber_nbNone : " + str(PppMatchDaftProperty_Ber_nbNone) + "(" + str(PppMatchDaftProperty_Ber_nbNone/i * 100) + "%)")

	'''
	print("PppMatchDaftProperty_RawAddress_nbNone : " + str(PppMatchDaftProperty_RawAddress_nbNone) + "(" + str(PppMatchDaftProperty_RawAddress_nbNone/i * 100) + "%)")
	'''

	print("PppMatchDaftProperty_PostalCode_nbNone : " + str(PppMatchDaftProperty_PostalCode_nbNone) + "(" + str(PppMatchDaftProperty_PostalCode_nbNone/i * 100) + "%)")

	print("PppMatchDaftProperty_SqrMetres_nbNone : " + str(PppMatchDaftProperty_SqrMetres_nbNone) + "(" + str(PppMatchDaftProperty_SqrMetres_nbNone/i * 100) + "%)")

	'''
	print("PppMatchDaftProperty_SaleAgreed_nbNone : " + str(PppMatchDaftProperty_SaleAgreed_nbNone) + "(" + str(PppMatchDaftProperty_SaleAgreed_nbNone/i * 100) + "%)")

	print("PppMatchDaftProperty_SaleAgreedDate_nbNone : " + str(PppMatchDaftProperty_SaleAgreedDate_nbNone) + "(" + str(PppMatchDaftProperty_SaleAgreedDate_nbNone/i * 100) + "%)")
	'''

	print("\n")
	display.display(pd.Series(nbNone).describe())

	

	print("Sales_Id_countNone : " + str(Sales_Id_countNone) + "(" + str(Sales_Id_countNone/i * 100) + "%)")
	print("Sales_date_countNone : " + str(Sales_date_countNone) + "(" + str(Sales_date_countNone/i * 100) + "%)")
	print("Sales_price_countNone : " + str(Sales_price_countNone) + "(" + str(Sales_price_countNone/i * 100) + "%)")
	print("Sales_property_type_countNone : " + str(Sales_property_type_countNone) + "(" + str(Sales_property_type_countNone/i * 100) + "%)")
	print("Sales_surface_countNone : " + str(Sales_surface_countNone) + "(" + str(Sales_surface_countNone/i * 100) + "%)")
	print("Sales_longitude_countNone : " + str(Sales_longitude_countNone) + "(" + str(Sales_longitude_countNone/i * 100) + "%)")
	print("Sales_latitude_countNone : " + str(Sales_latitude_countNone) + "(" + str(Sales_latitude_countNone/i * 100) + "%)")
	print("Sales_postcodes_countNone : " + str(Sales_postcodes_countNone) + "(" + str(Sales_postcodes_countNone/i * 100) + "%)")
	print("Sales_area_countNone : " + str(Sales_area_countNone) + "(" + str(Sales_area_countNone/i * 100) + "%)")
	print("Sales_bathrooms_countNone : " + str(Sales_bathrooms_countNone) + "(" + str(Sales_bathrooms_countNone/i * 100) + "%)")
	print("Sales_beds_countNone : " + str(Sales_beds_countNone) + "(" + str(Sales_beds_countNone/i * 100) + "%)")
	print("Sales_ber_id_countNone : " + str(Sales_ber_id_countNone) + "(" + str(Sales_ber_id_countNone/i * 100) + "%)")
	print("Sales_parking_countNone : " + str(Sales_parking_countNone) + "(" + str(Sales_parking_countNone/i * 100) + "%)")
	print("Sales_description_countNone : " + str(Sales_description_countNone) + "(" + str(Sales_description_countNone/i * 100) + "%)")
	print("Sales_central_heating_countNone : " + str(Sales_central_heating_countNone) + "(" + str(Sales_central_heating_countNone/i * 100) + "%)")
	print("Sales_alarm_countNone : " + str(Sales_alarm_countNone) + "(" + str(Sales_alarm_countNone/i * 100) + "%)")
	print("Sales_gas_heating_countNone : " + str(Sales_gas_heating_countNone) + "(" + str(Sales_gas_heating_countNone/i * 100) + "%)")
	print("Sales_oil_heating_countNone : " + str(Sales_oil_heating_countNone) + "(" + str(Sales_oil_heating_countNone/i * 100) + "%)")
	print("attic_conversion_countNone : " + str(attic_conversion_countNone) + "(" + str(attic_conversion_countNone/i * 100) + "%)")
	print("ensuites_countNone : " + str(ensuites_countNone) + "(" + str(ensuites_countNone/i * 100) + "%)")
	display.display(pd.Series(countNone_list).describe())


	#write the outputfile
	with open("result1.csv", "w+") as filepointer:

		firstLine = "Sales.Id;Sales.date;Sales.price;Sales.property_type;Sales.surface;Sales.longitude;Sales.latitude;Sales.postcodes;Sales.area;Sales.bathrooms;Sales.beds;Sales.ber_id;Sales.parking;Sales.description;Sales.central_heating;Sales.alarm;Sales.gas_heating;Sales.oil_heating;attic.conversion;ensuites"

		for j in range(sizeBiggestNumOfPriceHistory*2):
			firstLine += ";PriceHistory.date" + str(j) + ";PriceHistory.price" + str(j)

		filepointer.write(firstLine + "\n")
		for line in result1:

			Sales_Id, Sales_date, Sales_price, Sales_property_type, Sales_surface, Sales_longitude, Sales_latitude, Sales_postcodes, Sales_area, Sales_bathrooms, Sales_beds, Sales_ber_id, Sales_parking, Sales_description, Sales_central_heating, Sales_alarm, Sales_gas_heating, Sales_oil_heating, attic_conversion, ensuites, priceHistory = line


			currentLine = str(Sales_Id) + ";\"" + str(Sales_date) + ";\"" + str(Sales_price) + ";\"" + str(Sales_property_type) + ";\""+ str(Sales_surface) + ";\""+ str(Sales_longitude)+ ";\""+ str(Sales_latitude)+ ";\""+ str(Sales_postcodes)+ ";\""+ str(Sales_area)+ ";\""+ str(Sales_bathrooms) + ";\""+ str(Sales_beds) + ";\""+ str(Sales_ber_id) + ";\""+ str(Sales_parking) + ";\""+ str(Sales_description) + ";\""+ str(Sales_central_heating) + ";\""+ str(Sales_alarm) + ";\""+ str(Sales_gas_heating) + ";\""+ str(Sales_oil_heating) + ";\""+ str(attic_conversion) + ";\""+ str(ensuites) + "\""

			for j in range(len(priceHistory)):
				currentLine += ";" + str(priceHistory[j][1]) + ";" + str(priceHistory[j][2])

			for j in range(sizeBiggestNumOfPriceHistory*2 - len(priceHistory)):
				currentLine += ";;"

			filepointer.write(currentLine + "\n")



	result2 = []
	for l in result1:
		hasNone = False
		for e in l:
			if e is None:
				hasNone = True
				break;

		if not hasNone:
			result2.append(l)

	with open("result2.csv", "w+") as filepointer:

		firstLine = "Sales.Id;Sales.date;Sales.price;Sales.property_type;Sales.surface;Sales.longitude;Sales.latitude;Sales.postcodes;Sales.area;Sales.bathrooms;Sales.beds;Sales.ber_id;Sales.parking;Sales.description;Sales.central_heating;Sales.alarm;Sales.gas_heating;Sales.oil_heating;attic.conversion;ensuites"

		for j in range(sizeBiggestNumOfPriceHistory*2):
			firstLine += ";PriceHistory.date" + str(j) + ";PriceHistory.price" + str(j)

		filepointer.write(firstLine + "\n")
		for line in result2:

			Sales_Id, Sales_date, Sales_price, Sales_property_type, Sales_surface, Sales_longitude, Sales_latitude, Sales_postcodes, Sales_area, Sales_bathrooms, Sales_beds, Sales_ber_id, Sales_parking, Sales_description, Sales_central_heating, Sales_alarm, Sales_gas_heating, Sales_oil_heating, attic_conversion, ensuites, priceHistory = line


			currentLine = str(Sales_Id) + ";\"" + str(Sales_date) + ";\"" + str(Sales_price) + ";\"" + str(Sales_property_type) + ";\""+ str(Sales_surface) + ";\""+ str(Sales_longitude)+ ";\""+ str(Sales_latitude)+ ";\""+ str(Sales_postcodes)+ ";\""+ str(Sales_area)+ ";\""+ str(Sales_bathrooms) + ";\""+ str(Sales_beds) + ";\""+ str(Sales_ber_id) + ";\""+ str(Sales_parking) + ";\""+ str(Sales_description) + ";\""+ str(Sales_central_heating) + ";\""+ str(Sales_alarm) + ";\""+ str(Sales_gas_heating) + ";\""+ str(Sales_oil_heating) + ";\""+ str(attic_conversion) + ";\""+ str(ensuites) + "\""

			for j in range(len(priceHistory)):
				currentLine += ";" + str(priceHistory[j][1]) + ";" + str(priceHistory[j][2])

			for j in range(sizeBiggestNumOfPriceHistory*2 - len(priceHistory)):
				currentLine += ";;"

			filepointer.write(currentLine + "\n")

	#write any id used to not get them again

	print(str(len(result1)))
	print(str(len(result2)))
		


def countMatches(cnxn):

	c = cnxn.cursor()

	sqlquery = """
		SELECT count(*)
		FROM PppMatch
		"""

	c.execute(sqlquery)
	rows = c.fetchall()

	print(rows)

def checkCountyRS(c):
	sqlquery = """
		SELECT RawAddress, HouseNoStreet, Region, Area, County
		FROM DaftProperty
		WHERE MarketType = 'Residential Sale'
		"""

	c.execute(sqlquery)
	#rows = cursor.fetchall()
	rows = c.fetchone()

	for row in rows:
		for RawAddress, HouseNoStreet, Region, Area, County in row:
			print(str(RawAddress))
			print(str(HouseNoStreet) + ", " + str(Region) + ", " + str(Area) + ", " + str(County))
			print()

def checkCounty(cnxn):
	c = cnxn.cursor()

	sqlquery = """
		SELECT RawAddress, HouseNoStreet, Region, Area, County, Id
		FROM DaftProperty
		"""

	c.execute(sqlquery)
	rows = c.fetchall()
	#row = cursor.fetchone()

	global listCounties
	global listParsedCounties
	global nbCoFound
	global eircodeDescriptor


	total = 0
	nbMismatch = 0
	nbErrorCounty = 0
	nbCountyNull = 0
	#nbUC = 0
	nbCountyNotParsed = 0
	nbParsedInvalidCounty = 0
	nbMultipleCountyError = 0
	nbParsedValidCounty = 0

	tableCountyNull = []
	tableCountyError = []
	tableCountyMismatched = []
	tableCountyNotParsed = []

	dictCounty = {}

	#weirdCharCount = 0 #to count how many '\ufffd' were in raw address
	#dictECRK = {}

	for row in rows:
		total += 1

		RawAddress = row[0].replace("  ", "")
		RawAddress = re.sub('\ufffd', '', RawAddress)

		HouseNoStreet = row[1]
		Region = row[2]
		Area = row[3]
		County = row[4]
		Id = row[5]


		#parsedCounty = ""
		parsedCounty = parseRawAdressToGetCounty(RawAddress)
		'''
		#*****************************************************************************************
		regexERCK = "|".join(eircodeDescriptor.keys()) + "(?!(([a-zA-Z1-9]){1}( ){0,1}([a-zA-Z1-9]){3})|(( ){0,1}([a-zA-Z1-9]){4}))"

		g = re.search(regexERCK, RawAddress)
		if g != None:
			parsedCounty = g.group(0)

			if g.group(0) in eircodeDescriptor:
				#if there is only on county for 
				if len(eircodeDescriptor[g.group(0)][1]) == 1:
					parsedCounty = eircodeDescriptor[g.group(0)][1][0]
				'#''
				else:
					#more than on county
					
					#some debug
					if g.group(0) in dictECRK:
						dictECRK[g.group(0)] += 1
					else:
						dictECRK[g.group(0)] = 1
				'#''
			else:
				print("debug 1")
				print(str(g.group(0)))
				print("\n")

		
		#*****************************************************************************************
		'''
		'''
		#*****************************************************************************************
		g = re.search('\ufffd', RawAddress)
		if g != None:
			RawAddress = re.sub('\ufffd', '', RawAddress)
			print("debug 2")
			print(RawAddress)
			print("\n")
			#weirdCharCount += 1
		#*****************************************************************************************
		'''
		
		if parsedCounty == "":
			nbCountyNotParsed += 1
			tableCountyNotParsed.append((Id, County, HouseNoStreet, Region, Area, RawAddress))
		else:
			if parsedCounty == "InvalidCountyError":
				nbParsedInvalidCounty += 1
			else:
				if parsedCounty == "MultipleCountyError":
					nbMultipleCountyError += 1
				else:
					nbParsedValidCounty += 1

			if parsedCounty == "MultipleCountyError":
				nbMultipleCountyError += 1


		if County is None or County == "":
			nbCountyNull += 1
			tableCountyNull.append((Id, RawAddress))
		else:
			if County not in listCounties:
				nbErrorCounty += 1
				tableCountyError.append((Id, County, RawAddress))
			else:
				#nbUC += 1
				#if County.lower() not in RawAddress.lower()
				if County != parsedCounty and parsedCounty != "" and parsedCounty != "InvalidCountyError" and parsedCounty != "MultipleCountyError":
					nbMismatch += 1
					tableCountyMismatched.append((Id, County, HouseNoStreet, Region, Area, RawAddress, parsedCounty))


	
	print("total : " + str(total))
	#print("nbUC : " + str(nbUC))
	print("nbCountyNull : " + str(nbCountyNull) + " (" + str(100*nbCountyNull/total) +"%)")
	print("nbErrorCounty : " + str(nbErrorCounty) + " (" + str(100*nbErrorCounty/total) +"%)")
	print("nbMismatch : " + str(nbMismatch) + " (" + str(100*nbMismatch/total) +"%)")

	print("nbCoFound : " + str(nbCoFound) + " (" + str(100*nbCoFound/total) +"%)")
	print("nbCountyNotParsed : " + str(nbCountyNotParsed) + " (" + str(100*nbCountyNotParsed/total) +"%)")
	print("nbParsedInvalidCounty : " + str(nbParsedInvalidCounty) + " (" + str(100*nbParsedInvalidCounty/total) +"%)")
	print("nbMultipleCountyError : " + str(nbMultipleCountyError) + " (" + str(100*nbMultipleCountyError/total) +"%)")
	print("nbParsedValidCounty : " + str(nbParsedValidCounty) + " (" + str(100*nbParsedValidCounty/total) +"%)")
	nbMultipleCountyError
	#print("weirdCharCount : " + str(weirdCharCount) + " (" + str(100*weirdCharCount/total) +"%)")

	'''
	print("\neircode")
	for key, value in dictECRK.items():
		print(str(key) + " : " + str(value))
	'''


	listParsedCounties = OrderedDict(sorted(listParsedCounties.items(), key=lambda t: -t[1]))


	with open("tableCountyNotParsed.txt", "w+") as filepointer:
		for line in tableCountyNotParsed:
			filepointer.write(" ID: "+str(line[0]) + "\t; County: "+str(line[1]) + "\t; HouseNoStreet: "+str(line[2]) + "\t; Region: "+str(line[3]) + "\t; Area: "+str(line[4]) + "\t; RawAddress: \""+str(line[5]) + "\"\n")

	with open("tableCountyNotParsed.csv", "w+") as filepointer:
		filepointer.write("ID;County;HouseNoStreet;Region;Area;Raw Address\n")
		for line in tableCountyNotParsed:
			filepointer.write(" ID: "+str(line[0]) + "\t; County: "+str(line[1]) + "\t; HouseNoStreet: "+str(line[2]) + "\t; Region: "+str(line[3]) + "\t; Area: "+str(line[4]) + "\t; RawAddress: \""+str(line[5]) + "\"\n")
	
	with open("listParsedCounties.txt", "w+") as filepointer:
		for key, value in listParsedCounties.items():
			filepointer.write(str(key) + " : " + str(value) + "\n")

	with open("tableCountyNull.txt", "w+") as filepointer:
		for line in tableCountyNull:
			filepointer.write(" ID: "+str(line[0]) + "\t; RawAddress: \""+str(line[1]) + "\"\n")

	with open("tableCountyNull.csv", "w+") as filepointer:
		filepointer.write("ID;Raw Address\n")
		for line in tableCountyNull:
			filepointer.write(str(line[0]) + ";\""+str(line[1]) + "\"\n")

	with open("tableCountyError.txt", "w+") as filepointer:
		for line in tableCountyError:
			filepointer.write(" ID: "+str(line[0]) + "\t; County: "+str(line[1]) + "\t; RawAddress: \""+str(line[2]) + "\"\n")

	with open("tableCountyError.csv", "w+") as filepointer:
		filepointer.write("ID;County;Raw Address\n")
		for line in tableCountyError:
			filepointer.write(str(line[0]) + ";\""+str(line[1]) + "\"" + ";\""+str(line[2]) + "\"\n")

	with open("tableCountyMismatched.txt", "w+") as filepointer:
		for line in tableCountyMismatched:
			filepointer.write(" ID: "+str(line[0]) + "\t; County: "+str(line[1]) + "\t; HouseNoStreet: "+str(line[2]) + "\t; Region: "+str(line[3]) + "\t; Area: "+str(line[4]) + "\t; RawAddress: \""+str(line[5]) + "\"\t; parsedCounty: "+str(line[6]) + ".\n")

	with open("tableCountyMismatched.csv", "w+") as filepointer:
		filepointer.write("ID;County;HouseNoStreet;Region;Area;Raw Address;parsedAddress\n")
		for line in tableCountyMismatched:
			filepointer.write(str(line[0]) + ";\""+str(line[1]) + "\"" + ";\""+str(line[2]) + "\"" + ";\""+str(line[3]) + "\"" + ";\""+str(line[4]) + "\"" + ";\""+str(line[5]) + "\"\t; parsedCounty: "+str(line[6]) + ".\n")
	
#****************************************************************************************************************************



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
	

	#cursor = cnxn.cursor()
	#****************************************************************************************************************************

	#****************************************************************************************************************************
	#initialize some global variables
	#****************************************************************************************************************************
	global listCounties
	global eircodeDescriptor
	global listParsedCounties
	global nbCoFound
	
	listCounties = getCountiesList()
	eircodeDescriptor = getEircodeDescriptor()

	listParsedCounties = {}
	nbCoFound = 0
	#****************************************************************************************************************************


	#****************************************************************************************************************************
	#do the wanted queries
	#****************************************************************************************************************************
	#countMatches(cnxn)

	#checkCountyRS(cnxn)
	
	#checkCounty(cnxn)

	dataMaker(cnxn)
	#****************************************************************************************************************************


	#****************************************************************************************************************************
	#close the connection
	#****************************************************************************************************************************
	cnxn.close()
	#****************************************************************************************************************************

