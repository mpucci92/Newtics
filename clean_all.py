from hashlib import md5
from clean import clean
from tqdm import tqdm
import sys, os
import json

def write(items_to_write, ctr):
	with open(f"data/cleaned_rss_data/{ctr}.json", "w") as file:
		file.write(json.dumps(items_to_write))

if __name__ == '__main__':

	ctr = 0

	cleaned_items = []
	hashes = set()

	for filename in sorted(os.listdir("data/rss_data")):

		print("Parent File:", filename)

		if '.txt' not in filename:
			continue

		with open(f"data/rss_data/{filename}", "r") as file:
			items = json.loads(file.read())

		for item in tqdm(items):

			if 'title' not in item:
				continue

			new_item = clean(item)
			
			hashable_item = new_item.copy()
			hashable_item.pop('oscrap_timestamp')
			hashable_item.pop('timestamp')

			hash_ = md5(json.dumps(hashable_item, sort_keys=True).encode())
			hash_ = hash_.hexdigest()

			if hash_ in hashes:
				continue

			hashes.add(hash_)
			cleaned_items.append(new_item)
			ctr += 1

			if ctr % 10_000 == 0:
				print(ctr)

			if ctr % 50_000 == 0:
				write(cleaned_items, ctr)
				cleaned_items = []

	if len(cleaned_items) > 0:
		write(cleaned_items, ctr)