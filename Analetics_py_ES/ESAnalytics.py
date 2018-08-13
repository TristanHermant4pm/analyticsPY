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
import matplotlib as mpl
from matplotlib import pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import FuncFormatter
#from quantiphy import Quantity
from datetime import date, timedelta


#***********************************************************************************************************************************
#Meta Data
#***********************************************************************************************************************************

ResFolder = "res\\"
ResFolderByDate = "byDate\\"

#***********************************************************************************************************************************

#***********************************************************************************************************************************
#functions
#***********************************************************************************************************************************

def myxticks(x, label, ltd):
	x_res = []
	label_res = []

	size = len(x)
	nbOfLabelToDisplay = ltd

	ntopass = int(size/nbOfLabelToDisplay) if size > nbOfLabelToDisplay else 1

	for i in range(len(x)):
		if i%ntopass == 0:
			x_res.append(x[i])
			label_res.append(label[i])

	return (x_res, label_res)


def autolabel(ax, rects, heightMultiplier = 1.0, xpos='center'):
    """
    Attach a text label above each bar in *rects*, displaying its height.

    *xpos* indicates which side to place the text w.r.t. the center of
    the bar. It can be one of the following {'center', 'right', 'left'}.

    heightMultiplier multiplied by the Height of the bar gives the Y position of the label
    """

    xpos = xpos.lower()  # normalize the case of the parameter
    ha = {'center': 'center', 'right': 'left', 'left': 'right'}
    offset = {'center': 0.5, 'right': 0.57, 'left': 0.43}  # x_txt = x + w*off

    for rect in rects:
        height = rect.get_height()
        ax.text(
        	rect.get_x() + rect.get_width() * offset[xpos],
        	heightMultiplier*height,
            '{}'.format(height), 
            ha=ha[xpos], 
            va='bottom'
            )


