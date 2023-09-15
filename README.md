# XDD Terms

Code to create term lists and to analyze terms in a subset of a domain/topic.

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


## Analyzing clusters of documents

Main script: `np.py`.

Only works if term lists were created and files with cluster specifications are available, see an example of the latter in this repository at `data/corpora/bio/biomedical_content_50_cluster_example.json`.

This code runs only from the Python prompt, see the instructions in the script.

