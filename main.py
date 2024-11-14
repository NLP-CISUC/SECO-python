import logging
from argparse import ArgumentParser
from pathlib import Path

from seco.methods.antonym_riddle import AntonymRiddleGenerator
from seco.readers.read_agglutlex import AgglutLex
from seco.readers.read_frequencies import FrequencyLexicon
from seco.readers.read_kb_triples import LexicalBase
from seco.readers.read_morphobr import MorphoBR

if __name__ == '__main__':
    parser = ArgumentParser('Antonym riddle generator')
    parser.add_argument('--agglutination_lexicon',
                        '-a', help='Agglutination Lexicon file',
                        type=Path, required=True)
    parser.add_argument('--frequency_lexicon',
                        '-f', help='Frequency Lexicon file',
                        type=Path, required=True)
    parser.add_argument('--lexical_base',
                        '-l', help='Lexical Base triples file',
                        type=Path, required=True)
    parser.add_argument('--morphological_base',
                        '-m', help='MorphoBR directory path',
                        type=Path, required=True)
    parser.add_argument('--verbose', '-v',
                        action='count',
                        help='Verbose level',
                        default=0, required=False)
    args = parser.parse_args()

    # Configure logger
    logger = logging.getLogger('riddles')
    ch = logging.StreamHandler()
    if args.verbose == 1:
        logger.setLevel(logging.INFO)
        ch.setLevel(logging.INFO)
    elif args.verbose >= 1:
        logger.setLevel(logging.DEBUG)
        ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    agglutlex = AgglutLex.read(args.agglutination_lexicon)
    freqlex = FrequencyLexicon.read(args.frequency_lexicon)
    lexbase = LexicalBase.read(args.lexical_base)
    morphobr = MorphoBR.read(args.morphological_base)

    generator = AntonymRiddleGenerator(agglutlex, freqlex, lexbase, morphobr)
    riddles = generator.generate()
    with Path('results.json').open('w', encoding='utf-8') as file_:
        riddles.to_json(file_,
                        orient='records',
                        indent=4,
                        force_ascii=False)
    # print(f'Qual o contrário de {term["#Termo"]}? {antonym1} {antonym2}.')
