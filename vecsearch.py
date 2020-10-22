import re,os
from lxml import etree
#from nltk.tokenize import word_tokenize,sent_tokenize
#from nltk.tag.stanford import StanfordNERTagger
from nltk.stem import PorterStemmer
import json
import gzip
#from collections import OrderedDict
from math import sqrt,log2
from constants import STOP_WORDS, WORD2NUM, MONTH_ABR
from utils import *
import argparse
#from collections import Counter

"""
jar = "./stanford-ner-4.0.0/stanford-ner.jar"
model = './stanford-ner-4.0.0/classifiers/english.all.3class.distsim.crf.ser.gz'
ner_tagger = StanfordNERTagger(model, jar, encoding='utf8')
"""

porter = PorterStemmer()

# tags = ['PERSON', 'LOCATION','ORGANIZATION']
# stop = ['.',',',':',';','"','!','?','%']

def read_queryset(dict_path,idx_path,query_path,output_path,res_cutoff):
		
		# open a new file if already exists
		with open(output_path,'w') as f:
			pass

		"""
		with open(dict_path, 'r') as fp:
			IDX = json.load(fp)
		with open(idx_path, 'r') as fp:
			POST = json.load(fp)
		"""
		# gzip
		with gzip.GzipFile(dict_path, 'r') as f:  #dict
			IDX = json.loads(f.read().decode('utf-8'))

		with gzip.GzipFile(idx_path, 'r') as f:		#idx
			POST = json.loads(f.read().decode('utf-8'))
		

		di = IDX[0]
		doc = IDX[1]
		#n_docs = len(doc)
		po = POST
		doc_docno = doc[0]
		doc_docnorm = doc[1]
		doc_docfreqmax= doc[2]
		n_docs = len(doc_docno)
		#print(n_docs)

		#print("Loaded...")
	
		qcount=0
		with open(query_path,'r') as f:
			want_query_num = True
			qnum = None
			TAG_NER = set(["l:","o:","p:","n:"])
			#res = {}
			for line in f:
				if want_query_num and line.strip()[:5]=='<num>':
					#print("Scanning Query {}".format(qcount+1))
					qnum = re.sub(r'(\<num\>|Number\:)','',line).strip()
					want_query_num = False
				elif not want_query_num and line.strip()[:7]=='<title>':
					qcount+=1
					qtext = re.sub(r'(\<title\>|Topic\:)','',line).strip()
					
					#process
					"""
					tokenized = sent_tokenize(qtext)
					qtext_processed = []
					for i in tokenized:  
						wordsList = word_tokenize(i) 
						words_ner = ner_tagger.tag(wordsList)
						for j in words_ner:
							if j[1] in tags:
								qtext_processed.append(j[1][0] + ":" + j[0]+" ")
							else:
								qtext_processed.append(j[0]+" ")
						#print(words_ner)

					qtext = re.sub("&","s:and","".join(qtext_processed))
					"""
					#qtext = " ".join(word_tokenize(qtext))
					qtext = qtext.lower().replace("'s"," ").replace("&","")
					# >>> DO NOT REPLACE : and *
					qtext = re.sub(r"(\`|\'|\’|\?|\,|\.|\"|\(|\)|\[|\]|\{|\}|\!|\%|\;)","",qtext)
					qtext = re.sub(r"(\-|\_|\/|\+|\||\~)"," ",qtext)
					#qtext = [porter.stem(word) if word[:2] not in ["P:","L:","O:","s:"] else word for word in qtext.split()]
					## qtext = qtext.split()
					#print(qtext)

					#res.update({qnum:qtext})

					q_words_ct = {}
					for q_term in qtext.split():
						q_words_ct[q_term] = q_words_ct.get(q_term,0)+1

					max_qw_freq = max(q_words_ct.values())

					res = [[0,doc_docno_el] for doc_docno_el in doc_docno] # [[num],[den]]
					#print(res)

					q_norm = 0

					for qw,qw_freq in q_words_ct.items():
						# prcess here... <new>
						# what if i need P:and??
						#if qw in STOP_WORDS:
						#	continue

						# check search types
						NE = True if qw[:2] in TAG_NER else False
						PRE = True if qw[-1] == '*' else False

						# remove * for prefix 
						qw = qw[:-1] if PRE else qw

						possible_qwords = []
						
						# if named entity, if n:, then change to l,o,p else retain
						if NE:
							if qw[:2] == 'n:':
								possible_qwords = ["L:"+qw[2:],"O:"+qw[2:],"P:"+qw[2:]]
							else:
								possible_qwords.append(qw[0].upper()+qw[1:])
						
						# not named entity search... so l,o,p, and [qw itself] if prefix search else [stemmed query word and conversions if word not in stopwords] if not prefix search
						else:
							#possible_qwords = ["L:"+qw,"O:"+qw,"P:"+qw,qw]
							possible_qwords = ["L:"+qw,"O:"+qw,"P:"+qw]
							#possible_qwords = [porter.stem(qw)]
							if PRE:
								possible_qwords.append(qw)
							
							else:
								if qw not in STOP_WORDS:
									
									qw_stemmed = porter.stem(qw)  # no collision bw two dictionaries
									if qw_stemmed in WORD2NUM:
										qw_stemmed = WORD2NUM[qw_stemmed]
									elif qw_stemmed in MONTH_ABR:
										qw_stemmed = MONTH_ABR[qw_stemmed]
									possible_qwords.append(qw_stemmed)
						
						"""
						and		L:and,O:and,P:and
						and*	L:and,P;and,P:and,and
						L:and 	L:and
						N:and 	L:and,O:and,P:and
						hello	L:hello,O:hello,P:hello,<hello>
						hello*	L:hello,O:hello,P:hello,hello

						"""

						# start search ----
						# if prefix type, then all possible startwiths...
						if PRE:
							possible_qwords=tuple(possible_qwords)
							for w in di:
								if w.startswith(possible_qwords):
									postings = po[di[w][1]]
									df = di[w][0]
									#print(df,idf(df,n_docs))

									df = idf(df,n_docs)
									#print(df)

									q_f = tf(qw_freq,max_qw_freq)
									q_tf_idf = q_f * df
									#print(q_f)


									q_norm += (q_tf_idf**2)
									#print(q_norm)

									"""
									for p in postings:
										doc_id = p[0]
										freq = p[1]
									"""
									prev_doc = 0
									for doc_id,freq in zip(postings[::2], postings[1::2]):
										doc_id += prev_doc
										prev_doc = doc_id
										freq_max = doc_docfreqmax[doc_id]
										f = tf(freq,freq_max)

										

										res[doc_id][0] += (f*df*q_tf_idf)
										#res[doc_id][1] += (f*df)**2

						else:

							for w in possible_qwords:
							
									if w not in di:
										#print("\tNF:"+w)
										continue

									"""
									if porter.stem(w) not in di:

										#print("NF: "+w)
										#if 'L:'+w not in di and 'O:'+w not in di and 'P:'+w not in di:
										#	print('Failed.')
										continue
									"""

									"""
									if "L:"+w in di:
										print("\tL:"+w)
									if "O:"+w in di:
										print("\tO:"+w)
									if "P:"+w in di:
										print("\tP:"+w)
									"""
									#w = porter.stem(w)


									
									postings = po[di[w][1]]
									df = di[w][0]
									#print(df,idf(df,n_docs))

									df = idf(df,n_docs)
									#print(df)

									q_f = tf(qw_freq,max_qw_freq)
									q_tf_idf = q_f * df
									#print(q_f)


									q_norm += (q_tf_idf**2)
									#print(q_norm)

									"""
									for p in postings:
										doc_id = p[0]
										freq = p[1]
									"""
									prev_doc = 0
									for doc_id,freq in zip(postings[::2], postings[1::2]):
										doc_id += prev_doc
										prev_doc = doc_id
										freq_max = doc_docfreqmax[doc_id]
										f = tf(freq,freq_max)

										

										res[doc_id][0] += (f*df*q_tf_idf)
										#res[doc_id][1] += (f*df)**2

							
						#print("\n\n")

					q_norm_sqrt_val = sqrt(q_norm)
					for el,for_norm in zip(res,doc_docnorm):
						#if el[0]!=0 and el[0] == sqrt(el[1]*q_norm):
						#	print(el[0],el[1],q_norm)
						el[0] = el[0]/(for_norm*q_norm_sqrt_val) if for_norm>0 and q_norm_sqrt_val>0 else 0  # handling case where query not present...

					#res = [(el[0]/sqrt(el[1]*q_norm) if el[1]>0 else 0,el[2]) for el in res]

					res.sort(key=lambda x:[-x[0],x[-1]],reverse=False)
					#print(res[:10])
					#print('\n\n')
					#print(q_norm)

					maxret = 0
					with open(output_path,'a') as f:
						for it in res:
							if it[0]>0 or maxret<res_cutoff:
								print(int(qnum),'Q0',it[-1],str(0),it[0],'prisel',file=f)
								maxret+=1
							else:
								break
						print("\n",file=f)


					want_query_num = True
				#if qcount ==10 : break
			#print(res)


if __name__ == '__main__':
	
	parser = argparse.ArgumentParser(description='Performing vector-space retrieval')
	parser.add_argument('-q','--query', metavar="queryfile", required=True,
                    help='a file containing keyword queries, with each line corresponding to a query')
	parser.add_argument('-c','--cutoff', metavar="k", type=int, default=10,
                    help='the number k (default 10) which specifies how many top-scoring results have to be returned for each query')
	parser.add_argument('-o','--output', metavar="resultfile", required=True,
                    help='the output file named resultfile which is generated by your program, which contains the document ids of all documents that have top-k (k as specified) highest-scores and their scores in each line (note that the output could contain more than k documents).')
	parser.add_argument('-i','--index', metavar="indexfile", required=True,
                    help='the index file generated by invidx cons program')
	parser.add_argument('-d','--dict', metavar="dictfile", required=True,
                    help='the dictionary file generated by invidx cons program above')
	args = parser.parse_args()
	
	#print(args)

	#print("Executing...")

	read_queryset(args.dict,args.index,args.query,args.output,args.cutoff)
