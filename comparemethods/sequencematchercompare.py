from difflib import SequenceMatcher

class SequenceMatcherCompare:
    def __init__(self, left_words, right_words):
        self.left_words = left_words
        self.right_words = right_words

    def get_diff_as_string(self):
        matcher = SequenceMatcher(None, self.left_words, self.right_words)
        added = []
        removed = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'insert':
                for index in range(j1, j2):
                    added.append((index, self.right_words[index]))
            elif tag == 'delete':
                for index in range(i1, i2):
                    removed.append((index, self.left_words[index]))

        return added, removed