"""
all thoses list have the same length
"""
def plotInOne(
	nbHit_list,
	daftCount_list,
	daftdropCount_list, 
	myhomeCount_list, 
	nbPMtotal_list, 
	nbPMdaft_list, 
	nbPMdaftdrop_list, 
	nbPMmyhome_list, 
	timeframe_list,
	displayAlldata
	):

	#fig = plt.figure()

	gs = gridspec.GridSpec(6, 10) if displayAlldata else gridspec.GridSpec(2, 1)

	x = range(0, len(nbHit_list), 1)

	# define the axis formatting routines	
	tf_formatter = FuncFormatter(lambda x, string: '$%1.1fM' % (x*1e-6))
	(trimmedX, trimmedXLabel) = myxticks(x, timeframe_list, 25) # 25 is found manually

	trimmedY = range(0, 100, 10)
	trimmedYLabel = []
	for i in trimmedY:
		trimmedYLabel.append(str(i))

    #*******************************************************************************************************************************
    # GRAPH 1
    #*******************************************************************************************************************************
	axe1 = plt.subplot(gs[0:2, :-3]) if displayAlldata else plt.subplot(gs[0, :])

	axe1.plot(x, nbHit_list, 'k-.', label = "Total properties")

	if displayAlldata:
		axe1.plot(x, daftCount_list, 'c-.', label = "Total properties in Daft")
		axe1.plot(x, daftdropCount_list, 'y-.', label = "Total properties in Daftdrop")
		axe1.plot(x, myhomeCount_list, 'm-.', label = "Total properties in MyHome")

	axe1.plot(x, nbPMdaft_list, 'b--', label = "Daft perfect matches")
	axe1.plot(x, nbPMmyhome_list, 'r--', label = "MyHome perfect matches")
	axe1.plot(x, nbPMdaftdrop_list, 'g--', label = "DaftDrop perfect matches")
	axe1.plot(x, nbPMtotal_list, 'k--', label = "Total perfect matches")

	lines, labels = axe1.get_legend_handles_labels()
	axe1.legend(lines, labels, loc=0, fontsize=3)

	axe1.xaxis.set_major_formatter(tf_formatter)
	plt.setp(axe1.get_xticklabels(), rotation=30, horizontalalignment='right')
	plt.xticks(trimmedX, trimmedXLabel)
	for item in ([axe1.title, axe1.xaxis.label, axe1.yaxis.label] + axe1.get_xticklabels() + axe1.get_yticklabels()):
		item.set_fontsize(4)

	axe1.set_title("Evolution of perfact matches over time (raw number)", fontsize=10)
	#axe1.set_xlabel("Time")
	axe1.set_ylabel("Number of property")

	axe1.grid()


	#*******************************************************************************************************************************
	# GRAPH 2
	#*******************************************************************************************************************************
	
	y_total = 100 * np.asarray(nbPMtotal_list) / np.asarray(nbHit_list)
	y_daft = 100 * np.asarray(nbPMdaft_list) / np.asarray(nbHit_list)
	y_myhome = 100 * np.asarray(nbPMmyhome_list) / np.asarray(nbHit_list)
	y_daftdrop = 100 * np.asarray(nbPMdaftdrop_list) / np.asarray(nbHit_list)


	axe2 = plt.subplot(gs[3:5, :-3]) if displayAlldata else plt.subplot(gs[1, :])
	axe2.plot(x, y_daft, 'b--', label = "Daft")
	axe2.plot(x, y_myhome, 'r--', label = "MyHome")
	axe2.plot(x, y_daftdrop, 'g--', label = "DaftDrop")
	axe2.plot(x, y_total, 'k--', label = "Total perfect match")

	lines, labels = axe2.get_legend_handles_labels()
	axe2.legend(lines, labels, loc=0, fontsize=3)
	plt.ylim([0, 100])

	axe2.xaxis.set_major_formatter(tf_formatter)
	plt.setp(axe2.get_xticklabels(), rotation=30, horizontalalignment='right')
	plt.xticks(trimmedX, trimmedXLabel)
	axe2.yaxis.set_major_formatter(tf_formatter)
	plt.yticks(trimmedY, trimmedYLabel)
	for item in ([axe2.title, axe2.xaxis.label, axe2.yaxis.label] + axe2.get_xticklabels() + axe2.get_yticklabels()):
		item.set_fontsize(4)

	axe2.set_title("Evolution of perfect matches over time (percentage)", fontsize=10)
	#axe2.set_xlabel("Time")
	axe2.set_ylabel("Percentage of perfect matches")

	axe2.grid()

	if displayAlldata:
		#*******************************************************************************************************************************
		# SMALL GRAPH
		#*******************************************************************************************************************************

		(trimmedX2, trimmedXLabel2) = myxticks(x, timeframe_list, 8) # 8~25/3


		# SMALL GRAPH 1
		y_daft = []
		for i in range(len(daftCount_list)):
			temp = 100 * nbPMdaft_list[i] / daftCount_list[i] if daftCount_list[i] != 0 else 0
			y_daft.append(temp)

		axe3 = plt.subplot(gs[0:1, -2:])
		axe3.plot(x, y_daft, 'b--', label = "Daft")

		'''
		lines, labels = axe3.get_legend_handles_labels()
		axe3.legend(lines, labels, loc=0, fontsize=4)
		'''

		plt.ylim([0, 100])
		axe3.xaxis.set_major_formatter(tf_formatter)
		plt.setp(axe3.get_xticklabels(), rotation=30, horizontalalignment='right')
		plt.xticks(trimmedX2, trimmedXLabel2)
		axe3.yaxis.set_major_formatter(tf_formatter)
		plt.yticks(trimmedY, trimmedYLabel)
		for item in ([axe3.title, axe3.xaxis.label, axe3.yaxis.label] + axe3.get_xticklabels() + axe3.get_yticklabels()):
			item.set_fontsize(3)

		axe3.set_title("DaftPM / #Daft over time (percentage)", fontsize=6)
		#axe3.set_xlabel("Time")
		#axe3.set_ylabel("Percentage of perfect matches")

		axe3.grid()



		# SMALL GRAPH 2
		y_daftdrop = []
		for i in range(len(daftdropCount_list)):
			temp = 100 * nbPMdaftdrop_list[i] / daftdropCount_list[i] if daftdropCount_list[i] != 0 else 0
			y_daftdrop.append(temp)

		axe4 = plt.subplot(gs[2:3, -2:])
		axe4.plot(x, y_daftdrop, 'g--', label = "DaftDrop")

		'''
		lines, labels = axe4.get_legend_handles_labels()
		axe4.legend(lines, labels, loc=0, fontsize=4)
		'''

		plt.ylim([0, 100])

		axe4.xaxis.set_major_formatter(tf_formatter)
		plt.setp(axe4.get_xticklabels(), rotation=30, horizontalalignment='right')
		plt.xticks(trimmedX2, trimmedXLabel2)
		axe4.yaxis.set_major_formatter(tf_formatter)
		plt.yticks(trimmedY, trimmedYLabel)
		for item in ([axe4.title, axe4.xaxis.label, axe4.yaxis.label] + axe4.get_xticklabels() + axe4.get_yticklabels()):
			item.set_fontsize(3)

		axe4.set_title("DaftdropPM / #Daftdrop over time (percentage)", fontsize=6)
		#axe3.set_xlabel("Time")
		#axe4.set_ylabel("Percentage of perfect matches")

		axe4.grid()

		# SMALL GRAPH 3
		y_myhome = []
		for i in range(len(myhomeCount_list)):
			temp = 100 * nbPMmyhome_list[i] / myhomeCount_list[i] if myhomeCount_list[i] != 0 else 0
			y_myhome.append(temp)

		axe5 = plt.subplot(gs[4:5, -2:])
		axe5.plot(x, y_myhome, 'r--', label = "MyHome")

		'''
		lines, labels = axe5.get_legend_handles_labels()
		axe5.legend(lines, labels, loc=0, fontsize=4)
		'''

		plt.ylim([0, 100])

		axe5.xaxis.set_major_formatter(tf_formatter)
		plt.setp(axe5.get_xticklabels(), rotation=30, horizontalalignment='right')
		plt.xticks(trimmedX2, trimmedXLabel2)
		axe5.yaxis.set_major_formatter(tf_formatter)
		plt.yticks(trimmedY, trimmedYLabel)
		for item in ([axe5.title, axe5.xaxis.label, axe5.yaxis.label] + axe5.get_xticklabels() + axe5.get_yticklabels()):
			item.set_fontsize(3)

		axe5.set_title("MyhomePM / #Myhome over time (percentage)", fontsize=6)
		#axe3.set_xlabel("Time")
		#axe5.set_ylabel("Percentage of perfect matches")

		axe5.grid()


	plt.subplots_adjust(left=0.10, bottom=0.15, right=0.985, top=0.90, wspace=0.2, hspace=0.50)
	plt.savefig(ResFolder + 'trend.png', dpi=1000)
	plt.clf()


