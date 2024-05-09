# XDD Terms

Code to create term lists and to analyze terms in a subset of documents.

It includes functionality to (1) create term lists, (2) create lists of relevant terms for a document set, and (3) analyze clusters. There are two ways to do the first, the first is the original way of doings this (see next section) and the other is more integrated in the overal processing chain and has less dependencies, but it does not have all functionality.


## Creating term lists

Main script: `pos2phr.py`.

Create term files for one of the three topic domains (biomedical, geoarchive and molecular_physics).

Assumes some minimal documents structure in this repo

```
data/corpora/bio/pos
data/corpora/geo/pos
data/corpora/mol/pos
```

All this structure is included in the repository, but the `pos` directory needs to added and contain all POS files created by running the ner.py script in [https://github.com/lapps-xdd/xdd-processing](https://github.com/lapps-xdd/xdd-processing). You can link in the pos files with something like:

```bash
$ ln -s /Users/Shared/data/xdd/doc2vec/topic_doc2vecs/biomedical/processed_pos data/corpora/bio/pos
$ ln -s /Users/Shared/data/xdd/doc2vec/topic_doc2vecs/geoarchive/processed_pos data/corpora/geo/pos
$ ln -s /Users/Shared/data/xdd/doc2vec/topic_doc2vecs/molecular_physics/processed_pos data/corpora/mol/pos
```

The first part needs to be updated to reflect your local situation.

See `code/pos2phr.py` for some pointers on how to run term/phrase creation for the three domains from the Python prompt. You can also run the script from the command line:

```bash
$ cd code
$ python3 pos2phr.py (bio|geo|mol)
```


## Creating term lists - alternative entry point

Used by [https://github.com/lapps-xdd/xdd-integration](https://github.com/lapps-xdd/xdd-integration).

This does not rely on the directory structure above. It first collects the frequencies and then accumulates TFIDF scores for later insertion into the database. It does not print the head and modifier files (which should be added, even though they are not currently entered into the databse).

Frequency collection:

```
$ python pos2phr.py --pos POS_DIR --out TERMS_DIR [--limit N]
```

Run the script to collect term frequencies over the part-of-speech data in POS_DIR and write frquencies to TERMS\_DIR. Restrict counting to N documnets if --limit is used.

Accumulating TF-IDF scores:

```
$ python accumulate.py --terms TERMS_DIR
```

Take the frequencies from TERMS\_DIR and a file with frequencies and tf-idf scores.


## Creating lists of terms relevant to a set

Main script: `tech_terms.py`.

Creates a list of terms for a document set sorted on probability ratio (corpus prob / complement prob). It also shows the frequency and the probability in the document set, and the frequency and probability in the complement of the document set.

```
Martian surface   217330000.0   434   0.21733   0   1e-09
impact crater     183270000.0   366   0.18327   0   1e-09
Noachian          130200000.0   260   0.1302    0   1e-09
```

This code assumes that a df.json file exists for each corpus named in the -corpora parameter. The directory path should be of the form: `<data-dir>/corpora/<corpus>/df.json`. The df.json files should have been created by running pos2phr.run_all(<corpus>).

To run the code:

```bash
$ cd <code_dir>
$ python tech_terms.py -data_dir <data_dir> -corpora mol mars geo cultivars climate bio covd random -max_terms 10000
```
A ratio.json file is produced for each corpus named in the -corpora input parameter



## Analyzing clusters of documents

Main script: `np.py`.

Only works if term lists were created and files with cluster specifications are available, see an example of the latter in this repository at `data/corpora/bio/biomedical_content_50_cluster_example.json`.

This code runs only from the Python prompt, see the instructions in the script.

