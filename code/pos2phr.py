import os, sys, importlib, pdb, json
import pdb
import pos2phr
import re, string
import statistics
from collections import defaultdict, OrderedDict
from collections import Counter

"""
Version v1 Sept. 13, 2023

To run code: 
cd /Users/peteranick/Documents/work/AskMe/code
importlib.reload(pos2phr)
(hs,h, ms, m) = pos2phr.run_all()

TODO: fold together terms that appear both as capitalized and non-capitalized
words.
"""

# Set test_p True to see nps before and after normalization/filtering
test_p = False
#test_p = True

data_dir = "/Users/peteranick/Documents/work/AskMe/data/"
data_dir = '../data'

#corpus = "processed_pos_bio"
# I have changed the directory structure to:
# data/corpora/<corpus_name>/pos
#corpus = "bio"
#file = "63578be874bed2df5c9d5cdf.txt"
#file = "5a0abedacf58f153fe2f818f.txt"

# PARAMETERS
# number of doc files to process
#num_files = 1000000
#num_files = 1000
#num_files = 100
# number of phrases containing a head or mod.
# Only heads or mods with MORE than this number of different phrases will be output.
phrase_number_threshold = 4
# minimum df and cf for a phrase to be included in heads/mods data
minimum_df = 4
minimum_cf = 8
# maximum ratio of df to cf for a phrase to be saved for a head or mod.
df_cf_ratio_max = .8

# load dictionaries with lexical data
d_lexicon_art_pro_adv = {}
d_lexicon_noun = {}
d_lexicon_prep_conj = {}
d_en_jj_vb_noise = {}


print(f'>>> loading lexical resources')

with open("lexicon_art_pro_adv.txt") as str_file:
    for line in str_file:
        line = line.strip()
        d_lexicon_art_pro_adv[line] = True

with open("lexicon_prep_conj.txt") as str_file:
    for line in str_file:
        line = line.strip()
        d_lexicon_prep_conj[line] = True

with open("lexicon_noun.txt") as str_file:
    for line in str_file:
        line = line.strip()
        (surface, lemma) = line.split(" ")
        d_lexicon_noun[surface] = lemma

with open("en_jj_vb.noise") as str_file:
    for line in str_file:
        noiseword = line.strip()
        d_en_jj_vb_noise[noiseword] = True


# default dict for data capture
# collection frequency
d_np2cf = defaultdict(int)
# document frequency
d_np2df = defaultdict(int)


# Parse a single processed_pos file to identify, filter, and normalize
# noun phrases. Conpute the term frequencies for the doc and increment df
# and cf counts for the corpus as a whole.

def pos_file2phr(filename, d_np2cf, d_np2df):
  # accumulate a list of phrases in file_phr
  file_phr = []
  with open(filename) as str_file:
    # start in "beginning" context
    #print("_____________________________________")
    context = "b"
    for line in str_file:
      line = line.strip()
      #print("%s: %s|" % (context, line))
      # There are no good markers for the lines we want out of a pos file.
      # We will have to rely on looking for blank lines in certain contexts.
      if context == "b" and len(line) >= 3 and line[0:3] == "<s>":
        context = "s"
      elif context == "s" and "\t" in line:
        # We have entered the part of speech section of output
        context = "p"
      elif context == "p" and len(line) < 1:
        # entering the nominal context
        context = "n"
      elif context == "n":
        if len(line) > 1:
          if test_p:
            print("line: %s" % line)
          # we have an np line (e.g., 184	186	Emerging data)
          # extract the third field
          np = line.split("\t")[2]
          # downcase it to make filtering easier.
          ###np = np.lower()
          cleaned = clean(np)
          # normalize the phrase (filter noise and lemmatize the head word)
          ###norm = np_normalize(cleaned)
          norm = np_normalize_wc(cleaned)

          if test_p:
            if np == norm:
              print(np)
              #pass
            else:
              print("%s => %s" % (np, norm))
              
          else:
            # Save the phrase instance in file_phr list
            # and increment cf count
            if norm != "":
              file_phr.append(norm)
              d_np2cf[norm] += 1
        else:
          # we have reached the end of the np section
          context = "b"

      if test_p:
        print("context: %s" % context)

    #"""
    # Now that we have a list of all nps in file_phr, use Counter to
    # create a dictionary of terms and frequencies for all nps in the file.
    d_np2tf = Counter(file_phr)
    for value, count in d_np2tf.most_common():
      # increment df by one for all terms found in this doc
      d_np2df[value] += 1
      #print(value, count)
    #"""
    return(d_np2tf)