"""
all thoses list have the same length
"""
def plotSeperatly(
	nbHit_list,
	daftCount_list,
	daftdropCount_list, 
	myhomeCount_list, 
	nbPMtotal_list, 
	nbPMdaft_list, 
	nbPMdaftdrop_list, 
	nbPMmyhome_list, 
	timeframe_list,
	displayAlldata
	):

	#fig = plt.figure()

	gs = gridspec.GridSpec(1, 1)

	x = range(0, len(nbHit_list), 1)

	# define the axis formatting routines	
	tf_formatter = FuncFormatter(lambda x, string: '$%1.1fM' % (x*1e-6))
	(trimmedX, trimmedXLabel) = myxticks(x, timeframe_list, 25) # 25 is found manually

	trimmedY = range(0, 100, 10)
	trimmedYLabel = []
	for i in trimmedY:
		trimmedYLabel.append(str(i))

    #*******************************************************************************************************************************
    # GRAPH 1
    #*******************************************************************************************************************************
	axe1 = plt.subplot(gs[0, 0])
	axe1.plot(x, nbHit_list, 'k-.', label = "Total properties")

	if displayAlldata:
		axe1.plot(x, daftCount_list, 'c-.', label = "Total properties in Daft")
		axe1.plot(x, daftdropCount_list, 'y-.', label = "Total properties in Daftdrop")
		axe1.plot(x, myhomeCount_list, 'm-.', label = "Total properties in MyHome")

	axe1.plot(x, nbPMdaft_list, 'b--', label = "Daft perfect matches")
	axe1.plot(x, nbPMmyhome_list, 'r--', label = "MyHome perfect matches")
	axe1.plot(x, nbPMdaftdrop_list, 'g--', label = "DaftDrop perfect matches")
	axe1.plot(x, nbPMtotal_list, 'k--', label = "Total perfect matches")

	lines, labels = axe1.get_legend_handles_labels()
	axe1.legend(lines, labels, loc=0, fontsize=8)

	axe1.xaxis.set_major_formatter(tf_formatter)
	plt.setp(axe1.get_xticklabels(), rotation=30, horizontalalignment='right')
	plt.xticks(trimmedX, trimmedXLabel)
	for item in ([axe1.title, axe1.xaxis.label, axe1.yaxis.label] + axe1.get_xticklabels() + axe1.get_yticklabels()):
		item.set_fontsize(5)

	axe1.set_title("Evolution of perfact matches over time (raw number)", fontsize=10)
	#axe1.set_xlabel("Time")
	axe1.set_ylabel("Number of property")

	plt.grid()

	plt.subplots_adjust(left=0.10, bottom=0.15, right=0.985, top=0.90, wspace=0.2, hspace=0.50)
	plt.savefig(ResFolder + 'trend_raw.png', dpi=1000)
	plt.clf()


	#*******************************************************************************************************************************
	# GRAPH 2
	#*******************************************************************************************************************************
	
	y_total = 100 * np.asarray(nbPMtotal_list) / np.asarray(nbHit_list)
	y_daft = 100 * np.asarray(nbPMdaft_list) / np.asarray(nbHit_list)
	y_myhome = 100 * np.asarray(nbPMmyhome_list) / np.asarray(nbHit_list)
	y_daftdrop = 100 * np.asarray(nbPMdaftdrop_list) / np.asarray(nbHit_list)

	axe2 = plt.subplot(gs[0, 0])
	axe2.plot(x, y_daft, 'b--', label = "Daft")
	axe2.plot(x, y_myhome, 'r--', label = "MyHome")
	axe2.plot(x, y_daftdrop, 'g--', label = "DaftDrop")
	axe2.plot(x, y_total, 'k--', label = "Total perfect match")

	lines, labels = axe2.get_legend_handles_labels()
	axe2.legend(lines, labels, loc=0, fontsize=8)
	plt.ylim([0, 100])

	axe2.xaxis.set_major_formatter(tf_formatter)
	plt.setp(axe2.get_xticklabels(), rotation=30, horizontalalignment='right')
	plt.xticks(trimmedX, trimmedXLabel)
	axe2.yaxis.set_major_formatter(tf_formatter)
	plt.yticks(trimmedY, trimmedYLabel)
	for item in ([axe2.title, axe2.xaxis.label, axe2.yaxis.label] + axe2.get_xticklabels() + axe2.get_yticklabels()):
		item.set_fontsize(5)

	axe2.set_title("Evolution of perfect matches over time (percentage)", fontsize=10)
	#axe2.set_xlabel("Time")
	axe2.set_ylabel("Percentage of perfect matches")

	plt.grid()

	plt.subplots_adjust(left=0.10, bottom=0.15, right=0.985, top=0.90, wspace=0.2, hspace=0.50)
	plt.savefig(ResFolder + 'trend_percentage.png', dpi=1000)
	plt.clf()


	#*******************************************************************************************************************************
	# SMALL GRAPH
	#*******************************************************************************************************************************
	# SMALL GRAPH 1
	y_daft = []
	for i in range(len(daftCount_list)):
		temp = 100 * nbPMdaft_list[i] / daftCount_list[i] if daftCount_list[i] != 0 else 0
		y_daft.append(temp)


	axe3 = plt.subplot(gs[0, 0])
	axe3.plot(x, y_daft, 'b--', label = "Daft")

	'''
	lines, labels = axe3.get_legend_handles_labels()
	axe3.legend(lines, labels, loc=0, fontsize=4)
	'''

	plt.ylim([0, 100])
	axe3.xaxis.set_major_formatter(tf_formatter)
	plt.setp(axe3.get_xticklabels(), rotation=30, horizontalalignment='right')
	plt.xticks(trimmedX, trimmedXLabel)
	axe3.yaxis.set_major_formatter(tf_formatter)
	plt.yticks(trimmedY, trimmedYLabel)
	for item in ([axe3.title, axe3.xaxis.label, axe3.yaxis.label] + axe3.get_xticklabels() + axe3.get_yticklabels()):
		item.set_fontsize(5)

	axe3.set_title("Evolution of Daft perfect matches on the number of Daft properties over time.", fontsize=8)
	#axe3.set_xlabel("Time")
	#axe3.set_ylabel("Percentage of perfect matches")

	plt.grid()

	plt.subplots_adjust(left=0.10, bottom=0.15, right=0.985, top=0.90, wspace=0.2, hspace=0.50)
	plt.savefig(ResFolder + 'trend_daft.png', dpi=1000)
	plt.clf()



	# SMALL GRAPH 2
	y_daftdrop = []
	for i in range(len(daftdropCount_list)):
		temp = 100 * nbPMdaftdrop_list[i] / daftdropCount_list[i] if daftdropCount_list[i] != 0 else 0
		y_daftdrop.append(temp)

	axe4 = plt.subplot(gs[0, 0])
	axe4.plot(x, y_daftdrop, 'g--', label = "DaftDrop")

	'''
	lines, labels = axe4.get_legend_handles_labels()
	axe4.legend(lines, labels, loc=0, fontsize=4)
	'''

	plt.ylim([0, 100])

	axe4.xaxis.set_major_formatter(tf_formatter)
	plt.setp(axe4.get_xticklabels(), rotation=30, horizontalalignment='right')
	plt.xticks(trimmedX, trimmedXLabel)
	axe4.yaxis.set_major_formatter(tf_formatter)
	plt.yticks(trimmedY, trimmedYLabel)
	for item in ([axe4.title, axe4.xaxis.label, axe4.yaxis.label] + axe4.get_xticklabels() + axe4.get_yticklabels()):
		item.set_fontsize(5)

	#axe4.set_title("DaftdropPM / #Daftdrop over time (percentage)", fontsize=6)
	axe4.set_title("Evolution of Daftdrop perfect matches on the number of Daftdrop properties over time.", fontsize=8)
	#axe3.set_xlabel("Time")
	#axe4.set_ylabel("Percentage of perfect matches")

	plt.grid()

	plt.subplots_adjust(left=0.10, bottom=0.15, right=0.985, top=0.90, wspace=0.2, hspace=0.50)
	plt.savefig(ResFolder + 'trend_daft.png', dpi=1000)
	plt.clf()


	# SMALL GRAPH 3
	y_myhome = []
	for i in range(len(myhomeCount_list)):
		temp = 100 * nbPMmyhome_list[i] / myhomeCount_list[i] if myhomeCount_list[i] != 0 else 0
		y_myhome.append(temp)

	axe5 = plt.subplot(gs[0, 0])
	axe5.plot(x, y_myhome, 'r--', label = "MyHome")

	'''
	lines, labels = axe5.get_legend_handles_labels()
	axe5.legend(lines, labels, loc=0, fontsize=4)
	'''

	plt.ylim([0, 100])

	axe5.xaxis.set_major_formatter(tf_formatter)
	plt.setp(axe5.get_xticklabels(), rotation=30, horizontalalignment='right')
	plt.xticks(trimmedX, trimmedXLabel)
	axe5.yaxis.set_major_formatter(tf_formatter)
	plt.yticks(trimmedY, trimmedYLabel)
	for item in ([axe5.title, axe5.xaxis.label, axe5.yaxis.label] + axe5.get_xticklabels() + axe5.get_yticklabels()):
		item.set_fontsize(5)

	#plt.set_title("MyhomePM / #Myhome over time (percentage)", fontsize=6)
	axe5.set_title("Evolution of Myhome perfect matches on the number of Myhome properties over time.", fontsize=8)
	#axe3.set_xlabel("Time")
	#axe5.set_ylabel("Percentage of perfect matches")

	plt.grid()


	plt.subplots_adjust(left=0.10, bottom=0.15, right=0.985, top=0.90, wspace=0.2, hspace=0.50)
	plt.savefig(ResFolder + 'trend_myhome.png', dpi=1000)
	plt.clf()

