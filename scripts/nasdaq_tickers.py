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

if __name__ == '__main__':

	ctr = 0

	for i, item in enumerate(items):

		nasdaq_tickers = []
		ns_nasdaq_tickers = []

		try:
			tickers = item['nasdaq_tickers']
			tickers = tickers.split(",")
			for ticker in tickers:
				if ticker in ticker_set:
					nasdaq_tickers.append(ticker)
				else:
					ns_nasdaq_tickers.append(ticker)
			ctr += 1
		except:
			pass

		item['z_nasdaq_tickers'] = nasdaq_tickers
		item['z_ns_nasdaq_tickers'] = ns_nasdaq_tickers

		# if nasdaq_tickers:
		# 	print(nasdaq_tickers)
		# 	print(ns_nasdaq_tickers)
		# 	print("---")

	print()
	print(ctr / len(items))

	with open("data/items.json", "w") as file:
		file.write(json.dumps(items))