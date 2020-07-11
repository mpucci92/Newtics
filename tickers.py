from unicodedata import normalize
from bs4 import BeautifulSoup
from tqdm import tqdm
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

df = pd.read_csv("data/exchanges.csv")
exchange_set = df.Acronym.dropna().tolist()
exchange_set += df['Exchange Name'].dropna().tolist()

extra_exchange_set = ["Oslo", "Paris", "Helsinki", "Copenhagen", "OTC", "OTCQX"]
extra_exchange_set += ["OTCQB", "Stockholm", "CNSX", "OTC Markets", "Brussels"]
extra_exchange_set += ["Frankfurt", "Amsterdam", "Iceland", "Vilnius", "Tallinn"]
extra_exchange_set += ["Luxembourg", "Irish", "Riga", "Symbol"]
extra_exchange_set = [exch.upper() for exch in extra_exchange_set]

exchange_set += extra_exchange_set
exchange_set = [re.sub("-|\.", "", exch) for exch in exchange_set]

TICKER_PAT = "[A-Z\.-]{3,15}[\s]{0,1}:[\s]{0,1}[A-Z\.-]{1,15}"
TICKER_PAT2 = "\((?:Symbol|Nasdaq|Euronext)[\s]{0,1}:[\s]{0,1}[A-Z\.-]+\)"
SUB_PAT = "<pre(.*?)</pre>|<p(.*?)>|</p>|<img(.*?)/>|<img(.*?)></img>|<sup>(.*?)</sup>"

###################################################################################################

def validate(match, hit, miss):

	if match.count(":") == 1:
		match = re.sub(" : |: | :", ":", match)
		exch, ticker = match.split(":")
		exch = re.sub("-|\.|Other ", "", exch).upper()
		match = f"{exch}:{ticker}"

	if match in fullcode_set:
		hit.append(match)
	elif ":" in match and match.split(":")[0] in exchange_set:
		hit.append(match)
	elif match in ticker_set:
		hit.append(match)
	else:
		miss.append(match)

	return match

def tickers(item):

	ticker_matches = []
	ticker_misses = []

	def summary():

		try:
			summary = item['summary']
		except:
			summary = ''

		_summary = BeautifulSoup(summary, "lxml")

		###########################################################################################

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
				text = validate(text, ticker_matches, ticker_misses)

			summary = summary.replace(str(a_tag), text)

		###############################################################################################
		
		fullcodes = re.findall(TICKER_PAT, summary)
		for fullcode in fullcodes:
			
			text = validate(fullcode, ticker_matches, ticker_misses)
			summary = summary.replace(fullcode, text)

		###############################################################################################

		symbols = re.findall(TICKER_PAT2, summary)
		for symbol in symbols:
			validate(symbol[1:-1], ticker_matches, ticker_misses)

		summary = re.sub(SUB_PAT, "", summary)
		item['cleaned_summary'] = summary

	def tags():

		try:
			tags = item['tags']
		except:
			tags = []

		for tag in tags:

			if not tag['scheme']:
				continue

			if "ISIN" in tag['scheme']:
				continue

			if "http" in tag['scheme']:

				url = tag['scheme'].split("/")[3:]
				url = set(url)

				if len(url.intersection(href_set)) == 1:

					validate(tag['term'], ticker_matches, ticker_misses)

				elif "taxonomy" in url:

					finds = re.findall("\s([A-Z]+)\s", f" {tag['term']} ")

					if len(finds) == 1:						
						validate(tag['term'], ticker_matches, ticker_misses)

			elif tag['scheme'] == "stock-symbol":

				validate(tag['term'], ticker_matches, ticker_misses)

	def nasdaq_tickers():

		try:

			tickers = item['nasdaq_tickers']
			tickers = tickers.split(",")
			
			for ticker in tickers:

				if ":" not in ticker:
					ticker = "NASDAQ:" + ticker

				validate(ticker, ticker_matches, ticker_misses)

		except:

			pass

	summary()
	tags()
	nasdaq_tickers()

	item['ticker_matches'] = list(set(ticker_matches))
	item['ticker_misses'] = list(set(ticker_misses))

###################################################################################################

if __name__ == '__main__':

	for item in tqdm(items):
		tickers(item)

	with open("data/items_T.json", "w") as file:
		file.write(json.dumps(items))