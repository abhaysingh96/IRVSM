import re,os
from lxml import etree
#from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import json
#import pickle
import gzip
#from collections import OrderedDict
import argparse
from constants import STOP_WORDS, WORD2NUM, MONTH_ABR
from math import sqrt
from utils import *
import glob


porter = PorterStemmer()

def read_dataset(collpath,indexfile):
	TAG_NER = set(["P:","L:","O:"])
	xml = None

	for_max_freq, for_doc_norm, for_doc_no = [],[],[]

	dictionary, documents = {}, [for_doc_no,for_doc_norm,for_max_freq]
	POSTINGS, INDEX = [], [dictionary,documents]
	posting_idx = 0

	# l = 0  		# for debugging:: length of words

	#files = os.listdir(collpath)
	i,j = 0,0

	for file in glob.iglob( os.path.join(collpath, '*') ):
		""" For debugging
		if i != 236:
			i+=1
			continue
		print(file)
		""
		#if not os.path.is_file(file):
		#	continue
		#print("Scanning file {}".format(i+1))
		with open(file,'r') as f:
			xml = "<r>"+f.read()+"</r>"

		xml = xml.replace("&","") # AND is a STOP_WORD

		root = etree.fromstring(xml,parser=etree.XMLParser(recover=True))
		for doc in root.findall("DOC"):
			max_freq = 1 ## max frequency of words
			#norm_const = 0

			docno = doc.find("DOCNO").text.strip()
			#print(docno)
			texts = doc.findall('TEXT')
			for text in texts:
				text = etree.tostring(text).decode()
				#text = re.sub(r"(</?TEXT>|`|\'s|\'|\’|\?|\,|\.|\"|\+|\:|\;|\!|\%)","",text)
				#text = re.sub(r"(\-|\_)"," ",text)

				#text = " ".join(word_tokenize(text))
				text = text.lower()

				# do NOT replace /
				#text = text.replace('<text>','').replace('</text>','').replace("'s","").replace("'","").replace("’","").replace('"',"").replace("`","").replace(".","").replace("?","").replace(",","").replace("!","").replace(":","").replace(" amp;"," ").replace(";","").replace("+","").replace("%","").replace("-"," ").replace("_"," ")
				#text = text.replace('< text >','').replace('< /text >','').replace("'","").replace("’","").replace('"',"").replace("`","").replace(".","").replace("?","").replace(",","").replace("!","").replace(":","").replace(" amp;"," ").replace(";","").replace("+","").replace("%","").replace("-"," ").replace("_"," ").replace("~","").replace("|","")
				text = text.replace('<text>','').replace('</text>','').replace("'s","").replace("'","").replace("’","").replace('"',"").replace("`","").replace(".","").replace("?","").replace(",","").replace("!","").replace(":","").replace(" amp;"," ").replace(";","").replace("+","").replace("%","").replace("-"," ").replace("_"," ").replace("~"," ").replace("|"," ")
				#print(text)
				#print("\n\n\n")

				#text = text.lower()
				# Should I replace this too??
				#text = re.sub(r"</(.*?)><(.*?)>",r"</\1> <\2>",text)  # If no space between closing and opening tag, make space
				#text = re.sub(r"<organization>\s(.*?)\s</organization>",r"O:\1",text)
				#text = re.sub(r"<location>\s(.*?)\s</location>",r"L:\1",text)
				#text = re.sub(r"<person>\s(.*?)\s</person>",r"P:\1",text)
				#print(text)
				text = text.replace("<organization> ","O:").replace("<location> ","L:").replace("<person> ","P:").replace("</organization>","").replace("</location>","").replace("</person>","")
				#text = text.replace("< organization > ","O:").replace("< location > ","L:").replace("< person > ","P:").replace("< /organization >","").replace("< /location >","").replace("< /person >","")

				#print(text)
				#print("\n\n\n")
				text = [porter.stem(word) if word[:2] not in TAG_NER else word for word in text.split() if word not in STOP_WORDS]
				#print(text)

				for word in text:
					if word in WORD2NUM:
						word = WORD2NUM[word]
					elif word in MONTH_ABR:
						word = MONTH_ABR[word]
					if word not in dictionary:
						dictionary.update({word:[0,posting_idx]})
						POSTINGS.append([j,1])  # [[[j,1]],[[j+1,1]]]
						posting_idx+=1
						#norm_const += 1
						#dictionary.update({word:[[j,1]]})
					else:
						postings = POSTINGS[dictionary[word][1]]
						if j == postings[-2]:
							postings[-1] += 1
							max_freq = max(max_freq,postings[-1])
							#	+ < n^2 - (n-1)^2 > = + < (n-n+1)*(2*n-1) >
							#norm_const += (2*postings[-1]-1) 
						else:
							#postings.append(j)
							#postings.append(1)
							postings.extend([j,1])
							#norm_const += 1

				''' Get max length of words
				for word in text:
					dictionary[word]= dictionary.get(word,0) + 1
					l = max(len(word),l)
					if l == len(word):
						print(word,end="\t")
				'''

			#documents.append([docno,max_freq,0])  # update count of words in doc
				
			for_max_freq.append(max_freq)
			for_doc_no.append(docno)
			#for_doc_norm.append(0)

			j += 1

		i += 1

	#print("====================\nTotal documents found: {}".format(j))
	#for word in dictionary:
	#	dictionary[word] = [len(dictionary[word]),dictionary[word]]
	#documents[""] = j 				## total documents	
	#print(dictionary)
	#print("\n\n\n",documents)
	#print(l) # for debugging:: length of words
	
	"""
	POSTINGS = []
	DICT = OrderedDict()
	i = 0
	for key in sorted(dictionary):
		posting = dictionary[key]
		POSTINGS.append(posting)

		DICT.update({key:[len(posting),i]})
		i+=1

	INDEX = [DICT,documents]
	"""
	#n_docs = len(documents)
	n_docs = j
	for_doc_norm = [0 for i in range(n_docs)]
	#documents[1] = for_doc_norm
	#print(j)
	for key in dictionary:
		val = dictionary[key]
		posting = POSTINGS[val[1]]
		df_raw = len(posting) //2
		val[0] = df_raw
		df = idf(df_raw,n_docs)
		## beaware of d_gap eposting = POSTINGS[]
		prev_doc = 0
		for i in range(df_raw):
		#for doc_id,freq in zip(posting[::2], posting[1::2]):
			doc_id = posting[2*i]
			freq = posting[2*i+1]
			#curr_doc = for_doc_no[doc_id]
			freq_max = for_max_freq[doc_id]
			f = tf(freq,freq_max)
			#curr_doc[2] += (df*f)**2
			#for_doc_norm[doc_id] = sqrt(for_doc_norm[doc_id]**2 + (df*f)**2)
			for_doc_norm[doc_id] += (df*f)**2
			posting[2*i],prev_doc = posting[2*i]-prev_doc,posting[2*i]

	
	#for i in range(n_docs):
	#	for_doc_norm[i] = float("{:.4f}".format(sqrt(for_doc_norm[i])))

	### LOOK AT THIS!!!
	for_doc_norm = [float("{:.4f}".format(sqrt(norm_el))) for norm_el in for_doc_norm]

	documents[1] = for_doc_norm

	#print(dictionary)
	#print("\n\n\n")
	#print(documents)
	#print('\n\n\n\n\n')
	#print(POSTINGS)


	"""
	with open(str(indexfile)+'.dict', 'w') as fp:
		json.dump(INDEX,fp)
	with open(str(indexfile)+'.idx', 'w') as fp:
		json.dump(POSTINGS,fp)
	
	"""
	
	#check if utf-8 required
	with gzip.GzipFile(str(indexfile)+'.dict', 'w') as f:
		f.write(json.dumps(INDEX).encode('utf-8')) 

	with gzip.GzipFile(str(indexfile)+'.idx', 'w') as f:
		f.write(json.dumps(POSTINGS).encode('utf-8'))  
	
	"""
	with gzip.open(str(indexfile)+'.dict', 'wt') as f:
		json.dump(INDEX, f)

	with gzip.open(str(indexfile)+'.idx', 'wt',encoding="ascii") as f:
		json.dump(POSTINGS, f)
	"""


if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='Inverted indexing of the collection')
	parser.add_argument('collpath', metavar='coll-path',
                    help='the directory containing the files containing documents of the collection')
	parser.add_argument('indexfile', metavar='indexfile',
                    help='the name of the generated index files')
	args = parser.parse_args()
	collpath = args.collpath
	indexfile = args.indexfile

	#print("Executing...")
	
	read_dataset(collpath,indexfile)
	
	"""