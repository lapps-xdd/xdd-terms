# tech_terms.py

import os
import json
from collections import defaultdict
import pdb

"""
Dependencies: python 3.x
This code assumes that a df.json file exists for each corpus named in the -corpora parameter.
The directory path should be of the form: <data-dir>/corpora/<corpus>/df.json
The df.json files should have been created by running pos2phr.run_all(<corpus>)

To run code from shell:
cd <code_dir>
python tech_terms.py -data_dir <data_dir> -corpora mol mars geo cultivars climate bio covd random -max_terms 10000

Definitions:
A "collection" is the full set of documents under consideration.
A "corpus" is a domain-specific subset of a collection.
A "complement" of a corpus is the full collection minus the corpus docs.

Output:

A ratio.json file is produced for each corpus named in the -corpora input parameter
ratio.json is a tsv file with the following fields:
   term
   probability ratio (corpus prob / complement prob)
   df in corpus
   corpus probability of term occurring within a document in the corpus
   df in complement (all the docs in the collection not in the corpus)
   complement probability of term occurring within a document in the collection - corpus subset

Input parameters for running the code: 

data_dir: path to the data subdirectory
corpora: list of corpus names corresponding to folders under the <data_dir>/corpora directory.
ratio_min: a cutoff for ratio indicating domain-specific terms.
   Ratio of corpus prob / collection prob
   for a term. A higher ratio indicates the term is more specific to the
   corpus relative to the collection as a whole. Defaults to 10.
max_terms: a cutoff for the number of terms output into ratio.json. Defaults to 10000.

Example call: python tech_terms.py -data_dir /Users/peteranick/Documents/work/AskMe/data/ -corpora mol mars geo cultivars climate bio covd random -max_terms 10000

"""

# We set two internal parameter to filter phrases by phrase length and frequency.
# limit the max length of technical phrases
max_phrase_length = 2
# require a certain number of occurrences of a term within a corpus
min_term_occurrence_count = 4

# List of corpus folder names
#corpus_list = ['mol', 'mars', 'geo', 'cultivars', 'climate', 'bio', 'covid', "random"]
# test lists:
#corpus_list = ['mol', 'bio']
#corpus_list = ['covid', 'climate']

"""
This module writes out a ratio.json file for each corpus named in the -corpora parameter.

"""
corpus_counts_file = "corpus_counts.json"
ratio_file = "ratio.json"

# Function for building nested dictionaries
nested_dict = lambda: defaultdict(nested_dict)

def count_files_in_directories(data_dir, directories):

    corpora_dir = os.path.join(data_dir, "corpora")
    
    counts = {}
    for directory in directories:
        full_path = os.path.join(corpora_dir, directory, "pos")
        # Get the list of files in the directory
        files = os.listdir(full_path)
        
        # Count the number of files
        num_files = len(files)
        print("***corpus: %s, num_docs: %i" % (directory, num_files))
        
        # Add the count to the dictionary with directory name as key
        counts[directory] = num_files
    
    return counts

"""
top level call to compute the number of docs in each corpus
"""
def run_cc(data_dir, corpus_list):

    corpus_counts_path = os.path.join(data_dir, corpus_counts_file)

    # Call the function to get the directory counts
    corpus_counts = count_files_in_directories(data_dir, corpus_list)

    # Write the directory counts to a file in JSON format
    with open(corpus_counts_path, 'w') as f:

        json.dump(corpus_counts, f)