def displayresult(tab, folder, n, tf):

	#*******************************************************************************************************************************
	# GRAPHS
	#*******************************************************************************************************************************

	gs = gridspec.GridSpec(1, 10)
	#plt.title(tf)
	plt.suptitle(tf, size=12)

	#*******************************************************************************************************************************
	# GRAPH 1
	#*******************************************************************************************************************************

	axe1 = plt.subplot(gs[0, 1:-4])
	v = venn3(
		subsets = (
			(tab['NotDaftAndNotDatfdropAndMyhome'] + 1),
			(tab['NotDaftAndDatfdropAndNotMyhome'] + 1),
			(tab['NotDaftAndDatfdropAndMyhome'] + 1),
			(tab['DaftAndNotDatfdropAndNotMyhome'] + 1),
			(tab['DaftAndNotDatfdropAndMyhome'] + 1),
			(tab['DaftAndDatfdropAndNotMyhome'] + 1),
			(tab['DaftAndDatfdropAndMyhome'] + 1)
			),
		set_labels = ('MyHome', 'DaftDrop', 'Daft'),
		ax = axe1
		)
	
	if v.get_label_by_id('100') != None:
		v.get_label_by_id('100').set_text(str(tab['NotDaftAndNotDatfdropAndMyhome']))
	if v.get_label_by_id('010') != None:
		v.get_label_by_id('010').set_text(str(tab['NotDaftAndDatfdropAndNotMyhome']))
	if v.get_label_by_id('110') != None:
		v.get_label_by_id('110').set_text(str(tab['NotDaftAndDatfdropAndMyhome']))
	if v.get_label_by_id('001') != None:
		v.get_label_by_id('001').set_text(str(tab['DaftAndNotDatfdropAndNotMyhome']))
	if v.get_label_by_id('101') != None:
		v.get_label_by_id('101').set_text(str(tab['DaftAndNotDatfdropAndMyhome']))
	if v.get_label_by_id('011') != None:
		v.get_label_by_id('011').set_text(str(tab['DaftAndDatfdropAndNotMyhome']))
	if v.get_label_by_id('111') != None:
		v.get_label_by_id('111').set_text(str(tab['DaftAndDatfdropAndMyhome']))

	axe1.set_title("Repartition of perfect matches", fontsize=10)
    
    #*******************************************************************************************************************************
    # GRAPH 2
    #*******************************************************************************************************************************

	x = np.arange(1)
	width = 0.3  # the width of the bars

	nbPMdaft_list = [tab['nbDaftPerfectMacth']]
	nbPMmyhome_list = [tab['nbMyHomePefectMacth']] 
	nbPMdaftdrop_list = [tab['nbDaftdropPerfectMacth']]
	nbPMtotal_list = [tab['nbPerfectMatch']]
	nbHit_list = [tab['nbhit']]

	axe2 = plt.subplot(gs[0, -3:-1])
	bar1 = axe2.bar(x, nbHit_list, width*3, color = 'gray', label = "Total in PPP")
	bar2 = axe2.bar(x, nbPMtotal_list, width*3, color = 'silver', label = "#PM")
	bar3 = axe2.bar(x - width, nbPMdaft_list, width, color = 'skyblue', label = "Daft")
	bar4 = axe2.bar(x , nbPMmyhome_list, width, color = 'indianred', label = "MyHome")
	bar5 = axe2.bar(x + width, nbPMdaftdrop_list, width, color = 'forestgreen', label = "DaftDrop")


	lines, labels = axe2.get_legend_handles_labels()
	axe2.legend(lines, labels, loc=0, fontsize=4)

	autolabel(axe2, bar1, 0.8)
	autolabel(axe2, bar2, 1.1)
	autolabel(axe2, bar3, 0.8)
	autolabel(axe2, bar4, 0.8)
	autolabel(axe2, bar5, 0.8)

	#axe2.get_xaxis().set_minor_locator(mpl.ticker.AutoMinorLocator())
	axe2.xaxis.set_major_locator(plt.NullLocator())
	axe2.xaxis.set_major_formatter(plt.NullFormatter())
	plt.setp(axe2.get_xticklabels(), rotation=30, horizontalalignment='right')
	for item in ([axe2.title, axe2.xaxis.label, axe2.yaxis.label] + axe2.get_xticklabels() + axe2.get_yticklabels()):
		item.set_fontsize(8)

	axe2.set_title("Number of perfect matches", fontsize=10)
	#axe2.set_xlabel("Time")
	axe2.set_ylabel("Number of properties")
	
	plt.subplots_adjust(left=0.035, bottom=0.1, right=0.990, top=0.80, wspace=0.2, hspace=0.2)
	plt.savefig(folder + n + '.png', dpi=500)
	plt.clf()

