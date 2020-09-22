from google.cloud import storage

if __name__ == '__main__':

	client = storage.Client()
	bucket = client.bucket("oscrap_storage")

	for blob in bucket.list_blobs():

		if 'rss/' not in blob.name:
			continue

		print(blob.name)
		blob.download_to_filename(f"data/rss_data/{blob.name[4:]}")
