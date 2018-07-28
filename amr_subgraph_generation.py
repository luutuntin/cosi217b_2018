#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function, with_statement

"""
cosi217b- AMR2KB
alexluu@brandeis.edu
Python 3.4

References:
https://stackoverflow.com/questions/22180410/how-can-i-extract-all-possible-induced-subgraphs-from-a-given-graph-with-network
"""

from amr_reader.src.reader import get_amr_table_path
import networkx as nx
from constants import *
from utils import *
import os
import itertools
from collections import defaultdict

from amr_graph import amr_graph_str, AMRGraph
import time

# g: AMR graph object; n: node label
def get_connected_node_combinations(g,n,output):
    """ -> updated output by adding the content of output[n] """
    #https://stackoverflow.com/questions/2831212/python-sets-vs-lists
    # ||https://stackoverflow.com/questions/5931291/how-can-i-create-a-set-of-sets-in-python  
    output[n]=set()
    #https://stackoverflow.com/questions/661603/how-do-i-know-if-a-generator-is--from-the-start
    successors = list(g.successors(n))    
    if successors:
        # store intermediate info for dynamic programming algorithm
        temp = defaultdict(dict) 
        for span in range(1,len(successors)+1):
            # print('span = ',span)
            # print(temp)
            if span==1:
                for i in range(len(successors)):
                    # https://docs.python.org/3.5/library/stdtypes.html#set-types-set-frozenset
                    temp[span][i] = {frozenset({successors[i]})}
                    if output[successors[i]]:
                        temp[span][i] = temp[span][i].union\
                                        (set(x.union({successors[i]}) 
                                             for x in output[successors[i]]))
            else:
                for i in range(len(successors)-span+1):
                    for j in range(i+1,len(successors)-span+2):
                        # print(temp[1][i])
                        # print(temp[span-1][j])
                        temp[span][i]=set(x.union(y)
                                          for x in temp[1][i]
                                          for y in temp[span-1][j])
        # print(temp)
        for span in temp:
            for i in temp[span]:
                output[n] = output[n].union(temp[span][i])
    return output

# https://networkx.github.io/documentation/stable/reference/classes/multidigraph.html
# g: AMRGraph object; nodes: iterable container of nodes in g
# root_node is optional and, if given as input, does not belong to nodes
def construct_amr_subgraph(g,nodes,root_node=None): 
    """ Add dummy root node '@', apply AMRGraph type """
    if root_node:
        output = g.subgraph(nodes.union({root_node})).copy()
    else:
        output = g.subgraph(nodes).copy()
        # assumption: nx.is_directed_acyclic_graph(output)==True
        root_node = list(nx.topological_sort(output))[0]
    output.add_edge('@',root_node,label='')
    output = AMRGraph(output)
    output.meta = '# root node: {}'.format(root_node)
    return output

def get_ne_nodes(g):
    """ -> set of named entity nodes """
    return set(n for n in g if n!='@' and g.node[n]['content'].is_entity)
    
def check_ne_presence(g,ne_nodes,nodes):
    """check if there is any ne node in nodes """
    output = False
    for n in ne_nodes:
        if n in nodes:
            output = True
            break
    return output

#https://networkx.github.io/documentation/stable/reference/algorithms/dag.html
#https://networkx.github.io/documentation/stable/reference/algorithms/traversal.html
def extract_all_subgraphs(g): # g: AMRGraph object
    """ """
    output = defaultdict(list)
    if not nx.is_directed_acyclic_graph(g):
        print('The input graph is not directed acyclic.')
        return output

    ne_nodes = get_ne_nodes(g)
    if not ne_nodes:
        print('There is no named entity in the input graph.')
        return output
    
    #amr_root = list(g.successors('@'))[0]
    #order = list(nx.dfs_postorder_nodes(g, amr_root))
    order = list(nx.dfs_postorder_nodes(g))[:-1]
    #order = list(reversed(list(nx.topological_sort(g))))[:-1]
    # cnc: conntect node combinations
    cnc = defaultdict(set)
    for n in order:
        cnc = get_connected_node_combinations(g,n,cnc)
    for n in order:
        output[n] = [construct_amr_subgraph(g,nodes,n) 
                     for nodes in cnc[n]
                     if g.node[n]['content'].is_entity
                        or check_ne_presence(g,ne_nodes,nodes)]
    return output


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

