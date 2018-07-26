#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function, with_statement

"""
cosi217b- AMR2KB
alexluu@brandeis.edu
Python 3.4
"""

from amr_reader.src.reader import get_amr_table_path
import networkx as nx
from constants import *
from utils import *
import os
import itertools
from collections import defaultdict

from amr_graph import amr_graph_str, AMRGraph

def amr_subgraphs(g,num):   # g: AMRGraph object
    """ -> connected subgraphs with more than num nodes """
    output = defaultdict(list)
    # assumption: num < len(g.nodes())+1   
    for i in range(num,len(g.nodes())+1):
        for nodes in itertools.combinations(g.nodes(),i):
            sg = g.subgraph(nodes).copy()
            if nx.is_connected(sg.to_undirected()) and '@' not in sg.nodes():                
                amr_root = list(nx.topological_sort(sg))[0]
                sg.add_edge('@',amr_root,label='')
                sg = AMRGraph(sg)
                sg.meta = '# connected subgraph of {} nodes'.format(i)
                output[i].append(sg)
    return output

# future improvement: dynamtic programming style (CKY)
def amr_subgraphs_optimized(g,n_min=1,n_max=None):   # g: AMRGraph object
    """ -> connected subgraphs whose number of nodes is >= n_min & <= n_max """
    output = defaultdict(list)
    # PROXY_AFP_ENG_20021112_0467.11 - a cyclic graph
    if not nx.is_directed_acyclic_graph(g):
        print('The input graph is not directed acyclic.')
        return output
        
    amr_root = list(g.successors('@'))[0]
    order = list(nx.dfs_preorder_nodes(g,amr_root))
#    print(order)
    if not n_max:
        n_max = len(g.nodes())
    # assumption: n_min < n_max
    for i in range(n_min,n_max+1):
#        print(i)
        for n in order:
#            pool = list(nx.dfs_preorder_nodes(g,'s',depth_limit=i-1))
            pool = set(y for v in nx.dfs_successors(g,n,depth_limit=i-1).values() 
                         for y in v)
#            print(n,pool)
            if len(pool)<i-1: 
                continue
            for ns in itertools.combinations(pool,i-1):
                sg = g.subgraph((n,) + ns).copy()
                if nx.is_connected(sg.to_undirected()):                
                    amr_root = list(nx.topological_sort(sg))[0]
                    sg.add_edge('@',amr_root,label='')
                    sg = AMRGraph(sg)
                    sg.meta = '# connected subgraph of {} nodes'.format(i)
                    output[i].append(sg)
    return output

def lines_from_sent(g,n_min=1,n_max=None): # g: AMRGraph object
    """ -> list of string lines of subgraphs of one sentence graph """
    lines = []
#    sgs = amr_subgraphs(g,num)
    sgs = amr_subgraphs_optimized(g,n_min,n_max)
    for k in sgs:
        if sgs[k]:
            lines.append('#connected subgraphs of {} nodes'.format(k))
            for x in sgs[k]:
                lines.extend(amr_graph_str(x).split('\n'))
    return lines

def lines_from_doc(doc,n_min=1,n_max=None):    # doc: list of AMRGraph objects
    """ -> list of string lines of subgraphs of graphs in one document """
    lines = []
    for g in doc:
        print(g.id)
        lines.extend(g.meta.split('\n'))
        lines.extend(lines_from_sent(g,n_min,n_max))
    return lines
        

def lines_from_docs(docs,n_min=1,n_max=None):  # docs: amr_table
    """ -> list of string lines of subgraphs of graphs in all documents """
    lines = []
    for k in docs:
        print(k)
        lines.append('# {}'.format(k))
        doc = [AMRGraph(sen=docs[k][kk]) for kk in sorted(docs[k].keys())]
        lines.extend(lines_from_doc(doc,n_min,n_max))
    return [sgs ]

def amr_subgraphs_from_doc(doc,n_min=1,n_max=None):    # doc: list of AMRGraph objects
    """ -> list of string lines of subgraphs of graphs in one document """    
    return [amr_subgraphs_optimized(g,n_min,n_max) for g in doc]
        

def amr_subgraphs_from_docs(docs,n_min=1,n_max=None):  # docs: amr_table
    """ -> list of string lines of subgraphs of graphs in all documents """
    output = dict()
    for k in docs:        
        doc = [AMRGraph(sen=docs[k][kk]) for kk in sorted(docs[k].keys())]
        output[k] = amr_subgraphs_from_doc(doc,n_min,n_max)
    return output

if __name__ == "__main__":
#    pass
    # see amr_table data structure in amr_reader package (.\scr\reader.py)
#    amr_table = get_amr_table_path(AMR_PILOT_SELECTED)
    file_name = "amr-release-1.0-proxy_selected"
#    save_data_pkl(amr_table,os.path.join(AMR_PILOT_SELECTED_PKL,
#                                         ''.join([file_name,'.pkl'])))
    # TypeError: <amr_reader.models.Sentence.Sentence object at ... 
    #            is not JSON serializable
#    save_data_jsn(amr_table,os.path.join(AMR_PILOT_SELECTED_JSN,
#                                         ''.join([file_name,'.json'])))
#    docid = 'PROXY_AFP_ENG_20020422_0296'
#    docid = 'PROXY_AFP_ENG_20021112_0467'
    docid = 'PROXY_AFP_ENG_20040329_0408'
    amr_table = load_data_pkl(os.path.join(AMR_PILOT_SELECTED_PKL,
                              ''.join([file_name,'.pkl'])))
    doc = amr_table[docid]
    doc = [AMRGraph(sen=doc[k]) for k in sorted(doc.keys())]
    # g = doc[3]
    # print(lines_from_sent(g,3))
#    write_lines(lines_from_doc(doc,3,7),
#                os.path.join(AMR_PILOT_SELECTED_SUBGRAPHS,
#                             ''.join([docid,'.txt'])))
#    save_data_pkl(amr_subgraphs_from_doc(doc,3),
#                  os.path.join(AMR_PILOT_SELECTED_SUBGRAPHS,
#                               ''.join([docid,'.pkl'])))
    subgraphs = load_data_pkl(os.path.join(AMR_PILOT_SELECTED_SUBGRAPHS,
                                           ''.join([docid,'.pkl'])))