def writeresult(tab, folder, n, tf):
	print("nb total in propertypriceregister : " + str( tab['nbhit']))
	print("has perfect match : " + str(tab['nbPerfectMatch']))
	print("has not a perfect match : " + str(tab['nbNotPerfectMatch']))
	print("check sum : " + str((tab['nbPerfectMatch'] + tab['nbNotPerfectMatch']) == tab['nbhit']))

	if tab['nbhit'] != 0:
		print("proportion of hasPerfectMatch : " + str( (100 * tab['nbPerfectMatch']/tab['nbhit'])) + "%")
		print("proportion of hasNotPerfectMatch : " + str( (100 * tab['nbNotPerfectMatch']/tab['nbhit'])) + "%")
	else:
		print("There is no hit.")

	print()
	print()
	print("nb total in daft : " + str( tab['DaftSearch_Count'] ))
	print("nb total in daftdrop : " + str( tab['DaftdropSearch_Count'] ))
	print("nb total in myhome : " + str( tab['MyHomeSearch_Count'] ))

	print("has perfect match : " + str(tab['nbPerfectMatch']))
	print()
	print("Daft And Datfdrop And Myhome : " + str(tab['DaftAndDatfdropAndMyhome']))
	print("Daft And Datfdrop Andnot Myhome : " + str(tab['DaftAndDatfdropAndNotMyhome']))
	print("Daft Andnot Datfdrop And Myhome : " + str(tab['DaftAndNotDatfdropAndMyhome']))
	print("Daft Andnot Datfdrop Andnot Myhome : " + str(tab['DaftAndNotDatfdropAndNotMyhome']))
	print("not Daft And Datfdrop And Myhome : " + str(tab['NotDaftAndDatfdropAndMyhome']))
	print("not Daft And Datfdrop Andnot Myhome : " + str(tab['NotDaftAndDatfdropAndNotMyhome']))
	print("not Daft Andnot Datfdrop And Myhome : " + str(tab['NotDaftAndNotDatfdropAndMyhome']))
	print("not Daft Andnot Datfdrop Andnot Myhome : " + str(tab['NotDaftAndNotDatfdropAndNotMyhome']))

	mysum = (tab['DaftAndDatfdropAndMyhome'] 
		+ tab['DaftAndDatfdropAndNotMyhome'] 
		+ tab['DaftAndNotDatfdropAndMyhome'] 
		+ tab['DaftAndNotDatfdropAndNotMyhome'] 
		+ tab['NotDaftAndDatfdropAndMyhome']
		+ tab['NotDaftAndDatfdropAndNotMyhome']
		+ tab['NotDaftAndNotDatfdropAndMyhome']
		+ tab['NotDaftAndNotDatfdropAndNotMyhome'])

	print("check sum : " + str(mysum) + " == " + str(tab['nbPerfectMatch']) + " : " + str(mysum  ==  tab['nbPerfectMatch']))


	print()
	print("is a daft perfectMatch : " + str(tab['nbDaftPerfectMacth']))
	print("is a daftdrop perfectMatch : " + str(tab['nbDaftdropPerfectMacth']))
	print("is a myhome perfectMatch : " + str(tab['nbMyHomePefectMacth']))
	print("check sum : " + str((tab['nbDaftPerfectMacth'] + tab['nbMyHomePefectMacth'] + tab['nbDaftdropPerfectMacth'])) + " == "  + str(tab['nbPerfectMatch']) + " : " + str((tab['nbDaftPerfectMacth'] + tab['nbMyHomePefectMacth'] + tab['nbDaftdropPerfectMacth'] ) == tab['nbPerfectMatch']))

	print()


