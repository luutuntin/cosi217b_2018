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

Notes:
+ link to the article: https://en.wikinews.org/wiki?curid=[pageid]
"""

import bz2
from gensim.corpora.dictionary import Dictionary
from gensim.corpora.wikicorpus import *
from gensim import utils
import re

DUMMY = Dictionary([['dummy']]) #Dictionary() doesn't work

IGNORED_NAMESPACES = (x+':' for x in IGNORED_NAMESPACES)
IGNORED_TITLES = ('main page', 'news briefs')
IGNORED_TEXTS = ('#redirect')
CONTEXT = ('date=','location=')

# pageid and title
RE_P17 = re.compile(r'(^.+\n.+\n)')
# templates
RE_template_1 = re.compile(r'{{([^\|]+)}}(( )+)?')
RE_template_2 = re.compile(r'{{([^{}=]+)}}')
RE_template_3 = re.compile(r'{{([\w\|= ,.;:\(\)-]+)}}(( )+)?')

def _repl_or(matchobj):
    return (matchobj.group(1)).split('|')[-1]

def _repl_byline(matchobj):
    temp = matchobj.group(1).split('|')
    output = ''
    for x in temp:
        if any(x.lower().startswith(y) for y in CONTEXT):
            output += x.partition('=')[2] + '\n'
    return output

#def process_article_enwikinews(s):
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
    #text = RE_P2.sub('',text)  # remove the last list (=languages)
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
        #text = RE_P11.sub('', text)  # remove all remaining tags
        #text = RE_P14.sub('', text)  # remove categories
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

def selected_articles(raw): # raw: list of raw texts
    for x in raw:
        temp = process_enwikinews(x,verbose=False)
        if temp:
            yield temp

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
    with open('extracted_enwikinews_untokenized.txt','w',encoding='utf-8') as f:
        for t in selected_articles(corpus.get_texts_raw()):
            f.write('\n'.join(t))
            f.write('\n\n##################################################\n\n')