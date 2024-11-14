from pathlib import Path
from sys import argv


class LIWC(object):
    def __init__(self, tags, words) -> None:
        self.id2tags = tags
        self.tags2id = {tags[id_]: id_ for id_ in tags}
        self.words = words

    @classmethod
    def read(cls, filepath: Path) -> 'LIWC':
        id2tags = dict()
        word2id = dict()
        with filepath.open('rU', encoding='utf-8') as file_:
            mode = None
            for line in file_:
                strip_line = line.rstrip()
                if strip_line == '%' and mode is None:
                    mode = 'id2tags'
                elif strip_line == '%' and mode == 'id2tags':
                    mode = 'word2id'
                elif mode == 'id2tags':
                    id_, tag = strip_line.split('\t')
                    id2tags[int(id_)] = tag
                elif mode == 'word2id':
                    word_tags = strip_line.split('\t')
                    word = word_tags[0]
                    tags = [int(t) for t in word_tags[1:]]
                    word2id[word] = tags
        return LIWC(id2tags, word2id)

    def get_tags(self, word):
        if word in self.words:
            return [self.id2tags[t] for t in self.words[word]]
        else:
            return None


if __name__ == '__main__':
    filepath = Path(argv[1])
    liwc = LIWC.read(filepath)
    print(liwc.id2tags)
    print(liwc.tags2id)