def process(PPPSearch_hit, DaftSearch, MyHomeSearch, DaftdropSearch, folder, n, tf):

	current = {
		'nbhit' : 0,
		'nbPerfectMatch' : 0,
		'nbNotPerfectMatch' : 0,
		'nbDaftPerfectMacth' : 0,
		'nbDaftdropPerfectMacth' : 0,
		'nbMyHomePefectMacth' : 0,
		#'nbHasPerfectMatchPrice' : 0,
		#'nbHasnoPerfectMatchPrice' : 0,
		#'nbPriceDiffer' : 0,
		#'nbPriceSame' : 0,
		'DaftAndDatfdropAndMyhome' : 0,
		'DaftAndDatfdropAndNotMyhome' : 0,
		'DaftAndNotDatfdropAndMyhome' : 0,
		'DaftAndNotDatfdropAndNotMyhome' : 0,
		'NotDaftAndDatfdropAndMyhome' : 0,
		'NotDaftAndDatfdropAndNotMyhome' : 0,
		'NotDaftAndNotDatfdropAndMyhome' : 0,
		'NotDaftAndNotDatfdropAndNotMyhome' : 0,
		'DaftSearch_Count' : DaftSearch.count(),
		'MyHomeSearch_Count' : MyHomeSearch.count(),
		'DaftdropSearch_Count' : DaftdropSearch.count()
	}

	for hit in PPPSearch_hit:
		if hit["hasPerfectMatch"] == True:
			current['nbPerfectMatch'] += 1
			'''
			if "price" in hit["perfectMatches"]:
				current['nbHasPerfectMatchPrice'] += 1
				if hit["price"] != hit["perfectMatches"].price:
					current['nbPriceDiffer'] += 1
				else:
					current['nbPriceSame'] += 1
			else:
				current['nbHasnoPerfectMatchPrice'] += 1
			'''
			if "daftPerfectMatch" in hit["perfectMatches"]:
				current['nbDaftPerfectMacth'] += 1
			if "myhomePerfectMatch" in hit["perfectMatches"]:
				current['nbMyHomePefectMacth'] += 1
			if "daftdropPerfectMatch" in hit["perfectMatches"]:
				current['nbDaftdropPerfectMacth'] += 1

			if "daftPerfectMatch" in hit["perfectMatches"] :
				if "daftdropPerfectMatch" in hit["perfectMatches"]:
					if "myhomePerfectMatch" in hit["perfectMatches"]:
						current['DaftAndDatfdropAndMyhome'] += 1
					else:
						current['DaftAndDatfdropAndNotMyhome'] += 1
				else:
					if "myhomePerfectMatch" in hit["perfectMatches"]:
						current['DaftAndNotDatfdropAndMyhome'] += 1
					else:
						current['DaftAndNotDatfdropAndNotMyhome'] += 1
			else:
				if "daftdropPerfectMatch" in hit["perfectMatches"]:
					if "myhomePerfectMatch" in hit["perfectMatches"]:
						current['NotDaftAndDatfdropAndMyhome'] += 1
					else:
						current['NotDaftAndDatfdropAndNotMyhome'] += 1
				else:
					if "myhomePerfectMatch" in hit["perfectMatches"]:
						current['NotDaftAndNotDatfdropAndMyhome'] += 1
					else:
						current['NotDaftAndNotDatfdropAndNotMyhome'] += 1
		else:
			current['nbNotPerfectMatch'] += 1
		current['nbhit'] += 1

	displayresult(current, folder, n, tf)

	return current


