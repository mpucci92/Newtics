from unicodedata import normalize
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
import numpy as np
import sys, os
import json
import re

###################################################################################################

with open("data/items_T.json", "r") as file:
	items = json.loads(file.read())

SUB_PAT = "<pre(.*?)</pre>|<img(.*?)/>|<img(.*?)>(.*?)</img>|</br>"

###################################################################################################

def clean(item):

	tables = []

	try:
		summary = item['cleaned_summary']
	except:
		summary = ''

	summary = re.sub(SUB_PAT, "", summary)
	_summary = BeautifulSoup(summary, "lxml")

	###############################################################################################

	_tables = _summary.find_all("table")
	for table in _tables:
		tables.append(table)
		table.replace_with(_summary.new_string(""))

	###############################################################################################

	xls = _summary.find_all("ul")
	xls += _summary.find_all("ol")
	for xl in xls:
		
		xl_str = ""
		lis = xl.find_all("li")
		
		for li in lis:

			li = li.text.strip()
			
			if len(li) == 0:
				continue

			if li[-1] not in ";.,:?!":
				li += "."

			xl_str += f"{li} "

		xl.replace_with(_summary.new_string(xl_str.strip()))

	###############################################################################################

	summary = ""
	ctr = 0
	for string in _summary.strings:
		
		summary = summary.strip()
		if len(summary) == 0:
			continue

		if string == '\n':
			ctr += 1
		else:
			ctr = 0

		if ctr > 2 and summary[-1] not in ".:;?!":
			summary = summary + f". {string}"
		else:
			summary = summary + f" {string}"

	###############################################################################################

	item['cleaned_summary'] = summary

if __name__ == '__main__':

	for item in tqdm(items):
		clean(item)
