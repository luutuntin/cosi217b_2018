#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#from __future__ import print_function, with_statement

"""
cosi217b- AMR2KB
alexluu@brandeis.edu
Python 3.6

References:
+ https://github.com/RaRe-Technologies/gensim/issues/552 <-> extract_pages()
+ https://rhettinger.wordpress.com/2011/05/26/super-considered-super/
+ https://en.wikinews.org/wiki/Category:January_2005
+ https://en.wikinews.org/wiki/Wikinews:2005/February
(+ https://en.wikinews.org/wiki/Category:March_2005)

Notes:
+ link to the article: https://en.wikinews.org/wiki?curid=[pageid]
"""

import bz2
from gensim.corpora.dictionary import Dictionary
from gensim.corpora.wikicorpus import *
from gensim import utils
import re
import spacy
import itertools
import time

DUMMY = Dictionary([['dummy']]) #Dictionary() doesn't work

IGNORED_NAMESPACES = (x+':' for x in IGNORED_NAMESPACES)
IGNORED_TITLES = ('main page','news briefs:','digest/','crosswords/') # 'wikinews:','portal:','australia/'
IGNORED_TEXTS = ('#redirect')
CONTEXT = ('date=','location=')

RE_P14_edited = re.compile(r'\[\[[Cc]ategory:[^][]*\]\]', re.UNICODE)
# pageid and title
RE_P17 = re.compile(r'(^.+\n.+\n)')
# templates
RE_template_1 = re.compile(r'{{([^\|:]+)}}(( )+)?')
RE_template_2 = re.compile(r'{{([^:{}=]+)}}')
RE_template_3 = re.compile(r'{{([\w\|= ,.;:\(\)-]+)}}(( )+)?')

def _repl_or(matchobj):
    return (matchobj.group(1)).split('|')[-1]

def _repl_byline(matchobj):    
    if '|' not in matchobj.group(1): # {{Template:India}}
        return ''
    temp = matchobj.group(1).split('|')
    output = ''
    for x in temp:
        if any(x.lower().startswith(y) for y in CONTEXT):
            output += x.partition('=')[2] + '\n'
    return output

def process_enwikinews(s,verbose=True):
    # extract text (vs pageid and title)
    ss = RE_P17.split(s)
    if len(ss)!=3 or not ss[2]:        
        if verbose:
            print('There is no text in this acticle.')
        return None
    # [:-1] means remove the last '\n' in RE_P17
    pageid, _, title = ss[1][:-1].partition('\n')
    if any(title.lower().startswith(x) for x in IGNORED_TITLES):
        if verbose:
            print('This article does not have a normal title.')
        return None
    text = ss[2].strip()
    if any(text.lower().startswith(x) for x in IGNORED_TEXTS):
        if verbose:
            print('This article does not have a normal text.')
        return None
    # extract main content of text (i.e. remove its tail)
    text = text.partition('{{haveyoursay}}')    
    if not text[1]:
        text = text[0].partition('==')
    text = text[0].strip()
    
    # from filter_wiki()
    text = utils.to_unicode(text,'utf8',errors='ignore')
    text = utils.decode_htmlentities(text)
    
    # from remove_markup()
    text = RE_P2.sub('',text)  # remove the last list (=languages)
    ## template-related (for future: ...=...)
    ### {{Brazil}}
    text = RE_template_1.sub(r'\1\n',text)
    ### {{date|November 13, 2004}}
    text = RE_template_2.sub(_repl_or,text)
    ## file[/image]-related
    text = RE_P15.sub('',text)
    ## the rest
    iters = 0
    while True:
        old, iters = text, iters + 1
        text = RE_P0.sub('',text)  # remove comments (pageid = 1471698)
        text = RE_P1.sub('',text)  # remove footnotes
        text = RE_P9.sub('',text)  # remove outside links
        text = RE_P10.sub('MATH', text)  # remove math content
        text = RE_P11.sub('', text)  # remove all remaining tags
        text = RE_P14_edited.sub('', text)  # remove categories
        text = RE_P5.sub(r'\3', text)  # remove urls, keep description
        text = RE_P6.sub(r'\2', text)  # simplify links, keep description only
        # remove table markup
        text = text.replace('||', '\n|')  # each table cell on a separate line
        text = RE_P12.sub('\n', text)  # remove formatting lines
        text = RE_P13.sub(r'\n\3', text)  # leave only cell content
        # remove empty mark-up
        text = text.replace('[]', '')
        # stop if nothing changed between two iterations or after a fixed number of iterations
        if old == text or iters > 2:
            break
    text = text.replace('[', '').replace(']', '')  # promote all remaining markup to plain text
    # {{byline|date=November 14, 2004|location=RAMALLAH}}
    text = RE_template_3.sub(_repl_byline,text)
    # cleaning
    text = remove_template(text) # pageid = 113289
    text = re.sub('(\n)+','\n',text).strip()
    if not text:
        if verbose:
            print('This article does not have a normal text.')
        return None
    return pageid, title, text