def processByDate(PPPSearch, DaftSearch, MyHomeSearch, DaftdropSearch, ns, date_min, date_max, timeDelta):		

	total_summed = {
		'nbhit' : 0,
		'nbPerfectMatch' : 0,
		'nbNotPerfectMatch' : 0,
		'nbDaftPerfectMacth' : 0,
		'nbDaftdropPerfectMacth' : 0,
		'nbMyHomePefectMacth' : 0,
		#'nbHasPerfectMatchPrice' : 0,
		#'nbHasnoPerfectMatchPrice' : 0,
		#'nbPriceDiffer' : 0,
		#'nbPriceSame' : 0,
		'DaftAndDatfdropAndMyhome' : 0,
		'DaftAndDatfdropAndNotMyhome' : 0,
		'DaftAndNotDatfdropAndMyhome' : 0,
		'DaftAndNotDatfdropAndNotMyhome' : 0,
		'NotDaftAndDatfdropAndMyhome' : 0,
		'NotDaftAndDatfdropAndNotMyhome' : 0,
		'NotDaftAndNotDatfdropAndMyhome' : 0,
		'NotDaftAndNotDatfdropAndNotMyhome' : 0,
		'DaftSearch_Count' : 0,
		'MyHomeSearch_Count' : 0,
		'DaftdropSearch_Count' : 0
	}

	nbHit_list = []
	daftCount_list = []
	daftdropCount_list = []
	myhomeCount_list = []
	nbPMtotal_list = []
	nbPMdaft_list = []
	nbPMdaftdrop_list = []
	nbPMmyhome_list = []
	dateMin_list = []
	dateMax_list = []
	timeframe_list = []



	for i in range(0, ns):

		PPPSearchFiltered = PPPSearch.filter('range', saleDate = {"gte": date_min, "lte" : date_max})
		PPPSearchFiltered = PPPSearchFiltered[0:PPPSearchFiltered.count()]

		DaftSearchFiltered = DaftSearch.filter('range', saleAgreedDate = {"gte": date_min, "lt" : date_max})
		MyHomeSearchFiltered = MyHomeSearch.filter('range', addedDate = {"gte": date_min, "lt" : date_max})
		DaftdropSearchFiltered = DaftdropSearch.filter('range', dateEntered = {"gte": date_min, "lt" : date_max})


		name = "From_" + str(date_min) + "_to_" + str(date_max)
		timeframe = "From " + str(date_min) + " to " + str(date_max)
		name2 =  str(date_min.day) + "/" + str(date_min.month) + "/" + str((date_min.year - 2000)) + "-" + str(date_max.day) + "/" + str(date_max.month) + "/" + str((date_max.year - 2000))
		timeframe_list.append(name2)
		dateMin_list.append(date_min)
		dateMax_list.append(date_max)

		'''
		print("******************************************************************")
		print(timeframe)
		print("******************************************************************")
		'''

		hit = PPPSearchFiltered.execute()

		if len(hit) != PPPSearchFiltered.count():
			print(timeframe + " : " + str(len(hit)) + " != " + str(PPPSearchFiltered.count()) + " ; missing = " + str(PPPSearchFiltered.count() - len(hit)))

		current = process(
			hit, 
			DaftSearchFiltered, 
			MyHomeSearchFiltered, 
			DaftdropSearchFiltered, 
			ResFolder + ResFolderByDate, 
			name, 
			timeframe
			)

		total_summed['nbhit'] += current['nbhit']
		nbHit_list.append(current['nbhit'])
		total_summed['nbPerfectMatch'] += current['nbPerfectMatch']
		nbPMtotal_list.append(current['nbPerfectMatch'])
		total_summed['nbNotPerfectMatch'] += current['nbNotPerfectMatch']
		total_summed['nbDaftPerfectMacth'] += current['nbDaftPerfectMacth']
		nbPMdaft_list.append(current['nbDaftPerfectMacth'])
		total_summed['nbDaftdropPerfectMacth'] += current['nbDaftdropPerfectMacth']
		nbPMdaftdrop_list.append(current['nbDaftdropPerfectMacth'])
		total_summed['nbMyHomePefectMacth'] += current['nbMyHomePefectMacth']
		nbPMmyhome_list.append(current['nbMyHomePefectMacth'])
		#total_summed['nbHasPerfectMatchPrice'] += current['nbHasPerfectMatchPrice']
		#total_summed['nbHasnoPerfectMatchPrice'] += current['nbHasnoPerfectMatchPrice']
		#total_summed['nbPriceDiffer'] += current['nbPriceDiffer']
		#total_summed['nbPriceSame'] += current['nbPriceSame']
		total_summed['DaftAndDatfdropAndMyhome'] += current['DaftAndDatfdropAndMyhome']
		total_summed['DaftAndDatfdropAndNotMyhome'] += current['DaftAndDatfdropAndNotMyhome']
		total_summed['DaftAndNotDatfdropAndMyhome'] += current['DaftAndNotDatfdropAndMyhome']
		total_summed['DaftAndNotDatfdropAndNotMyhome'] += current['DaftAndNotDatfdropAndNotMyhome']
		total_summed['NotDaftAndDatfdropAndMyhome'] += current['NotDaftAndDatfdropAndMyhome']
		total_summed['NotDaftAndDatfdropAndNotMyhome'] += current['NotDaftAndDatfdropAndNotMyhome']
		total_summed['NotDaftAndNotDatfdropAndMyhome'] += current['NotDaftAndNotDatfdropAndMyhome']
		total_summed['NotDaftAndNotDatfdropAndNotMyhome'] += current['NotDaftAndNotDatfdropAndNotMyhome']
		total_summed['DaftSearch_Count'] += current['DaftSearch_Count']
		total_summed['DaftdropSearch_Count'] += current['DaftdropSearch_Count']
		total_summed['MyHomeSearch_Count'] += current['MyHomeSearch_Count']
		daftCount_list.append(current['DaftSearch_Count'])
		daftdropCount_list.append(current['DaftdropSearch_Count'])
		myhomeCount_list.append(current['MyHomeSearch_Count'])

		date_min -= tDelta
		date_max -= tDelta


	nbHit_list.reverse()
	nbPMtotal_list.reverse()
	nbPMdaft_list.reverse()
	nbPMdaftdrop_list.reverse()
	nbPMmyhome_list.reverse()
	dateMin_list.reverse()
	dateMax_list.reverse()
	timeframe_list.reverse()
	daftCount_list.reverse()
	daftdropCount_list.reverse()
	myhomeCount_list.reverse()

	plotSeperatly(
		nbHit_list, 
		daftCount_list, 
		daftdropCount_list, 
		myhomeCount_list, 
		nbPMtotal_list, 
		nbPMdaft_list, 
		nbPMdaftdrop_list, 
		nbPMmyhome_list, 
		timeframe_list,
		False
		)


	plotInOne(
		nbHit_list, 
		daftCount_list, 
		daftdropCount_list, 
		myhomeCount_list, 
		nbPMtotal_list, 
		nbPMdaft_list, 
		nbPMdaftdrop_list, 
		nbPMmyhome_list, 
		timeframe_list,
		True
		)

	#plot2(nbHit_list, nbPMtotal_list, nbPMdaft_list, nbPMdaftdrop_list, nbPMmyhome_list, timeframe_list)
	displayresult(total_summed, ResFolder, "total_summed", "Total (summed)")

	#return total_summed

