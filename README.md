# xdd-terms

Create term files for one of the three topic domains (bionedical, geoarchive and molecular_physics).

Assumes some minimal documents structure in this repo

```
data/corpora/bio/pos
data/corpora/geo/pos
data/corpora/mol/pos
```

All this structure is included in the repository, but the `pos` directory needs to added and contain all POS files created by running the ner.py script in [https://github.com/lapps-xdd/xdd-processing](https://github.com/lapps-xdd/xdd-processing). You can link in all this files with some like:

```bash
$ ln -s /Users/Shared/data/xdd/doc2vec/topic_doc2vecs/biomedical/processed_pos data/corpora/bio/pos 
```

The first part needs to be updated to reflect your local situation.

See `code/pos2phr.py` for some pointers on how to run term/phrase creation for the three domains. You can also run the script from the command line:

```bash
$ cd code
$ python3 pos2phr.py (bio|geo|mol)
```


