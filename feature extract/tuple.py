#	-*- coding:utf-8 -*-
import xlwt
import xlrd
import csv
import re
import pickle

class subGraph():
	def __init__(self, subgraph, articleId, sentenceId, annotation):
		self.subgraph = subgraph
		self.articleId = articleId
		self.sentenceId = sentenceId
		self.annotation = annotation

	def __repr__(self):
		return "{}\t{}\t{}\t{}".format(self.articleId, self.sentenceId, self.subgraph, self.annotation)



def main():
	subgraphFilePath = "../subgraph/amr-release-1.0-training-proxy-subgraph.txt"
	annotationFilePath = "./annotion.xlsx"
	lino = 0
	subGraphs = []

	subgraph = open(subgraphFilePath,'r').read().split('-'*50+'\n')[2:]
	annotation = xlrd.open_workbook(annotationFilePath).sheets()[0]
	try:
		for s in subgraph:
			line = s.split('\n')
			index = re.search("id\s(\S+)\.(\d)",line[0])
			aid = index.group(1)
			sid = index.group(2)
			for i in range(len(line)):
				if line[i].startswith('#'):
					continue
				else:
					break
			sg = '\n'.join(line[i:])
			if not sg:
				continue
			sg = sg.split('\n\n')[:-1]


			for e in sg:
				r = re.search("\((\d)\)",e)
				if not r:
					print('sb')
				ind = int(r.group(1)) 	# a integer
				graph = e[r.end(1)+1:]

				while(annotation.row(lino)[1].value != aid+'.'+sid):
					#print(annotation.row(lino)[1].value)
					lino += 1

				i = 1
				while(ind != annotation.row(lino+i)[2].value):
					#print(annotation.row(lino+i)[2].value)
					i += 1

				if annotation.row(lino+i)[3].value == 'y' or annotation.row(lino+i)[3].value == 'yes':
					y = 1.0
				else:
					y = 0.0

				subGraphs.append(subGraph(aid,sid,graph,y))
	except IndexError:
		pass
	print(subGraphs)
	with open('./tuple.pkl','w') as p:
		pickle.dump(subGraphs,p)

if __name__ == '__main__':
	main()


