import logging
import sys
from pathlib import Path

import pandas as pd

logger = logging.getLogger('riddles')
antonymy_relations = ['ANTONIMO_V_DE',
                      'ANTONIMO_N_DE',
                      'ANTONIMO_ADJ_DE',
                      'ANTONIMO_ADV_DE']


class LexicalBase(object):
    def __init__(self, data: pd.DataFrame) -> None:
        self.data = data

    @classmethod
    def read(cls, filepath: Path) -> 'LexicalBase':
        logger.info(f'Loading file \'{filepath}\'')
        with filepath.open(encoding='utf-8') as file_:
            df = pd.read_csv(file_, sep='\t',
                             names=['Triple', 'Resources'])
            final_df = pd.DataFrame(df['Triple'].str.split(' ').to_list(),
                                    columns=['Word 1', 'Relation', 'Word 2'])
            final_df['Resources'] = df['Resources']
        logger.info(f'{final_df.shape[0]} items loaded')
        logger.info(f'Lexical Base ready')
        return LexicalBase(final_df)

    def words_with_antonymy(self) -> pd.Series:
        is_antonymy = self.data['Relation'].isin(antonymy_relations)
        words_with_antonymy = self.data.loc[is_antonymy, 'Word 2'].unique()
        return words_with_antonymy

    def antonyms_of(self, word: str) -> set:
        is_antonymy = self.data['Relation'].isin(antonymy_relations)
        is_word_1 = self.data['Word 1'] == word
        is_word_2 = self.data['Word 2'] == word

        word_1_ant = self.data.loc[is_antonymy & is_word_1, 'Word 2'].to_list()
        word_2_ant = self.data.loc[is_antonymy & is_word_2, 'Word 1'].to_list()
        return set(word_1_ant + word_2_ant)

    def get_weight(self, word1: str, word2: str) -> int:
        is_antonymy = self.data['Relation'].isin(antonymy_relations)
        is_word_11 = self.data['Word 1'] == word1
        is_word_12 = self.data['Word 2'] == word1
        is_word_21 = self.data['Word 1'] == word2
        is_word_22 = self.data['Word 2'] == word2

        rel_word12 = self.data.loc[is_antonymy &
                                   is_word_11 &
                                   is_word_22, 'Resources']
        rel_word21 = self.data.loc[is_antonymy &
                                   is_word_21 &
                                   is_word_12, 'Resources']

        return_value = 0
        if not rel_word12.empty:
            return_value = max(rel_word12.to_list())
        if not rel_word21.empty:
            return_value = max(rel_word21.to_list())
        return return_value


if __name__ == '__main__':
    filepath = Path(sys.argv[1])
    reader = LexicalBase.read(filepath)
    print(reader.data)
    print(reader.antonyms_of('rever'))
    print(reader.antonyms_of('são'))
    print(reader.get_weight('são', 'insano'))
