# -*- coding:utf
from sklearn import svm
from sklearn.decomposition import PCA, CCA
from math import *
import array
import sys
import pickle
sys.path.append('../feature_extract')
from tuple import subGraph
from sklearn.model_selection import KFold, cross_val_score

def train():
	with open('../feature_extract/traindata.pkl','rb') as p:
		data = pickle.load(p)
	X = data[:,:-1]
	X = PCA(n_components=20).fit_transform(X)
	y = data[:,-1:]

	clf = svm.SVC(kernel = 'rbf')

	l = len(X)
	s = floor(0.8*l)

	X_train = X[:s]
	X_test = X[s:]
	y_train = y[:s]
	y_test = y[s:]

	p = clf.fit(X_train,y_train).predict(X_test)
	print(len(X))

	TP = sum([int(p[i] == y_test[i]) for i in range(len(y_test)) if p[i] == 1])
	FP = sum(p) - TP
	TN = sum([int(p[i] == y_test[i]) for i in range(len(y_test)) if p[i] == 0])
	FN = len(p) - sum(p) - TN
	P = TP / (TP + FP)
	R = TP / (TP + FN)
	F = 2*P*R/(P+R)

	print('Precision:',P)
	print('Recall:', R)
	print('F-measure:', F)




	with open('./classifier.pickle','wb') as p:
		pickle.dump(clf, p)
	# k_fold = KFold(n_splits = 10)

	
	# score = cross_val_score(clf, X, y, cv = 10)
	# print('rbf:\n', score)	


if __name__ == '__main__':
	train()