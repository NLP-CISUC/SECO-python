import logging
from re import match
import sys
from itertools import product
from pathlib import Path

import pandas as pd

logger = logging.getLogger('riddles')


class MorphoBR(object):
    def __init__(self, data):
        self.word_to_feat = data
        self.feat_to_word = {(l, f): w for (w, l) in data
                             for f in data[(w, l)]}
        self.vocab = {w for (w, _) in data}

    @classmethod
    def read(cls, dirpath):
        logger.info(f'Loading MorphoBR from directory {dirpath}')
        folders = ['adjectives', 'adverbs',
                   'nouns', 'verbs']
        morphology_dict = dict()
        for folder in dirpath.iterdir():
            if folder.name in folders:
                for filepath in folder.iterdir():
                    with filepath.open('rU', encoding='utf-8') as file_:
                        for line in file_:
                            word, features = line.rstrip().split('\t')
                            split_feats = features.split('+')
                            lemma = split_feats[0]
                            feats = '+'.join(split_feats[1:])

                            if (word, lemma) not in morphology_dict:
                                morphology_dict[(word, lemma)] = set()
                            morphology_dict[(word, lemma)].add(feats)
        logger.info(f'Loaded {len(morphology_dict)} words')
        return cls(morphology_dict)

    def get_feats(self, words, lemmas, only_pos=False):
        def mapping(value):
            return_value = set()
            if value in self.word_to_feat:
                return_value = self.word_to_feat[value]
                if only_pos:
                    return_value = {match(r'(\w+)(?:\+|$)', f).group(1)
                                    for f in return_value}
            return return_value
        tuples = pd.Series(zip(words, lemmas), index=words.index)
        feats = tuples.map(mapping)
        return feats

    # def get_lexical_forms(self, lemmas, features):
    #     forms = list()
    #     used_features = list()
    #     for lemma, feats in zip(lemmas, features):
    #         frs = list()
    #         fts = list()
    #         for t in product(lemma, feats):
    #             if t in self.feat_to_word:
    #                 frs.append(self.feat_to_word[t])
    #                 fts.append(t[1])
    #         if frs:
    #             forms.append(frs)
    #             used_features.append(fts)
    #         else:
    #             # No lexical form found, use the lemma
    #             forms.append(lemma)
    #             used_features.append(feats)
    #     return pd.Series(forms, index=lemmas.index), pd.Series(used_features, index=lemmas.index)

    def get_lexical_forms(self, lemmas, features):
        def mapping(value):
            if value in self.feat_to_word:
                return self.feat_to_word[value]
            return value[0]  # No lexical form found, use lemma
        tuples = pd.Series(zip(lemmas, features))
        return tuples.map(mapping)


if __name__ == '__main__':
    dirpath = Path(sys.argv[1])
    morphobr = MorphoBR.read(dirpath)
    words = pd.Series(['mal', 'despe', 'revi', 'kjfj'])
    lemmas = pd.Series(['mal', 'despir', 'rever', 'kjfj'])
    feats = morphobr.get_feats(words, lemmas)
    print(feats)
    antonyms = pd.Series([['bem'], ['vestir'], ['esquecer'], ['kjfj']])
    lex_form = morphobr.get_lexical_forms(antonyms, feats)
    print(lex_form)
