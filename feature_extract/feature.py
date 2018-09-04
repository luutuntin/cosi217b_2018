# -*- coding:utf-8
from tuple import subGraph
import pickle
import sys
sys.path.append("../subgraph/")
import amr_reader
import numpy as np
from constants import *
from nltk.stem import WordNetLemmatizer
from functools import partial
# import constant

feature_funcs = []
lemmatizer = partial(WordNetLemmatizer().lemmatize,pos = 'v')



def register(feature_func):
	print('extracting feature: ',feature_func.__name__)
	feature_funcs.append(feature_func)
	return feature_func

@register
def nenum2f(data, root):
	num = 0
	queue = [root]
	while queue:
		head = queue[-1]
		queue.pop()
		if head.is_entity:
			num += 1
		for child in head.next_nodes:
			queue.append(child)
	data.nenum = num


@register
def level2f(data, root):
	max = 1
	data.level = detectLevel(root)


def detectLevel(node):
	if not node.next_nodes:
		return 1
	else:
		return max([1 + detectLevel(e) for e in node.next_nodes])

pred_list = set()

@register
def pred2f(data, root):
	global pred_list
	data.pred = [0]*len(pred_list)
	idx = list(pred_list).index(root.ful_name)
	if idx:
		data.pred[idx] = 1

@register
def children2f(data, root):
	data.childrenNum = len(root.next_nodes)


@register
def TempMod2f(data, root):
	TempModNum = 0
	for w in data.raw_text:
		if lemmatizer(w) in TempMod:
			TempModNum += 1
	data.TempMod = TempModNum

@register
def Say2f(data,root):
	SayTermNum = 0
	for w in data.raw_text.split():
		# print(lemmatizer(w))
		if lemmatizer(w) in SayTerm:
			SayTermNum += 1
	data.SayTerm = SayTermNum

feature_list = []

def find_feature(root):
	global feature_list
	#find structure with one node

	# r = treenode()
	# for c1 in root.next_nodes:
	# 	n1 = treenode()
	# 	r.next_edges.append(c1.edge_label)
	# 	for c2 in c1.next_nodes:
	# 		n2 = treenode()
	# 		n1.next_edges.append(c2.edge_label)
	# 		n1.next_nodes.append(n2)
	# 	r.next_nodes.append(n1)
	# feature_list.append(r)
	s = ""
	for i in root.next_nodes:
		s += i.edge_label
		for j in i.next_nodes:
			s += j.edge_label
	feature_list.append(s)



@register
def tplt2f(data, root):
	global feature_list
	s = ""
	for i in root.next_nodes:
		s += i.edge_label
		for j in i.next_nodes:
			s += j.edge_label
	data.tplt = [0]*len(feature_list)
	if s in feature_list:
		idx = feature_list.index(s)
		data.tplt[idx] = 1





class treenode:
	def __init__(self):
		self.next_edges = [] #label
		self.next_nodes = []		#reference





def main():
	global feature_funcs
	global pred_list
	with open('./tuple.pkl','rb') as p:
		subGraphs = pickle.load(p)

		root_list = []
		# extract feature


		for s in subGraphs:
			amr = s.graph
			amr_nodes_acronym, root = amr_reader.amr_reader(amr)
			root_list.append(root)
			pred_list.add(root.ful_name)
			if s.annotation == 1.0:
				find_feature(root)

		#compute feature
		for i in range(len(subGraphs)):
			s = subGraphs[i]
			root = root_list[i]
			for f in feature_funcs:
				f(s, root)
	
	attrs = [attr for attr in dir(subGraphs[0]) if attr not in dir(subGraph)]
	print(attrs)
	for a in ['graph','articleId','sentenceId','annotation','tplt', 'pred','raw_text']:
		attrs.remove(a)
	traindata = []
	for e in subGraphs:
		lst = [getattr(e,a) for a in attrs] + e.tplt + e.pred + [e.annotation]
		traindata.append(lst)
	traindata = np.array(traindata)
	with open('./traindata.pkl','wb') as p:
		pickle.dump(traindata,p)


if __name__ == '__main__':
	main()