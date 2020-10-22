from math import sqrt,log2
#import functools

#@functools.lru_cache(maxsize=256)
def tf(f,norm,K=0.5):
	'''Computing tf using augmented frequency method'''
	#return K + (1-K)*(f/norm)
	#return 1 + log2(f)
	return (K + (1-K)*(f/norm))*(1 + log2(f))

#@functools.lru_cache(maxsize=128)
def idf(df,N):
	'''IDF using Smoothed inv. freq.'''
	#return log2(1+N/df)
	return log2(N/(1+df)) + 1			## 1+df=2N >> 0

def tf_idf(f,f_norm,df,n_docs,K_f=0.5):
	return tf(f,f_norm,K_f)*idf(df,n_docs)
