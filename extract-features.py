#! /usr/bin/python3

import sys
from os import listdir

from xml.dom.minidom import parse

from deptree import *
#import patterns

# clue verbs
clue_verbs = ['resist', 'demonstrate', 'anticipate', 'interact', 'potentiate', 'result', 'recommend', 'maintain', 'reduce', 'titrate', 'experience', 'associate', 'monitor', 'increase', 'report', 'displace', 'show', 'inhibit', 'exert', 'combine', 'develop', 'warn', 'exercise', 'administer', 'decrease', 'avoid', 'emerge', 'augment', 'enhance', 'metabolize', 'adjust', 'amplify', 'adverse', 'discontinue', 'involve', 'investigate', 'eliminate', 'block', 'ameliorate']
## ------------------- 
## -- Convert a pair of drugs and their context in a feature vector

def extract_features(tree, entities, e1, e2) :
   feats = set()

   # get head token for each gold entity
   tkE1 = tree.get_fragment_head(entities[e1]['start'],entities[e1]['end'])
   tkE2 = tree.get_fragment_head(entities[e2]['start'],entities[e2]['end'])

   if tkE1 is not None and tkE2 is not None:


      # feature: vib= (clue) verb in between
      vib = False
      for tk in range(tkE1 + 1, tkE2):
         if not tree.is_stopword(tk):
            lemma = tree.get_lemma(tk).lower()
            if tree.get_tag(tk) == "VB" and lemma in clue_verbs:
               vib = True
               feats.add("cverb_inbetween="+lemma)
            
      feats.add('vib=' + str(vib))

      # feature: vbe1= (clue) verb before entity 1
      vbe1=False
      for tk in range(tkE1):
         if not tree.is_stopword(tk):
            lemma = tree.get_lemma(tk).lower()
            if tree.get_tag(tk) == "VB" and tree.get_lemma(tk).lower() in clue_verbs:
               vbe1 = True
               feats.add("cverb_before="+lemma)
      feats.add('vbe1=' + str(vbe1))

      # features: 
      #vae2= verb after entity 2 (boolean)
      #cverb_after=
      #
      vae2=False
      for tk in range(tkE2, tree.get_n_nodes()):
         if not tree.is_stopword(tk):
            lemma = tree.get_lemma(tk).lower()
            if tree.get_tag(tk) == "VB" and lemma in clue_verbs:
               vae2 = True
               feats.add("cverb_after="+lemma)
      feats.add('vae2=' + str(vae2))
      



      tk=tkE1+1
      try:
        while (tree.is_stopword(tk)):
          tk += 1
      except:
        return set()
      word  = tree.get_word(tk)
      lemma = tree.get_lemma(tk).lower()
      tag = tree.get_tag(tk)
      feats.add("lib=" + lemma)
      feats.add("wib=" + word)
      feats.add("lpib=" + lemma + "_" + tag)
      
      # feature: eib= entity in between
      eib = False
      for tk in range(tkE1+1, tkE2) :
         if tree.is_entity(tk, entities):
            eib = True 
      feats.add('eib='+ str(eib))

      # features about paths in the tree
      lcs = tree.get_LCS(tkE1,tkE2)
      lcs_word = tree.get_word(lcs)
      lcs_lemma = tree.get_lemma(lcs).lower()
      lcs_tag = tree.get_tag(lcs)
      feats.add("lcs_word=" + lcs_word)
      feats.add("lcs_lemma=" + lcs_lemma)
      feats.add("lcs_tag=" + lcs_tag)
      
      path1 = tree.get_up_path(tkE1,lcs)
      path1 = "<".join([tree.get_lemma(x)+"_"+tree.get_rel(x) for x in path1])
      feats.add("path1="+path1)

      path2 = tree.get_down_path(lcs,tkE2)
      path2 = ">".join([tree.get_lemma(x)+"_"+tree.get_rel(x) for x in path2])
      feats.add("path2="+path2)

      path = path1+"<"+tree.get_lemma(lcs)+"_"+tree.get_rel(lcs)+">"+path2      
      feats.add("path="+path)
      
   return feats


## --------- MAIN PROGRAM ----------- 
## --
## -- Usage:  extract_features targetdir
## --
## -- Extracts feature vectors for DD interaction pairs from all XML files in target-dir
## --

# directory with files to process
datadir = sys.argv[1]

# process each file in directory
for f in listdir(datadir) :

    # parse XML file, obtaining a DOM tree
    tree = parse(datadir+"/"+f)

    # process each sentence in the file
    sentences = tree.getElementsByTagName("sentence")
    for s in sentences :
        sid = s.attributes["id"].value   # get sentence id
        stext = s.attributes["text"].value   # get sentence text
        # load sentence entities
        entities = {}
        ents = s.getElementsByTagName("entity")
        for e in ents :
           id = e.attributes["id"].value
           offs = e.attributes["charOffset"].value.split("-")           
           entities[id] = {'start': int(offs[0]), 'end': int(offs[-1])}

        # there are no entity pairs, skip sentence
        if len(entities) <= 1 : continue

        # analyze sentence
        analysis = deptree(stext)

        # for each pair in the sentence, decide whether it is DDI and its type
        pairs = s.getElementsByTagName("pair")
        for p in pairs:
            # ground truth
            ddi = p.attributes["ddi"].value
            if (ddi=="true") : dditype = p.attributes["type"].value
            else : dditype = "null"
            # target entities
            id_e1 = p.attributes["e1"].value
            id_e2 = p.attributes["e2"].value
            # feature extraction

            feats = extract_features(analysis,entities,id_e1,id_e2) 
            # resulting vector
            if len(feats) != 0:
              print(sid, id_e1, id_e2, dditype, "\t".join(feats), sep="\t")

