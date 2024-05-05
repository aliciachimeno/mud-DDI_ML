#!/usr/bin/env python3

import sys
from sklearn.feature_extraction import DictVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.svm import LinearSVC, SVC
import numpy as np
from xgboost import XGBClassifier
import argparse
from joblib import dump


def load_data(data, allowed_features):
	features = []
	labels = []
	for interaction in data:
		interaction = interaction.strip()
		interaction = interaction.split('\t')
		interaction_dict = {
		feat.split('=')[0]:feat.split('=')[1] for feat in interaction[1:]
		if (feat.split('=')[0] in allowed_features)
		}
		features.append(interaction_dict)
		labels.append(interaction[0])
	return features, labels



if __name__ == '__main__':
	#initial state
	paths = ["path","path2","path1"] 
	eib = ["eib"] 
	add_next_non_stopword = ["lib","wib","lpib"]
	# tkE1 and tkE2 features
	features_tkE1= ["tkE1_word","tkE1_lemma","tkE1_tag"]
	features_tkE2= ["tkE2_word","tkE2_lemma","tkE2_tag"]
	
	# features using tkE1 and tkE2 combined:
	features_combined=["count_tokens_bt","lemma_pair","tag_pair","word_pair"]
	#features about the context
	features_context=["cverb_before","cverb_inbetween","cverb_after","tags_beforeE1","lemmas_beforeE1","tags_afterE2","lemmas_afterE2","before_tagE2","before_lemmaE2","tags_afterE1","lemma_afterE1"]
	
	#lcs features
	features_lcs=["lcs_word","lcs_lemma","lcs_tag"]
	# parent features
	features_parent=["lemma_p1","tag_p1","lemma_p2","tag_p2"]
	allowed_features = features_tkE1 + features_tkE2 + features_combined+features_context+paths+ eib  + add_next_non_stopword +features_lcs+features_parent

	model_file = sys.argv[1]
	vectorizer_file = sys.argv[2] 	

	train_features, y_train = load_data(sys.stdin,allowed_features)
	y_train = np.asarray(y_train)
	classes = np.unique(y_train)

	v = DictVectorizer()
	X_train = v.fit_transform(train_features)

	
	
	#clf = MultinomialNB(alpha=0.01)
	#clf.partial_fit(X_train, y_train, classes)
	'''
	clf = CRF(algorithm='lbfgs', # Choose optimization algorithm, here 'lbfgs' is used
          c1=0.1,             # L1 regularization coefficient
          c2=0.1,             # L2 regularization coefficient
          max_iterations=100, # Maximum number of iterations
          all_possible_transitions=True) # Use all possible transitions between labels

	#clf.fit(X_train, y_train)
	'''
	
	#clf = SVC(kernel='poly', degree=3, probability=True)
	#clf = XGBClassifier()
	clf = SVC(kernel='linear',probability=True)
	clf.fit(X_train, y_train)
	#clf = RandomForestClassifier(n_estimators=100, random_state=42)
	#clf.fit(X_train, y_train)	
	#Save classifier and DictVectorizer
	dump(clf, model_file) 
	dump(v, vectorizer_file)

	 






		


	 