# def lines_from_sent(g,n_min=1,n_max=None): # g: AMRGraph object
def lines_from_sent(g): # g: AMRGraph object
    """ -> list of string lines of subgraphs of one sentence graph """
    lines = []
#    sgs = amr_subgraphs(g,num)
    # sgs = amr_subgraphs_optimized(g,n_min,n_max)
    sgs = extract_all_subgraphs(g)
    for k in sgs:
        if sgs[k]:
            # lines.append('#connected subgraphs of {} nodes'.format(k))
            lines.append('# root node: {}'.format(k))
            for x in sgs[k]:
                lines.extend(amr_graph_str(x).split('\n'))
    return lines

# def lines_from_doc(doc,n_min=1,n_max=None):    # doc: list of AMRGraph objects
def lines_from_doc(doc):    # doc: list of AMRGraph objects
    """ -> list of string lines of subgraphs of graphs in one document """
    lines = []
    for g in doc:
        print(g.id)
        lines.extend(g.meta.split('\n'))
        # lines.extend(lines_from_sent(g,n_min,n_max))
        lines.extend(lines_from_sent(g))
    return lines
        

# def lines_from_docs(docs,n_min=1,n_max=None):  # docs: amr_table
def lines_from_docs(docs):  # docs: amr_table
    """ -> list of string lines of subgraphs of graphs in all documents """
    lines = []
    for k in docs:
        print(k)
        lines.append('# {}'.format(k))
        doc = [AMRGraph(sen=docs[k][kk]) for kk in sorted(docs[k].keys())]
        # lines.extend(lines_from_doc(doc,n_min,n_max))
        lines.extend(lines_from_doc(doc))
    # return [sgs ]
    return lines

# def amr_subgraphs_from_doc(doc,n_min=1,n_max=None):    # doc: list of AMRGraph objects
def amr_subgraphs_from_doc(doc):    # doc: list of AMRGraph objects
    """ -> list of string lines of subgraphs of graphs in one document """    
    # return [amr_subgraphs_optimized(g,n_min,n_max) for g in doc]
    return [extract_all_subgraphs(g) for g in doc]
        

# def amr_subgraphs_from_docs(docs,n_min=1,n_max=None):  # docs: amr_table
def amr_subgraphs_from_docs(docs,n_min=1,n_max=None):  # docs: amr_table
    """ -> list of string lines of subgraphs of graphs in all documents """
    output = dict()
    for k in docs:        
        doc = [AMRGraph(sen=docs[k][kk]) for kk in sorted(docs[k].keys())]
        # output[k] = amr_subgraphs_from_doc(doc,n_min,n_max)
        output[k] = amr_subgraphs_from_doc(doc)
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
    # docid = 'PROXY_AFP_ENG_20020422_0296'
    # docid = 'PROXY_AFP_ENG_20021112_0467'
    docid = 'PROXY_AFP_ENG_20040329_0408'
    amr_table = load_data_pkl(os.path.join(AMR_PILOT_SELECTED_PKL,
                              ''.join([file_name,'.pkl'])))
    doc = amr_table[docid]
    doc = [AMRGraph(sen=doc[k]) for k in sorted(doc.keys())]
    # g = doc[4]
    # print(g)
    # print(lines_from_sent(g,3))
    ti = time.time()
    print('Subgraph generation - START')
    # for line in lines_from_sent(g):
        # print(line)
    
#    write_lines(lines_from_doc(doc,3,7),
    # write_lines(lines_from_doc(doc),
                # os.path.join(AMR_PILOT_SELECTED_SUBGRAPHS,
                            #  ''.join([docid,'_20180728.txt'])))
    # save_data_pkl(amr_subgraphs_from_doc(doc,3),
    save_data_pkl(amr_subgraphs_from_doc(doc),
                  os.path.join(AMR_PILOT_SELECTED_SUBGRAPHS,
                               ''.join([docid,'_20180728.pkl'])))
    # subgraphs = load_data_pkl(os.path.join(AMR_PILOT_SELECTED_SUBGRAPHS,
                                        #    ''.join([docid,'.pkl'])))
    print('Subgraph generation - END')
    print(str(time.time() - ti))            