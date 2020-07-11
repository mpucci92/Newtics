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

###################################################################################################

def tickers(item, tags):

	http_tickers = []
	ns_http_tickers = []

	symbols = []
	ns_symbols = []

	taxonomy_tickers = []
	ns_taxonomy_tickers = []

	for tag in tags:

		if not tag['scheme']:
			continue

		if "ISIN" in tag['scheme']:
			continue

		if "http" in tag['scheme']:

			url = tag['scheme'].split("/")[3:]
			url = set(url)

			if len(url.intersection(href_set)) == 1:

				ticker = tag['term']
				if ticker in ticker_set:
					http_tickers.append(ticker)
				else:
					ns_http_tickers.append(ticker)

			elif "taxonomy" in url:

				finds = re.findall("\s([A-Z]+)\s", f" {tag['term']} ")
				if len(finds) == 1:
					
					ticker = tag['term']
					if ticker in ticker_set:
						taxonomy_tickers.append(ticker)
					else:
						ns_taxonomy_tickers.append(ticker)

		elif tag['scheme'] == "stock-symbol":

			ticker = tag['term']
			if ticker in ticker_set:
				symbols.append(ticker)
			else:
				ns_symbols.append(ticker)

	item['z_http_tickers'] = http_tickers
	item['z_ns_http_tickers'] = ns_http_tickers

	item['z_symbols'] = symbols
	item['z_ns_symbols'] = ns_symbols

	item['z_taxonomy_tickers'] = taxonomy_tickers
	item['z_ns_taxonomy_tickers'] = ns_taxonomy_tickers

	### Other OTC:OXUT -> Remove other from the tag value.
	### Tickers with numbers in it? Keep or remove.. not sure.

	return item

if __name__ == '__main__':

	ctr = 0

	for i, item in enumerate(items):

		print(i, i / len(items))

		try:
			tags = item['tags']
		except:
			tags = []

		item = tickers(item, tags)

		s = 0
		for key in ['http_tickers', 'symbols', 'taxonomy_tickers']:
			s += len(item['z_' + key])
			s += len(item['z_ns_'+key])
		ctr += 1 if s > 0 else 0

	print()
	print(ctr / len(items))

	with open("data/items.json", "w") as file:
		file.write(json.dumps(items))