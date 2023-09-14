import os, importlib, pdb, json
import pdb
import pos2phr
import re, string
import statistics
from collections import defaultdict, OrderedDict
from collections import Counter
import math
from operator import itemgetter

"""
To run code: 
This code assumes that the heads, mods, tf and df for each individual file have already been processed.

Modify the line in this file starting with "cluster_file" to reference
the cluster of interest. Also set the corpus variable.
The cluster file should be placed in the corpora/<corpus_name> folder.

cd /Users/peteranick/Documents/work/AskMe/code
python
from importlib import reload
import np
np.heads("1") # run over a cluster number
# This outputs the head and its phrases for the top heads in a cluster

reload(np)

"""
corpora_dir = "/Users/peteranick/Documents/work/AskMe/data/corpora"
#corpus = "geo"
corpus = "bio"
#clusters_file = "geoarchive_content_cluster_20.json"
#clusters_file = os.path.join(corpora_dir, corpus, "geoarchive_content_cluster_20.json")
#clusters_file = os.path.join(corpora_dir, corpus, "geoarchive_content_50_cluster_example.json")
clusters_file = os.path.join(corpora_dir, corpus, "biomedical_content_50_cluster_example.json")






def populate_corpus_files(corpus):
    df_file = os.path.join(corpora_dir, corpus, "df.json")
    tf_file = os.path.join(corpora_dir, corpus, "tf.json")
    heads_file = os.path.join(corpora_dir, corpus, "heads.json")
    mods_file = os.path.join(corpora_dir, corpus, "mods.json")

    with open(df_file) as json_file:
        d_np2df = json.load(json_file)
    with open(tf_file) as json_file:
        d_doc2tf = json.load(json_file)
    with open(heads_file) as json_file:
        d_head2nps = json.load(json_file)
    with open(mods_file) as json_file:
        d_mod2nps = json.load(json_file)

    corpus_size = len(d_doc2tf)
    return(d_np2df, d_doc2tf, d_head2nps, d_mod2nps, corpus_size)
        
# read in a list of files to be a proxy for the top n results of a query
def load_clusters(clusters_file):
    with open(clusters_file) as json_file:
        d_cid2files = json.load(json_file)
    return(d_cid2files)

# corpus tables
(d_np2df, d_doc2tf, d_head2nps, d_mod2nps, corpus_size) = populate_corpus_files(corpus)
# cluster_id ("0", "1", "2") to list of files (without the .txt) 
d_cid2files = load_clusters(clusters_file)


# compute heads and mods sorted by the number of nps they occur in
def heads(cluster_id):
    # sum of the tf across terms in the result set
    d_np2r_tf = defaultdict(int)
    # sum of the df across terms within the result set
    d_np2r_df = defaultdict(int)

    d_head2r_nps = defaultdict(set)
    d_mod2r_nps = defaultdict(set)
    sorted_heads = []
    #pdb.set_trace()
    for file in d_cid2files[cluster_id]:
        filename = file + ".txt"
        d_nps = d_doc2tf[filename]

        # the key is np, value is the tf, which we ignore for now
        for (np, tf) in d_nps.items():
            l_np = np.split(" ")
            # increment the total tf across results with the current tf
            d_np2r_tf[np] += tf
            # increment the number of result set docs the term is in
            d_np2r_df[np] += 1
            if len(l_np) > 1:
                # np is phrase; add it to the set of nps with this head
                head = l_np[-1]
                d_head2r_nps[head].add(np)
                # loop over mods
                for mod in l_np[0:-1]:
                    d_mod2r_nps[mod].add(np)
    sorted_heads = sorted(d_head2r_nps, key=lambda k: len(d_head2r_nps[k]), reverse=True)
    """
    for head in sorted_heads[0:19]:
        print("head: %s" % head)
        for np in d_head2r_nps[head]:
            print("   %s" % np)
    """
    sorted_mods = sorted(d_mod2r_nps, key=lambda k: len(d_mod2r_nps[k]), reverse=True)
    """
    for mod in sorted_mods[0:19]:
        print("mod: %s" % mod)
        for np in d_mod2r_nps[mod]:
            print("   %s" % np)
    """
    
    # compute tfidf of terms in the result set.
    # list of (np, tfidf) pairs where tf is summed over docs in a result set
    l_tfidf = []
    # list of np with number of result set docs it occurs in
    l_rdf = []
    for (np, tf) in d_np2r_tf.items():
        df = d_np2df[np]
        rdf = d_np2r_df[np]
        tfidf = math.log10(tf) * math.log10(corpus_size / df)
        l_tfidf.append((np, tfidf))
        l_rdf.append((np, rdf))
                         
    sorted_tfidf = sorted(l_tfidf, key=itemgetter(1), reverse = True)
    sorted_rdf = sorted(l_rdf, key=itemgetter(1), reverse = True)
    print("tfidf scores: %s" % sorted_tfidf[0:20])
    print("*****************************")
    print("rdf scores: %s" % sorted_rdf[0:20])
    i = 1
    for (np, df) in sorted_rdf[0:29]:
        if len(d_head2r_nps[np]) > 5:
            print("%i: %s" % (i, np))
            for nps in d_head2r_nps[np]:
                print("   %s" % nps)
            i += 1
            
                
        
            
