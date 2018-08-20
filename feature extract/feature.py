# -*- coding:utf-8
from tuple import subGraph
import pickle
import sys
sys.path.append("../")
from subgraph import *
from subgraph import 

feature_funcs = []

def register(feature_func):
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
	current = root
	while current.next_nodes:
		for child in current.next_nodes:
			current = child
			level += 1
			if level > max:
				max = level



@register
def children2f(data, root):
	data.childrenNum = len(root.next_nodes)

@register
def pred2f(data, root):
	data.pred = one_hot(root)

@register
def label2f(data, root):
	pass


def main():
	global feature_funcs
	with open('./tuple.pkl','rb') as p:
		subGraphs = pickle.load(p)
		for s in subGraphs:
			amr = s.graph
			amr_nodes_acronym, root = amr_reader.amr_reader(amr)
			for f in feature_funcs:
				f(s, root)
	with open('./data.pkl','w') as p:
		pickle.dump(subGraphs,p)


if __name__ == '__main__':
	main()