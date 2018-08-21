# -*- coding:utf-8
from tuple import subGraph
import pickle
import sys
sys.path.append("../subgraph/")
import amr_reader
# import constant



feature_funcs = []

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




@register
def children2f(data, root):
	data.childrenNum = len(root.next_nodes)
#
# @register
# def pred2f(data, root):
# 	data.pred = (root)

# @register
# def label2f(data, root):
# 	seq = [1 if e.edge_labels in noneCoreLabels else 0 for e in root.next_nodes]
# 	pass

def main():
	global feature_funcs
	with open('./tuple.pkl','rb') as p:
		subGraphs = pickle.load(p)
		for s in subGraphs:
			amr = s.graph
			amr_nodes_acronym, root = amr_reader.amr_reader(amr)
			for f in feature_funcs:
				f(s, root)
	print(subGraphs[:5])
	with open('./data.pkl','wb') as p:
		pickle.dump(subGraphs,p)


if __name__ == '__main__':
	main()