# (output: 20874 articles)
def selected_articles(raw): # raw: list of raw texts (articles)
    for x in raw:
        temp = process_enwikinews(x,verbose=False)
        if temp:
            yield temp

# https://github.com/c-amr/camr
nlp = spacy.load('en',disable=['ner'])
# (output: 20446 articles)
def selected_articles_sents(raw):
    """ Prerequisite for camr input format (.txt - one sentence / line) """
    for pageid, title, text in selected_articles(raw):
        #sents = nlp(text).sents # <- bug (see below)
        sents = list(nlp(text).sents)
        if any(len(s)>=10 for s in sents): # sents cannot be a generator/iterator
            yield pageid, title, sents     # its wholeness is a must for the output

# https://spacy.io/usage/processing-pipelines#section-multithreading
def selected_articles_sents_multithreading(raw):
    """ Not tested yet """
    # https://github.com/explosion/spacy/issues/172#issuecomment-183963403
    #gen1, gen2, gen3 = itertools.tee(selected_articles(raw),n=3)
    gen1, gen2, gen3 = itertools.tee(selected_articles(raw),3)
    pageids = (pageid for (pageid,_,_) in gen1)
    titles = (title for (_,title,_) in gen2)
    # https://spacy.io/usage/processing-pipelines#section-multithreading
    # nlp.pipe(texts, batch_size=10000, n_threads=3)
    texts = nlp.pipe((text for (_,_,text) in gen3))
    #for pageid, title, text in itertools.izip(pagedids,titles,texts):
    for pageid, title, text in zip(pageids,titles,texts): # Python 3 specific
        if any(len(s)>=10 for s in text.sents):
            yield pageid, title, text.sents
    
    
class WikiCorpus_extended(WikiCorpus):
    """ Add self.get_texts_raw(), yielding raw texts from extract_pages() """
    # keep fname as the first argument for convinient use
    # metadata is the only new argument in comparison with WikiCorpus
    # (in WikiCorpus self.metadata is hardcoded as False)
    # assign dictionary to DUMMY to prevent self.get_texts() in __init__
    def __init__(self,fname,metadata=True,dictionary=DUMMY,**kwds): 
        super().__init__(fname=fname,dictionary=dictionary,**kwds)
        #print(self.fname)
        #print(self.dictionary)
        #print(self.metadata)
        self.metadata = metadata
        #print(self.metadata)
        self.length = None
        
    # pretty fast 
    # (<30' or ~15' on my labtop for enwikinews-20170820-pages-meta-current.xml.bz2)
    # (output: 40723 raw texts)
    def get_texts_raw(self):
        """ -> generator of untokenized texts """
        self.length = 0
        for title, text, pageid in extract_pages(bz2.BZ2File(self.fname), 
                                                 self.filter_namespaces):
            if not text or any(title.startswith(x) for x in IGNORED_NAMESPACES):
                continue
            self.length += 1
            if self.metadata:
                yield '\n'.join([pageid,title,text])
            else:
                yield text
                
if __name__ == "__main__":
    dump = "enwikinews-20170820-pages-meta-current.xml.bz2"
    corpus = WikiCorpus_extended(dump)
    
    # manually fix sentence breaks in article 1117
    # (<1h on my labtop)
#    t = time.time()
#    with open('extracted_enwikinews_untokenized.txt','w',encoding='utf-8') as f:
#        for a in selected_articles(corpus.get_texts_raw()):
#            f.write('\n'.join(a))
#            f.write('\n\n##################################################\n\n')
#    print(str(time.time()-t))

    # (<2h on my labtop)
