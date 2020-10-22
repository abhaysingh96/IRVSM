import argparse,json,gzip

if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='Prints the dictionary out in a human-readable form to the screen')
	parser.add_argument('indexfile_dict', metavar='indexfile.dict',
                    help='the name of the generated index dictionary')
	args = parser.parse_args()
	
	with gzip.GzipFile(args.indexfile_dict, 'r') as f:
		IDX = json.loads(f.read().decode('utf-8'))

	dictionary = IDX[0]

	for w in sorted(dictionary):
		val = dictionary[w]
		print("{indexterm}:{df}:{offset}".format(indexterm=w,df=val[0],offset=val[1]))