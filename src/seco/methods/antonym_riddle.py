import logging
import re

import pandas as pd
from numpy import exp, log

logger = logging.getLogger('riddles')


class AntonymRiddleGenerator(object):
    def __init__(self, agglutlex, freqlex, lexbase, morphbase):
        self.agglutlex = agglutlex
        self.freqlex = freqlex
        self.lexbase = lexbase
        self.morphbase = morphbase

    def get_candidates(self):
        logger.info('Retrieving words with agglutination in syllable')
        agglut_in_syllable = self.agglutlex.data['Agglutination in syllable']
        df = self.agglutlex.data.loc[agglut_in_syllable, :]
        logger.info(f'{df.shape[0]} retrieved')

        logger.info('Removing items whose parts do not have antonyms')
        words_with_antonymy = self.lexbase.words_with_antonymy()
        p1_has_antonym = df['Lema1'].isin(words_with_antonymy)
        p2_has_antonym = df['Lema2'].isin(words_with_antonymy)
        df = df.loc[p1_has_antonym & p2_has_antonym, :]
        logger.info(f'{df.shape[0]} items left')

        logger.info('Keeping only nouns, adjectives, adverbs and verbs')
        words_to_remove = df.loc[~df['P1'].isin(self.morphbase.vocab) |
                                 ~df['P2'].isin(self.morphbase.vocab), :]
        logger.debug(f'Removed the following words\n{words_to_remove}')
        df.drop(index=words_to_remove.index, inplace=True)

        logger.info('Retrieving antonyms')
        p1_antonyms = df['Lema1'].apply(self.lexbase.antonyms_of)
        p2_antonyms = df['Lema2'].apply(self.lexbase.antonyms_of)
        df['P1 Antonyms'] = p1_antonyms
        df['P2 Antonyms'] = p2_antonyms
        logger.debug(f'P1 Antonyms\n{p1_antonyms}')
        logger.debug(f'P2 Antonyms\n{p2_antonyms}')

        # Unpack lists of antonyms in candidates DataFrame
        df = df.explode('P1 Antonyms')
        df = df.explode('P2 Antonyms')
        df.reset_index(drop=True, inplace=True)

        logger.info('Performing morphological analysis')
        p1_feats = self.morphbase.get_feats(df['P1'],
                                            df['Lema1'])
        p2_feats = self.morphbase.get_feats(df['P2'],
                                            df['Lema2'])
        df['P1 Features'] = p1_feats
        df['P2 Features'] = p2_feats
        logger.debug(f'P1 Morphological Features\n{p1_feats}')
        logger.debug(f'P2 Morphological Features\n{p2_feats}')

        # Unpack lists of features in candidates DataFrams
        df = df.explode('P1 Features')
        df = df.explode('P2 Features')
        df.reset_index(drop=True, inplace=True)

        logger.info('Retrieving antonyms lexical forms')
        p1_ant_lex_form = self.morphbase.get_lexical_forms(df['P1 Antonyms'],
                                                           df['P1 Features'])
        p2_ant_lex_form = self.morphbase.get_lexical_forms(df['P2 Antonyms'],
                                                           df['P2 Features'])
        df['P1 Antonym Lexical Form'] = p1_ant_lex_form
        df['P2 Antonym Lexical Form'] = p2_ant_lex_form
        logger.debug(f'P1 Antonyms Lexical Forms\n{p1_ant_lex_form}')
        logger.debug(f'P2 Antonyms Lexical Forms\n{p2_ant_lex_form}')
        logger.debug(f'\n{df}')
        return df

    def filter_candidates_by_rules(self, df):
        logger.info('Filtering candidates through rules')
        adj_re = re.compile(r'^(A)(?:$|\+)')
        adv_re = re.compile(r'^(ADV)(?:$|\+)')
        v_re = re.compile(r'^(V)(?:$|\+)')
        n_re = re.compile(r'^(N)(?:$|\+)')

        p1_adj = df['P1 Features'].str.match(adj_re)
        p1_adv = df['P1 Features'].str.match(adv_re)
        p1_v = df['P1 Features'].str.match(v_re)
        p1_n = df['P1 Features'].str.match(n_re)

        p2_adj = df['P2 Features'].str.match(adj_re)
        p2_adv = df['P2 Features'].str.match(adv_re)
        p2_v = df['P2 Features'].str.match(v_re)
        p2_n = df['P2 Features'].str.match(n_re)

        # Rules
        rules = (p1_adj & p2_adj) | \
            (p1_adj & p2_adv) | \
            (p1_adj & p2_n) | \
            (p1_adv & p2_adj) | \
            (p1_adv & p2_v) | \
            (p1_v & p2_adv) | \
            (p1_v & p2_n) | \
            (p1_n & p2_adj) | \
            (p1_n & p2_v)
        logger.info(f'Removed {df.loc[~rules, :].shape[0]} candidates')
        return df.loc[rules, :]

    def compute_candidate_scores(self, df):
        logger.info('Calculating log probability for candidate words')
        termo_freq = self.freqlex.get_frequencies(df['#Termo'], smoothing=True)
        termo_freq = df['#Termo'].map(termo_freq)
        termo_prob = termo_freq / termo_freq.sum()
        df['#Termo Log Probability'] = log(termo_prob)

        logger.info('Calculating log probability for P1')
        p1_freq = self.freqlex.get_frequencies(df['P1'], smoothing=True)
        p1_freq = df['P1'].map(p1_freq)
        p1_prob = p1_freq / p1_freq.sum()
        df['P1 Log Probability'] = log(p1_prob)

        logger.info('Calculating log probability for P2')
        p2_freq = self.freqlex.get_frequencies(df['P2'], smoothing=True)
        p2_freq = df['P2'].map(p2_freq)
        p2_prob = p2_freq / p2_freq.sum()
        df['P2 Log Probability'] = log(p2_prob)

        logger.info('Calculating and sorting by score')
        df['Score'] = df['#Termo Log Probability'] + \
            df['P1 Log Probability'] + \
            df['P2 Log Probability']
        df.sort_values(by='Score', ascending=False, inplace=True)
        logger.debug(f'\n{df}')
        logger.debug(f'\n{df.describe()}')
        return df

    def generate(self):
        df = self.get_candidates()
        df = self.filter_candidates_by_rules(df)
        df = self.compute_candidate_scores(df)

        return df

        # df = self.compute_candidate_scores(df)
        # logger.info('Retrieving term for riddle')
        # term = candidates.sample(weights=exp(candidates['Score']),
        #                          n=1).squeeze()
        # logger.debug(f'Selected term\n{term}')

        # logger.info('Create combined antonyms using rules')

        # return term, p1_ant_lex_form, p2_ant_lex_form