"""
def np_normalize(np):
    # break the np into words by spaces
    # keeping track if we are at the start, middle, or end of a phrase.
    # if noise is at the start, trim it off.
    # if in the middle, discard the phrase
    # if last word, normalize to singular
    state = "s"
    word_l = np.split(" ")
    last_word = word_l.pop()
    if (last_word in d_en_jj_vb_noise or last_word in d_lexicon_art_pro_adv or last_word in d_lexicon_prep_conj):
        return("")
    # build up the normalized phrase from its (filtered) pieces.
    normalized_np = []
    for word in word_l:
        # remove a single quote in front or end of a word
        word = word.strip(string.punctuation)
        word = word.strip("‘•’‘")
        # For now, ignore phrases that contain a prep or conj
        if word in d_lexicon_prep_conj:
            return("")
        elif (state == "s" and word.isnumeric()):
            # treat numbers as noise if prefixes of phrase
            pass
        elif not(word in d_lexicon_art_pro_adv or word in d_en_jj_vb_noise):
            normalized_np.append(word)
            state = "m"
        elif state == "m":
            # Then we have a noise word in the middle of a phrase.
            # Reject the phrase entirely for now.
            return("")
        
    # normalize the head word
    # remove a single quote in front or end of a word
    last_word = last_word.strip(string.punctuation)
    last_word = last_word.strip("‘•’‘“”")

    if last_word in d_lexicon_noun:
        last_word = d_lexicon_noun[last_word]
    normalized_np.append(last_word)
    return(" ".join(normalized_np))
"""


# normalize while preserving case (wc)
def np_normalize_wc(np):
    # break the np into words by spaces
    # keeping track if we are at the start, middle, or end of a phrase.
    # if noise is at the start, trim it off.
    # if in the middle, discard the phrase
    # if last word, normalize to singular
    state = "s"
    word_l = np.split(" ")
    last_word_surface = word_l.pop()
    ### keep un-lowercased form of last word
    last_word = last_word_surface.lower()
    if (last_word in d_en_jj_vb_noise or last_word in d_lexicon_art_pro_adv or last_word in d_lexicon_prep_conj):
        return("")
    # build up the normalized phrase from its (filtered) pieces.
    normalized_np = []
    for word in word_l:
        # remove a single quote in front or end of a word
        word = word.strip(string.punctuation)
        word = word.strip("‘•’‘")
        ### keep around the surface word for capitalization
        surface_word = word
        word = word.lower()
        # For now, ignore phrases that contain a prep or conj
        # or illegal punctuation
        if word in d_lexicon_prep_conj:
            return("")
        elif (state == "s" and word.isnumeric()):
            # treat numbers as noise if prefixes of phrase
            pass
        elif not(word in d_lexicon_art_pro_adv or word in d_en_jj_vb_noise):
            ### filter noise based on the lowercased word form
            ### but use the surface form
            ### in our normalized_np list of words, if the lowercase form
            ### survives the lexical filtering.
            normalized_np.append(surface_word)
            state = "m"
        elif state == "m":
            # Then we have a noise word in the middle of a phrase.
            # Reject the phrase entirely for now.
            return("")
        
    # remove a single quote in front or end of a word
    last_word = last_word.strip(string.punctuation)
    last_word = last_word.strip(" ‘•’‘“”")

    # normalize head word unless it begins with a capital letter    
    if last_word_surface.istitle():
        normalized_np.append(last_word_surface)
    else:
        if last_word in d_lexicon_noun:
            last_word = d_lexicon_noun[last_word]
        normalized_np.append(last_word)
    np_string = " ".join(normalized_np)
    if np_string.isnumeric():
        # filter nps that are entirely a single number.
        # or contain illegal punc.
        return("")
    else:
        return(np_string)


def clean_dashes(s):
    # remove spaces around internal dash
    s = re.sub("\s*([/-])\s*" , "\\1", s)
    # remove an initial dash
    
    return(s)


def strip_punc(s):
    return(s.strip(string.punctuation))


def filter_p(s):
    # returns True if s contains certain punc
    chars = set('$,!#+@:%(){}[]~|®“”')
    if any((c in chars) for c in s):
        return(True)
    else:
        return(False)


def clean(s):
    # return empty string if certain punctuation is found
    if filter_p(s):
        return("")
    else:
        # strip punctuation
        s = s.strip(string.punctuation)
        s = s.strip("¸")
        # space around dashes removed
        s = re.sub("\s*([/-])\s*" , "\\1", s)
        return(s)
    
