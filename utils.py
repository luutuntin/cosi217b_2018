#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
cosi217b - AMR2KB
alexluu@brandeis.edu
Python 3.4
"""

from pickle import dump, load, HIGHEST_PROTOCOL
import json

def read_lines(data_file,encoding='utf-8'):
    """ data file -> lines (a sequence of strings) """
    with open(data_file,'r',encoding=encoding) as f:
        for line in f.readlines():
            yield line

def write_lines(lines,data_file,encoding='utf-8'):
    """ lines (a sequence of strings) -> data file """
    with open(data_file,'w',encoding=encoding) as f:
        for line in lines:
            f.write(''.join([line,'\n']))

# pickle <-> binary files (Python-specific)
def save_data_pkl(data,pklfile):
    """ save data to a pickle file """        
    with open(pklfile,'wb') as f:
        dump(data,f,HIGHEST_PROTOCOL)

def load_data_pkl(pklfile):
    """ load data from a pickle file """        
    with open(pklfile,'rb') as f:
        return load(f)

# json <-> text files (human-readable)    
def save_data_jsn(data,jsnfile):
    """ save data to a json file """        
    with open(jsnfile,'w') as f:
        json.dump(data,f)

def load_data_jsn(jsnfile):
    """ load data from a json file """        
    with open(jsnfile,'r') as f:
        return json.load(f)

if __name__ == "__main__":
    pass

