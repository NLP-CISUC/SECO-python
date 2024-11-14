import logging
from pathlib import Path
import sys
import pyphen
import pandas as pd


logger = logging.getLogger('riddles')


class AgglutLex(object):
    '''
    Class that represents an agglutination Lexicon.
    An agglutination in when a word whose string comprehends two
    other meaningful words as substrings.
    '''

    def __init__(self, data):
        self.data = data

    @classmethod
    def read(cls, filepath):
        '''
        Read a TSV file. The file should contain 5 columns:
            #Termo - Whole agglutinated word
            P1 - First subword
            P2 - Second subword
            Lema1 - Lemma of the first subword
            Lema2 - Lemma of the second subword

        The words are processed as being written in European Portuguese.
        '''
        logger.info(f'Loading file \'{filepath}\'')
        with filepath.open(encoding='utf-8') as file_:
            df = pd.read_csv(file_, sep='\t')
        logger.info(f'{df.shape[0]} words loaded')

        # Find if agglutination coincides with a syllable
        logger.info('Processing syllables')
        dic = pyphen.Pyphen(lang='pt_PT')
        # triples (P1, P2, syllables)
        syl_agglu_pos = zip(df['P1'].str.len(),
                            df['Termo#'].str.len() - df['P2'].str.len(),
                            df['Termo#'].apply(dic.positions))
        df['Agglutination in syllable'] = [agglu_p1 in syl_pos or agglu_p2 in syl_pos
                                           for agglu_p1, agglu_p2, syl_pos in syl_agglu_pos]
        logger.info('Agglutination Lexicon ready')
        return AgglutLex(df)

    def filter_words(self, words):
        indices = self.data['#Termo'].isin(words)
        return self.data.loc[indices, :]


if __name__ == '__main__':
    filepath = Path(sys.argv[1])
    reader = AgglutLex.read(filepath)
    print(reader.data)
