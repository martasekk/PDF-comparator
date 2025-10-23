from Bio.Align import PairwiseAligner

class HirschbergCompare:
    def __init__(self, left_words, right_words):
        self.left_words = left_words
        self.right_words = right_words

    def get_diff_as_string(self):
        aligner = PairwiseAligner()
        aligner.mode = "global"

        # Convert list of words into strings
        seq_left = " ".join(self.left_words)
        seq_right = " ".join(self.right_words)

        alignments = aligner.align(seq_left, seq_right)
        aligned = alignments[0]

        # We can’t directly get word-level indices from char alignment,
        # so split back to words and diff manually.
        added, removed = [], []
        left_index, right_index = 0, 0

        left_words = self.left_words
        right_words = self.right_words

        # Simple manual diff logic
        while left_index < len(left_words) and right_index < len(right_words):
            if left_words[left_index] == right_words[right_index]:
                left_index += 1
                right_index += 1
            else:
                # word mismatch: check which side differs
                if right_words[right_index] not in left_words[left_index:]:
                    added.append((right_index, right_words[right_index]))
                    right_index += 1
                elif left_words[left_index] not in right_words[right_index:]:
                    removed.append((left_index, left_words[left_index]))
                    left_index += 1
                else:
                    left_index += 1
                    right_index += 1

        # catch tail ends
        while left_index < len(left_words):
            removed.append((left_index, left_words[left_index]))
            left_index += 1
        while right_index < len(right_words):
            added.append((right_index, right_words[right_index]))
            right_index += 1

        return added, removed
