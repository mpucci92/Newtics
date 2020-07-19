from unicodedata import normalize
from urllib.parse import urlparse
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

###################################################################################################

if __name__ == '__main__':

	for item in items:

		contribs = []
		for contributor in item.get("contributors", []):
			contribs.append(contributor['name'])
		item['oscrap_contributors'] = contribs
		print(item['oscrap_contributors'])