# pos2phr.process_dir("/Users/peteranick/Documents/work/AskMe/data/processed_pos_bio")


# process the bio corpus
# pos2phr.pd()
def pd():
  process_dir("/Users/peteranick/Documents/work/AskMe/data", "bio")


# Loop through the processed_pos files for the corpus and write out json files
# with tf, cf, and df values for noun phrases of one or more terms.
# To process a subset of files for testing, set num_files to a lower number.
# Output written to corpus directory: cf.json, tf.json, df.json, hr.json, mr.json
def process_dir(data_dir, corpus, num_files=10000000):
    # corpus frequency
    #d_np2cf = defaultdict(int)
    d_np2cf = Counter()
    # doc frequency
    #d_np2df = defaultdict(int)
    d_np2df = Counter()
    # tf per doc
    d_doc2tf = defaultdict(int)
    path = os.path.join(data_dir, "corpora", corpus)
    pos_path = os.path.join(data_dir, "corpora", corpus, "pos")
    print(f'>>> processing {num_files} files in {pos_path}')
    # paths for output json files
    cf_out = os.path.join(path, "cf.json")
    df_out = os.path.join(path, "df.json")
    tf_out = os.path.join(path, "tf.json")
    
    file_list = os.listdir(pos_path)
    #print(file_list[0:20])
    # loop over all files in the corpus/pos dir
    for n, file in enumerate(file_list[0:num_files]):
        if n % 100 == 0:
            print(n)
        filename = os.path.join(pos_path, file)
        #print("****Processing: %s" % filename)
        d_np2tf = pos_file2phr(filename, d_np2cf, d_np2df)
        d_doc2tf[file] = d_np2tf
    """
    # output cf and df stats
    print("--------DF stats:")
    print(d_np2df.most_common(10))
    """
    with open(df_out, 'w', encoding='utf-8') as f:
        json.dump(d_np2df, f, ensure_ascii=False, indent=4)

    """
    print("--------CF stats:")
    for k, v in d_np2cf.items():
        print(k, v.most_common(10))
    print(d_np2cf.most_common(10))
    """
        
    with open(cf_out, 'w', encoding='utf-8') as f:
        json.dump(d_np2cf, f, ensure_ascii=False, indent=4)

    """
    print("--------TF stats:___________________________")
    for k, v in d_doc2tf.items():
        print(k, v.most_common(10))
    """
        
    with open(tf_out, 'w', encoding='utf-8') as f:
        json.dump(d_doc2tf, f, ensure_ascii=False, indent=4)


# Given a sorted odict and corresponding head or mod dict,
# return a list of words that have #phrases > min_len
def trim_by_length(odict, full_dict, min_len):
    l_trimmed = []
    for np in odict:
        if len(full_dict[np]) > min_len:
            l_trimmed.append(np)
        else:
            # since odict is reverse sorted by # phrases, as soon as we reach
            # min_len, no further nps can be > min_len
            break
                
    return(l_trimmed)


