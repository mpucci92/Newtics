from unicodedata import normalize
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import sys, os
import json
import re

###################################################################################################

with open("data/items.json", "r") as file:
	items = json.loads(file.read())

df = pd.read_csv("data/tickers.csv")
df['FullCode'] = df.ExchangeCode + ":" + df.Ticker

fullcode_set = set(df.FullCode)
ticker_set = set(df.Ticker)
href_set = {"stock", "stocks", "symbol"}

TICKER_PAT = "[A-Z\.-]{3,15}[\s]{0,1}:[\s]{0,1}[A-Z\.-]{1,15}"
TICKER_PAT2 = "\((?:Symbol|Nasdaq|Euronext)[\s]{0,1}:[\s]{0,1}[A-Z\.-]+\)"
SUB_PAT = "<pre(.*?)</pre>|<p(.*?)>|</p>|<img(.*?)/>|<img(.*?)></img>|<sup>(.*?)</sup>"

###################################################################################################

def tickers(item, summary, _summary):

	a_tickers = []
	ns_a_tickers = []

	pat_tickers = []
	ns_pat_tickers = []

	pat2_tickers = []
	ns_pat2_tickers = []

	###############################################################################################

	a_tags = _summary.find_all("a")
	for a_tag in a_tags:

		text = f" {a_tag.text} "
		classes = a_tag.get("class", [""])
		href = set(a_tag.get("href", "").split("/")[3:])
		finds = re.findall("\s([A-Z]+)\s", text)

		if len(finds) != 1 or ' ' in a_tag.text:
			continue

		text = text.strip()

		if 'ticker' in classes or len(href.intersection(href_set)) >= 1:

			if text in ticker_set:
				a_tickers.append(text)
			else:
				ns_a_tickers.append(text)

		summary = summary.replace(str(a_tag), text)

	###############################################################################################
	
	fullcodes = re.findall(TICKER_PAT, summary)
	for fullcode in fullcodes:

		_fullcode = fullcode.replace(": ", ":")
		_fullcode = _fullcode.replace(" :", ":")
		_, ticker = _fullcode.split(":")
		
		if _fullcode in fullcode_set:
			pat_tickers.append(_fullcode)
		else:
			ns_pat_tickers.append(_fullcode)

		summary = summary.replace(fullcode, _fullcode)

	###############################################################################################

	symbols = re.findall(TICKER_PAT2, summary)
	for symbol in symbols:

		symbol = symbol[1:-1].split(":")
		symbol = symbol[1].strip()

		if symbol in ticker_set:
			pat2_tickers.append(symbol)
		else:
			ns_pat2_tickers.append(symbol)

	item['z_a_tickers'] = a_tickers
	item['z_ns_a_tickers'] = ns_a_tickers

	item['z_pat_tickers'] = pat_tickers
	item['z_ns_pat_tickers'] = ns_pat_tickers

	item['z_pat2_tickers'] = pat2_tickers
	item['z_ns_pat2_tickers'] = ns_pat2_tickers

	## 0.44173002196316946 weird (NASDAQ: **) format
	## 0.44213066879057755 weird (NASDAQ-) format
	## 0.438737238433133 inverted format (AG: NYSE) or (FR: TSX)
	## 0.43865035116935774 (Euronext Amsterdam en Brussel: KDS) weird exchange
	## 0.43819660656964254 (NASDAQ GS: ) format ??
	## 0.43779113267202474 (OTC US: ) format ??

	return item, summary

if __name__ == '__main__':

	ctr = 0

	for i, item in enumerate(items):

		print(i / len(items))

		try:
			summary = item['summary']
		except:
			summary = ''

		summary = normalize("NFKD", summary)
		_summary = BeautifulSoup(summary, "lxml")

		item, summary = tickers(item, summary, _summary)
		summary = re.sub(SUB_PAT, "", summary)

	print()
	print(ctr / len(items))

	with open("data/items.json", "w") as file:
		file.write(json.dumps(items))
 