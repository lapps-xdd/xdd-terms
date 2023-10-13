"""

Script to accumulate the data that later need to be inserted in some form into the
ElasticSearch database.

This assumes the following input:
	../data/corpora/DOMAIN/cf.json
	../data/corpora/DOMAIN/df.json
	../data/corpora/DOMAIN/tf.json

Those files can be created with pos2phr.py.

"""

import os, json, math

DOMAINS = ('bio', 'geo', 'mol')

FREQUENCY_THRESHOLD = 2


def domain_dir(domain):
	return os.path.join('..', 'data', 'corpora', domain)


def collect_from_domain(domain):
	data_dir = domain_dir(domain)
	cf_file = os.path.join(data_dir, 'cf.json')
	df_file = os.path.join(data_dir, 'df.json')
	tf_file = os.path.join(data_dir, 'tf.json')
	print('>>>', domain)
	#print('Loading corpus frequencies...')
	#cf_data = json.loads(open(cf_file).read())
	print('Loading document frequencies...')
	df_data = json.loads(open(df_file).read())
	print('Loading term frequencies...')
	tf_data = json.loads(open(tf_file).read())
	print('Accumulating frequencies and TFIDF scores...')
	accumulation = {}
	calculate_tfidf(df_data, tf_data, accumulation)
	return accumulation


def calculate_tfidf(df_data, tf_data, accumulation):
	docs_in_domain = len(tf_data)
	count = 0
	for fname in tf_data:
		count += 1
		#if count > 2: break
		scores = []
		identifier = os.path.splitext(fname)[0]
		accumulation[identifier] = scores
		calculate_tfidf_for_document(docs_in_domain, fname, df_data, tf_data[fname], scores)


def calculate_tfidf_for_document(
		docs_in_domain: int, fname: str, df_data: dict, tf_data: dict, scores: list):
	total_terms_count = sum(tf_data.values())
	#print(fname, total_terms_count)
	for term in tf_data:
		tf = tf_data[term]
		if tf < FREQUENCY_THRESHOLD:
			continue
		doc_count = df_data[term]
		tfidf_score = tfidf(term, tf, total_terms_count, docs_in_domain, doc_count)
		#print(f'{tfidf_score:.6f}  {fname}  {term}')
		scores.append([term, tf, tfidf_score])


def tfidf(term: str, tf: int, total_terms: int, docs_in_domain: int, docs_with_term: int):
	#print(total_terms, docs_in_domain, docs_with_term, term)
	tf = tf / total_terms
	idf = math.log10(docs_in_domain / docs_with_term)
	#print(f'{tf:.4f}, {idf:.4f}, {tf*idf:.6f}  {term}')
	return tf * idf


def test_tfidf():
	"""One thing that comes out of this testng is that we should not report this
	number for very small documents, there is just not enough to go with for those."""
	docs_in_corpus = 100
	total_terms_values = (10, 100)
	frequency_values = (1, 2, 5)
	docs_with_term_values = (1, 5, 50)
	total_terms_in_doc    = []
	term_frequency_in_doc = []
	docs_with_term        = []
	for x in total_terms_values:
		for y in frequency_values:
			for z in docs_with_term_values:
				total_terms_in_doc.append(x)
				term_frequency_in_doc.append(y)
				docs_with_term.append(z)
	for x, y, z in zip(total_terms_in_doc, term_frequency_in_doc, docs_with_term):
		tfidf_score = tfidf('', y, x, docs_in_corpus, z)
		print(f'tfidf={tfidf_score:.6f}  tf={y} terms-in-doc={x} docs-in-corpus={docs_in_corpus} docs-with-term={z}')


def analyze_frequencies():
	for fname in ('frequencies-bio.json', 'frequencies-geo.json', 'frequencies-mol.json'):
		print(fname)
		d = json.loads(open(fname).read())
		term_sizes = list(sorted([len(value) for value in d.values()]))
		print('   number of document     ', len(d))
		print('   largest number of terms', term_sizes[-1])
		print('   average number of terms', int(sum(term_sizes) / len(d)))


if __name__ == '__main__':

	#test_tfidf()
	#analyze_frequencies()
	#exit()
	for domain in DOMAINS:
		d = collect_from_domain(domain)
		with open(f'frequencies-{domain}.json', 'w') as fh:
			json.dump(d, fh, indent=2)
