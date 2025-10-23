from deepdiff import DeepDiff

class DeepDiffCompare:
    def __init__(self, left_words, right_words):
        self.left_words = left_words
        self.right_words = right_words

    def get_diff_as_string(self):
        diff = DeepDiff(self.left_words, self.right_words, ignore_order= True)
        added = []
        removed = []

        if 'iterable_item_added' in diff:
            for path, value in diff['iterable_item_added'].items():
                index = int(path.split('[')[-1].rstrip(']'))
                added.append([index, value])

        if 'iterable_item_removed' in diff:
            for path, value in diff['iterable_item_removed'].items():
                index = int(path.split('[')[-1].rstrip(']'))
                removed.append([index, value])
        print("DeepDiffCompare module loaded successfully.")

        return added, removed
    
    