#***********************************************************************************************************************************









#***********************************************************************************************************************************
#main
#***********************************************************************************************************************************

# Define a default Elasticsearch client
elasticServer = 'http://172.20.30.70:9200/'	#prod
#elasticServer = 'http://172.20.31.19:9200/' #dev

client = Elasticsearch(hosts=[elasticServer])

q = Q('match', id='_search')

sPPP = Search(using=client, index="propertypriceregister", doc_type="propertypriceregister").query()
sDaft = Search(using=client, index="daft", doc_type="daftproperty").query()
sMyHome = Search(using=client, index="myhome", doc_type="myhomeproperty").query()
sDaftdrop = Search(using=client, index="daftdrop", doc_type="daftdropproperty").query()


numbersSteps = 108 #(52 weeks/years * 8 years / 4 ) + 4
#numbersSteps = 2 #test

tDelta = timedelta(weeks = 4)


d_max = date.today() #prod
#d_max = date(year = 2018, month = 4, day = 1) #test
# d_max = date(year = today.year, month = today.month) + timedelta(weeks = 4) ?????

d_min = d_max - timedelta(weeks = 3, days = 6)

processByDate(sPPP, sDaft, sMyHome, sDaftdrop, numbersSteps, d_min, d_max, tDelta)




''' not needed anymore as the filtering is working as it should
print("******************************************************************")
print("Total (real)")
print("******************************************************************")
process(sPPP.scan(), sDaft, sMyHome, sDaftdrop, ResFolder, "realTotal", "Total (real)")
'''