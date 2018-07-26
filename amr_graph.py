#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function, with_statement

"""
cosi217b- AMR2KB
alexluu@brandeis.edu
Python 3.4

Quote consideration
"""

from amr_reader.src.reader import get_amr_table_path
import networkx as nx
import re
from constants import *
from utils import *
import os

def amr_node_str(n):    # n: amr node (define in amr-reader package)
    """ -> '[variable] / [concept]'|'[variable] / [entity] - [entity name]' """    
    output = ' / '.join([n.name,n.ful_name])
    if n.is_entity:
        output = ' - '.join([output,n.entity_name])
    return output

def amr_graph_str(g):   # g: AMRGraph object
    """ -> string representation of an AMRGraph object """
    amr_root = list(g.successors('@'))[0]
    # root concept line
    output = '{}\n'.format(amr_node_str(g.node[amr_root]['content']))
    # dfs: depth first search
    dfs_nodes = list(nx.dfs_preorder_nodes(g, amr_root))[1:]
    dfs_edges = nx.dfs_edges(g, amr_root)
    # lines of other concepts
    for (node, edge) in zip(dfs_nodes,dfs_edges):
        node_depth = nx.shortest_path_length(g,'@',node)
        # indent
        output += '\t'*(node_depth-1)
        # relation
        output += '{}     '.format(nx.get_edge_attributes(g,'label')\
                                                         [(edge[0],edge[1],0)])
        # concept
        output += amr_node_str(g.node[node]['content'])
        # empty line - graph separator
        output += '\n'
    return output

# https://github.com/luutuntin/Cinderella/blob/master/semaland_amr_graph.py
class AMRGraph(nx.MultiDiGraph):
    """
    Interested operations: graph union, vertex identification
    Add node/edge attributes: entry id, frequency
    """
    def __init__(self, data=None, sen=None, quote=False):
        super(AMRGraph, self).__init__(data)
        self.quote = quote
        self.id = ''
        self.text = ''
        self.meta = ''
        if sen!=None:
            self.id = sen.sentid
            self.text = sen.sent
            self.meta = sen.comments
            # build the graph using sen.amr_nodes and sen.graph
            nodes = set()
            for e in sen.graph:
                self.add_edge(e[0], e[1], label=str(e[2]))
                nodes.add(e[0])
                nodes.add(e[1])
            for n in nodes:
                if n != '@':
                    self.node[n]['content'] = sen.amr_nodes[n]
    def __str__(self):
        return amr_graph_str(self)

def get_edges_by_direction(g,n,e_di):
    # g: AMR graph, n: node, e_di: 'in'/'out'
    """ -> incoming/outgoing edges of node in graph """
    if e_di=='in':
        return g.in_edges(n,data=True)
    elif e_di=='out':
        return g.out_edges(n,data=True)
    else:
        print('Invalid e_di info!')
        return None
        
def check_edge_label(g,n,e_di,l_re):
    # g: AMR graph, n: node, e_di: 'in'/'out', l_re: label pattern
    """ -> True/False (whether there is an edge matching l_re) """
    edges = get_edges_by_direction(g,n,e_di)
    if not edges:
        return None
    else:
        for e in edges:
            if 'label' in e[2]: # e[2] is dict of edge attribute
                if re.match(l_re,e[2]['label']):
                    return True
    return False

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
#    g = doc[3]