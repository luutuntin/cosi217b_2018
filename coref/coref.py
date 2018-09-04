# -*- coding: utf-8 -*-
import re
import json


def main(filename):
	f =open(filename,'r')
	data = json.load(f)
	f.close()
	document = data['document']
	clusters = data['clusters']
	corefs = []
	for i in clusters:
		coref = []
		for j in i:
			s = document[slice(j[0],j[1]+1)]
			coref.append(" ".join(s))
		corefs.append(coref)
	for i in corefs:
		print(i)
		print('--------')


if __name__ == '__main__':
	filename = 'output.jsonl'
	main(filename)