# accumulate the total doc freq for a filtered subset of terms
# e.g., a filter might be one or two word terms with individual corpus df > 1
# As we iterate through the corpora, we also create a dict which contains the
# prob of the term within each corpus, using df / num_docs.
# Finally, create a dict with the prob of a term across the entire collection.
def run_ratios(data_dir, corpora, ratio_min, max_terms):
    corpora_dir = os.path.join(data_dir, "corpora")
    corpus_counts_path = os.path.join(data_dir, corpus_counts_file)
    with open(corpus_counts_path) as json_file:
        d_corpus_counts = json.load(json_file)
    collection_size = 0
    # compute size of collection for corpora under consideration
    for corpus in corpora:
        collection_size += d_corpus_counts[corpus]
    print("collection count: %i" % (collection_size))
    # key is filtered term, value is collection df
    d_term2coll_df = defaultdict(int)
    # create dict to store for each corpus a dict of term2df
    d_corpus2d_term2df = defaultdict(int)
    # dict to store for each corpus the stats for a term
    d_corpus2term2stats = nested_dict()
    for corpus in corpora:
        d_term2corpus_df = defaultdict(int)
        num_docs = d_corpus_counts[corpus]
        # key is filtered_term, value is a list of corpus df and corpus prob
        d_corpus_prob = defaultdict(list)
        print("corpus: %s, count: %i" % (corpus, num_docs))

        df_path = os.path.join(corpora_dir, corpus, "df.json")
        with open(df_path) as json_file:
            d_term2df = json.load(json_file)
        #for (term, term_df) in 
        term_list = [(k,v) for k,v in d_term2df.items() if int(v) >= min_term_occurrence_count and len(k.split(" ")) <= max_phrase_length]
        #print("term list: %s" % term_list)
        # increment collection df for the term
        for (term, df) in term_list:
            d_term2coll_df[term] += df
            # save corpus_df as well
            d_term2corpus_df[term] = df
        # store the corpus df dictionary in d_corpus2d_term_df
        d_corpus2d_term2df[corpus] = d_term2corpus_df 
        
        #ratio = round(np[2]/np[1], 2)
    #return(d_corpus2d_term2df, d_term2coll_df)
    # create dict of df and collection prob for each term
    # dict[term][df] returns df
    # dict[term][prob] returns prob
    d_coll_term2df_prob = nested_dict()

    """
    #print("****d_term2coll_df: %s" % d_term2coll_df)
    #return d_term2coll_df
    
    for result in d_term2coll_df.items():
        print("result: %s" % result)

    """
    #print("collection size: %i" % collection_size)
    for term in d_term2coll_df.keys():
        coll_df = d_term2coll_df[term]
        #pdb.set_trace()
        #print("term: %s, coll_df: %i" % (term, coll_df))
        prob = round(coll_df / collection_size, 5)
        #print("prob: %f" % prob)
        # avoid future division by 0 by replacing 0 with a very small prob
        if prob == 0.0:
            prob = 0.000000001

        d_coll_term2df_prob[term]["df"] = coll_df
        d_coll_term2df_prob[term]["prob"] = prob
        #print("term: %s, df: %i, prob: %f" % (term, coll_df, prob))
    
    # for each corpus, for each term, compute df, prob of term in corpus,
    # ratio of corpus to collection probs.

    # comp(lement) is the collection - the corpus
    # We will compare the corpus prob to the complement prob, which
    # we have to compute here on the fly.
    # comp_df will be collection df - corpus df
    # comp_num_docs will be collection size - corpus size
        
    for corpus in corpora:
        # dict to store corpus > term > df, prob, ratio (of corpus prob to coll prob)

        # extract the corpus df dictionary from d_corpus2d_term_df
        d_term2corpus_df = d_corpus2d_term2df[corpus]
        # get the total number of docs in the corpus
        num_docs = d_corpus_counts[corpus]
        comp_num_docs = collection_size - num_docs
        print("comp_num_docs: %i, collection_size: %i, num_docs: %i" % (comp_num_docs, collection_size, num_docs))
        if comp_num_docs == 0:
            #avoid division by 0 below (this should only happen if there is a single corpus, so not really necessary)
            comp_num_docs = 1
        # create a dictionary to store data for the complement set
        d_comp2term2stats = nested_dict()
        
        for term, df in d_term2corpus_df.items():
            #print(term, df)

            prob = round(df / num_docs, 5)
            # avoid future division by 0 by giving very small prob
            if prob == 0.0:
                prob = 0.000000001
            d_corpus2term2stats[corpus][term]["df"] = df
            d_corpus2term2stats[corpus][term]["prob"] = prob
            coll_prob = d_coll_term2df_prob[term]["prob"]
            comp_df = d_coll_term2df_prob[term]["df"] - df
            
            comp_prob = round(comp_df / comp_num_docs, 5)
            # avoid future division by 0 by giving very small prob
            if comp_prob == 0.0:
                comp_prob = 0.000000001

            # add entries into d_comp2term2stats
            d_comp2term2stats[term]["df"] = comp_df
            d_comp2term2stats[term]["prob"] = comp_prob
            
            # ratio based on entire collection prob for the term
            #ratio = round(prob / coll_prob, 3)
            # ratio based on complement prob for the term
            ratio = round(prob / comp_prob, 3)
            
            d_corpus2term2stats[corpus][term]["ratio"] = ratio

        # extract a subset of terms with ratio >= ratio_min and
        # create a list for sorting terms by ratio.
        ratio_list = []
        for term in d_corpus2term2stats[corpus]:
            ratio = d_corpus2term2stats[corpus][term]['ratio']
            df  = d_corpus2term2stats[corpus][term]['df']
            prob  = d_corpus2term2stats[corpus][term]['prob']

            #coll_df = d_coll_term2df_prob[term]["df"]
            #coll_prob = d_coll_term2df_prob[term]["prob"]

            comp_df = d_comp2term2stats[term]["df"]
            comp_prob = d_comp2term2stats[term]["prob"]
            
            if ratio > ratio_min:
                ratio_list.append((term, ratio, df, prob, comp_df, comp_prob))
        # sort tuples by ratio in descending order
        ratio_list.sort(key=lambda x: x[1], reverse = True)
        #print("\n\n\n\n*********ratio list for %s: %s\n" % (corpus, ratio_list[0:max_terms]))

        
        ratio_path = os.path.join(corpora_dir, corpus, ratio_file)
        with open(ratio_path, 'w') as f:
            print("creating ratio.json for %s" % corpus)
            for stats in ratio_list[0:max_terms]:
                #print('\t'.join(map(str, stats)))
                stat_line = '\t'.join(map(str, stats))
                f.write("%s\n" % stat_line)
            print("completed writing %s" % ratio_path)

    # for debugging
    #return d_coll_term2df_prob
    #return d_corpus2term2stats, d_coll_term2df_prob