# Read df and cf json files and contruct head and mod files
# min_cf and min_df are cutoffs for inclusion of an np in the list
# for any head or mod.
# min_length is the cutoff form the number of nps that have a given head or mod.
def create_head_mod_files(data_dir, corpus, min_cf=minimum_cf, min_df=minimum_df, min_length=phrase_number_threshold):
    d_head = defaultdict(list)
    d_mod = defaultdict(list)
    # try using average df/cf ratio as a diagnostic
    d_head_ratio = defaultdict(float)
    d_mod_ratio = defaultdict(float)
    
    path = os.path.join(data_dir, "corpora", corpus)
    cf_file = os.path.join(path, "cf.json")
    df_file = os.path.join(path, "df.json")
    with open(cf_file, 'r') as f:
        d_cf = json.load(f)
    with open(df_file, 'r') as f:
        d_df = json.load(f)
    # for each np in cf, if it is longer than one term, add it to the
    # list of phrases for the head and for each modifier.
    for np, cf in d_cf.items():
        word_l = np.split(" ")
        df = d_df[np]
        """
        # sanity check if df and cf ever differ
        if df != cf:
            print("diff cf, df for %s: %i, %i" % (np, cf, df))
        """
        # check if cf,df cutoffs are met
        if (len(word_l) > 1) and (cf >= min_cf) and (df >= min_df):
            #check for df/cf ratio cutoff
            ratio = round(df/cf, 2) 
            if ratio > df_cf_ratio_max:
                print("Rejecting %s, %f" % (np, ratio))
            else:
                head = word_l.pop()                
                d_head[head].append((np, cf, df))
                for mod in word_l:
                    d_mod[mod].append((np, cf, df))

    # using collections.OrderedDict()
    # Sort dictionary by value list length
    d_head_sorted = OrderedDict(sorted(d_head.items(), key = lambda x : len(x[1]), reverse=True)).keys()
    l_head_trimmed = trim_by_length(d_head_sorted, d_head, min_length)
    d_mod_sorted = OrderedDict(sorted(d_mod.items(), key = lambda x : len(x[1]), reverse=True)).keys()
    l_mod_trimmed = trim_by_length(d_mod_sorted, d_mod, min_length)

    # compute the average df/cf ratio for each head/mod.
    # If the ratio is high, we assume the phrase is not specific enough and do not include it.
    for head in l_head_trimmed:
        ratio_sum = 0
        l_ratio = []
        for np in d_head[head]:
            ratio = round(np[2]/np[1], 2)
            #if ratio > .8:
            #    print("Rejecting %s, %f" % (np[0], ratio))
            #else:
            ratio_sum += ratio
            l_ratio.append(ratio)
        ### note cannot take median of empty list!
        d_head_ratio[head] = (round(ratio_sum/len(d_head[head]), 2), round(statistics.median(l_ratio), 2) ) 

    for mod in l_mod_trimmed:
        ratio_sum = 0.0
        l_ratio = []
        for np in d_mod[mod]:
            ratio = round(np[2]/np[1])
            #if ratio > .8:
            #    print("Rejecting %s, %f" % (np[0], ratio))
            #else:
            l_ratio.append(ratio)
            ratio_sum += ratio
        #pdb.set_trace()
        d_mod_ratio[mod] = (round(ratio_sum/len(d_mod[mod]), 2), round(statistics.median(l_ratio), 2) ) 

    # printing result
    #print("Sorted keys by value list : " + str(d_head_sorted))
    print("Trimmed keys: %s" % l_head_trimmed)

    # write out as json files
    # paths for output json files
    heads_out = os.path.join(path, "heads.json")
    mods_out = os.path.join(path, "mods.json")
    heads_trimmed_out = os.path.join(path, "heads_trimmed.json")
    mods_trimmed_out = os.path.join(path, "mods_trimmed.json")
    head_ratio_out = os.path.join(path, "head_ratio.json")
    mod_ratio_out = os.path.join(path, "mod_ratio.json")

    with open(heads_out, 'w', encoding='utf-8') as f:
        json.dump(d_head, f, ensure_ascii=False, indent=4)
    with open(heads_trimmed_out, 'w', encoding='utf-8') as f:
        json.dump(l_head_trimmed, f, ensure_ascii=False, indent=4)
    with open(mods_out, 'w', encoding='utf-8') as f:
        json.dump(d_mod, f, ensure_ascii=False, indent=4)
    with open(mods_trimmed_out, 'w', encoding='utf-8') as f:
        json.dump(l_mod_trimmed, f, ensure_ascii=False, indent=4)

    with open(head_ratio_out, 'w', encoding='utf-8') as f:
        json.dump(d_head_ratio, f, ensure_ascii=False, indent=4)
    with open(mod_ratio_out, 'w', encoding='utf-8') as f:
        json.dump(d_mod_ratio, f, ensure_ascii=False, indent=4)
        
    return(l_head_trimmed, d_head, l_mod_trimmed, d_mod, d_head_ratio, d_mod_ratio)

            
def test(corpus, file):
    test_file = os.path.join(data_dir, "corpora", corpus, "pos", file)
    pos_file2phr(test_file)


# (h,m) = pos2phr.test_chmf("bio")
def test_chmf(corpus):
    r = create_head_mod_files(data_dir, corpus)
    return(r)


# Full run
# (hs,h, ms, m, hr, mr) = pos2phr.run_all("mol")

# Test run to create df, cf, tf files only
# pos2phr.run_all("mol", 100, False)
# bio corpus takes 7 minutes to run on mac.

def run_all(corpus, num_files=100000000, create_hm=True):
    process_dir(data_dir, corpus, num_files=num_files)
    if create_hm:
        r = create_head_mod_files(data_dir, corpus)
        return(r)
    

if __name__ == '__main__':

    corpus = 'bio'
    if len(sys.argv) > 1 and sys.argv[1] in ('bio', 'geo', 'mol'):
        corpus = sys.argv[1]
    (hs, h, ms, m, hr, mr) = run_all(corpus, num_files=100000)
