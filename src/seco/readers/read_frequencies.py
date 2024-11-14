import logging
import sys
from pathlib import Path
import pandas as pd

logger = logging.getLogger('riddles')


class FrequencyLexicon(object):
    def __init__(self, data):
        self.data = data

    @classmethod
    def read(cls, filepath):
        logger.info(f'Loading file \'{filepath}\'')
        with filepath.open(encoding='utf-8') as file_:
            df = pd.read_csv(file_, sep='\t',
                             names=['Frequency', 'Word'],
                             index_col='Word').squeeze()
        logger.info(f'{df.shape[0]} items loaded')
        logger.info(f'Frequency Lexicon ready')
        return FrequencyLexicon(df)

    def get_frequencies(self, words, smoothing=False):
        '''
        Gets frequencies for the `words` passed. If `smoothing` is false, all words
        not present in the frequency corpus are ignored. If `smoothing` is true,
        a simple smoothing is performed by adding 1 to every word frequency.

        Arguments:
            words: pandas.Series - Words to retrieve frequency
            smoothing: boolean - Wheter to perform smoothing or not
        Return:
            pandas.Series - Words as index and frequency as value
        '''
        words = words.copy()
        words.drop_duplicates(inplace=True)
        has_freq = words.isin(self.data.index)
        words_with_freq = words.loc[has_freq]
        words_freq = self.data[words_with_freq]

        if smoothing:
            words_freq += 1 # Add count
            words_wo_freq = words.loc[~has_freq]
            words_no_freq = pd.Series(1, index=words_wo_freq) # New words with frequency 1
            words_freq = pd.concat([words_freq, words_no_freq])
        return words_freq


if __name__ == '__main__':
    filepath = Path(sys.argv[1])
    reader = FrequencyLexicon.read(filepath)
    print(reader.data)