# tech_terms.run_tech_terms("/Users/peteranick/Documents/work/AskMe/data/", ["bio1", "climate1"], 10, 200)
def run_tech_terms(data_dir, ratio_min, max_terms, corpora):
    print("data_dir: %s, ratio_min: %i, max_terms: %i, corpora: %s" % (data_dir, ratio_min, max_terms, corpora))
    
    print("computing number of docs for corpora...")
    run_cc(data_dir, corpora)
    print("results written to %s/corpus_counts.json" % data_dir)
    print("computing probability and ratio statistics...")
    run_ratios(data_dir, corpora, ratio_min, max_terms)
    print("run_tech_terms completed")
    

def main():
    import argparse
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-data_dir', type=str)
    arg_parser.add_argument('-ratio_min', type=int, default=10)
    arg_parser.add_argument('-max_terms', type=int, default=10000) 
    arg_parser.add_argument('-corpora', nargs='*', type=str, default=[])
    args = arg_parser.parse_args()

    print("in main. args: %s" % args)

    # Test that the df.json files exist for the corpora names passed in
    corpora_dir = os.path.join(args.data_dir, "corpora")

    for corpus in args.corpora:
        df_path = os.path.join(corpora_dir, corpus, "df.json") 
        if not os.path.isfile(df_path):
            print("ERROR: No df.json file (%s) found for corpus named %s. Exiting program." % (df_path, corpus)) 
            exit()
            
    run_tech_terms(args.data_dir, args.ratio_min, args.max_terms, args.corpora)

"""
python tech_terms.py -data_dir "/Users/peteranick/Documents/work/AskMe/data/" -ratio_min 10 -max_terms 10000 -corpora bio1 climate1
python tech_terms.py -data_dir /Users/peteranick/Documents/work/AskMe/data/ -corpora bio1 climate1 cultivars1 -max_terms 10000

python tech_terms.py -data_dir /Users/peteranick/Documents/work/AskMe/data/ -corpora mol mars geo cultivars climate bio covid random -max_terms 10000
"""
if __name__ == "__main__":
    main()
    