#    t = time.time()
#    with open('extracted_enwikinews_amr_multithreading_timed.txt','w',encoding='utf-8') as f:
#        for a in selected_articles_sents(corpus.get_texts_raw()):
#            f.write('\n'.join(list(a[:-1])+[s.text for s in a[-1]]))
#            f.write('\n\n##################################################\n\n')
#    print(str(time.time()-t))

    # (~1.5h on my labtop)
#    t = time.time()
#    with open('extracted_enwikinews_amr_multithreading_timed.txt','w',encoding='utf-8') as f:
#        for a in selected_articles_sents_multithreading(corpus.get_texts_raw()):
#            f.write('\n'.join(list(a[:-1])+[s.text for s in a[-1]]))
#            f.write('\n\n##################################################\n\n')
#    print(str(time.time()-t))
    
    # (~3.5h(?I dont' know if my labtop slept for a while?) on my labtop)
#    t = time.time()
#    with open('extracted_enwikinews_amr_multithreading_timed_cleaned.txt','w',encoding='utf-8') as f:
#        for a in selected_articles_sents_multithreading(corpus.get_texts_raw()):
#            f.write('\n'.join(['ARTICLE '+a[0],a[1]]+[s.text.strip() for s in a[2] if len([t for t in s if t.is_alpha])>1])) # -> condition 'if len(...)>1' has no effect
#            f.write('\n\n##################################################\n\n')
#    print(str(time.time()-t))

    with open('extracted_enwikinews_amr_multithreading_timed_cleaned.txt',encoding='utf-8') as f1, open('extracted_enwikinews_amr_cleaned.txt','w',encoding='utf-8') as f2:
    text = f1.read()
    #text = re.sub('\n\n##################################################\n\n','',text)
    text = re.sub('\n\n##################################################\n','',text)
    f2.write(text)
    
    # https://spacy.io/usage/processing-pipelines#disabling    
    nlp = spacy.load('en',disable=['parser','tagger','ne'])

    def analyze_line(l):
        s =nlp(l)
        # https://spacy.io/usage/linguistic-features#section-tokenization
        #return len([t for t in s if t.is_alpha])
        # https://docs.python.org/3.6/library/stdtypes.html#text-sequence-type-str
        return len([t for t in s if t.orth_.isalnum()])
    
    # https://stackoverflow.com/questions/4617034/how-can-i-open-multiple-files-using-with-open-in-python
    with open('extracted_enwikinews_amr_cleaned.txt',encoding='utf-8') as f1, open('extracted_enwikinews_amr_cleaned_super.txt','w',encoding='utf-8') as f2:
        for l in f1.readlines():
            if analyze_line(l)>1:
                f2.write(l)
    # then manually fix sentence breaks in article 1117 -> 'extracted_enwikinews_amr_cleaned_super_1117.txt'
    # then purify -> 'purified_enwikinews.txt':
    # search '=' -> remove metadata including picture and box info  chronologically (lines 5154,40724-40735,139754,140550,149285,149426,149539,149548,151120,152103,152508,152554,152706,153071,154255,158801,159697,159733,166538,169117,177387,178729,178880,179071,179839,180055,180121,180779,180853-180854,181011,181694,181847,181981,182189,182453,183288,185952,190233,190697,192625,208599,208612,208921,210567,210820,211705,212938,213105,214749,215003,215185,215201,215220,215366,215491,215508,215938,215955,216288,216458,216469,216490,217937,217972,218254,218279-218280,220529,220942,222153,222476,232029,237088,240967,242154,244348,247239,247958,248100,248600,249504*,250063*,250697,251661*,252442*,255749,256819,256837,258235,260835,261023,262658,266491,275825*,278890,279067,292485,296440,296689,298435,298458,298500,304368,304384,304756,304769,308076,309843,311740,316097,321257,336669,336670,336792,336793,337878-337880,338322,338324,338427,338428,339063,339576,341734,341918-341921,344121-344126,360688-360689,363528) -> final: 383462 lines (spacy-sentences)
    # *: only part of sentence is deleted