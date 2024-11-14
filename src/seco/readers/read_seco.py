from pathlib import Path

import pandas as pd
from pyphen import Pyphen

from .read_kb_triples import LexicalBase
from .read_morphobr import MorphoBR


def read_seco(filepath: Path, lexical_base: Path = None, morphological_base: Path = None) -> pd.DataFrame:
    df = pd.read_csv(filepath, encoding='utf-8')

    # Get only antonym riddles
    df = df.loc[df['origem'].str.startswith('antonimos-2')]
    df.sort_values(by='potencial_humorstico',
                   ascending=False,
                   inplace=True)

    # Retrieve riddles parts
    if lexical_base is not None and morphological_base is not None:
        df['#Termo'] = df['adivinha'].str.extract(r'(\w+)\?')
        lexbase = LexicalBase.read(lexical_base)
        df['P1'] = df['relacionado_1'].apply(lexbase.antonyms_of)
        df['P2'] = df['relacionado_2'].apply(lexbase.antonyms_of)
        df = df.explode('P1')
        df = df.explode('P2')
        df = df.loc[[x[0] in x[1] for x in zip(df['P1'], df['#Termo'])], :]
        df = df.loc[[x[0] in x[1] for x in zip(df['P2'], df['#Termo'])], :]

        # Remove duplicates (keep larger part)
        df.reset_index(inplace=True)
        df.sort_values(by='P1', inplace=True,
                       key=lambda x: x.str.len())
        df.drop_duplicates('index', keep='last', inplace=True)
        df.sort_values(by='index', inplace=True)
        df.set_index('index', inplace=True)

        # Find if agglutination coincides with a syllable
        dic = Pyphen(lang='pt_PT')
        # triples (P1, P2, Syllables)
        syl_agglu_pos = zip(df['P1'].str.len(),
                            df['#Termo'].str.len() - df['P2'].str.len(),
                            df['#Termo'].apply(dic.positions))
        df['Agglutination in syllable'] = [agglu_p1 in syl_pos or agglu_p2 in syl_pos
                                           for agglu_p1, agglu_p2, syl_pos in syl_agglu_pos]

        # Morphological analysis
        morphbase = MorphoBR.read(morphological_base)
        p1_feats = morphbase.get_feats(df['P1'],
                                       df['P1'],
                                       only_pos=True)
        p2_feats = morphbase.get_feats(df['P2'],
                                       df['P2'],
                                       only_pos=True)
        df['P1 Features'] = p1_feats
        df['P2 Features'] = p2_feats
        df = df.explode('P1 Features')
        df = df.explode('P2 Features')

        # Add relation weights
        df['Relation 1 Weight'] = df.aggregate(lambda x: lexbase.get_weight(x['P1'], x['relacionado_1']),
                                               axis='columns')
        df['Relation 2 Weight'] = df.aggregate(lambda x: lexbase.get_weight(x['P2'], x['relacionado_2']),
                                               axis='columns')
    return df
