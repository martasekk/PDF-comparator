class MyersDiff:
    def __init__(self, a=None, b=None):
        self.a = a or []
        self.b = b or []
        self.diffs = []

    def max(self):
        return len(self.a) + len(self.b)

    def compute_diff(self):
        n, m = len(self.a), len(self.b)
        maxd = self.max()
        offset = maxd
        trace = []

        v = [-1] * (2 * maxd + 1)
        v[offset + 1] = 0

        for d in range(maxd + 1):
            trace.append(v.copy())
            for k in range(-d, d + 1, 2):
                if k == -d or (k != d and v[k - 1 + offset] < v[k + 1 + offset]):
                    x = v[k + 1 + offset]
                else:
                    x = v[k - 1 + offset] + 1

                y = x - k

                while x < n and y < m and self.a[x] == self.b[y]:
                    x += 1
                    y += 1

                v[k + offset] = x

                if x >= n and y >= m:
                    return trace, offset
        return trace, offset

    def backtrack(self, trace, offset):
        x, y = len(self.a), len(self.b)
        self.diffs = []

        for d in reversed(range(len(trace))):
            v = trace[d]
            k = x - y

            if k == -d or (k != d and v[k - 1 + offset] < v[k + 1 + offset]):
                prev_k = k + 1
            else:
                prev_k = k - 1

            prev_x = v[prev_k + offset]
            prev_y = prev_x - prev_k

            while x > prev_x and y > prev_y:
                self.diffs.append([x - 1, y - 1, x, y])
                x -= 1
                y -= 1

            if d > 0:
                self.diffs.append([prev_x, prev_y, x, y])

            x, y = prev_x, prev_y

        return self.diffs

    def get_diff(self):
        trace, offset = self.compute_diff()
        if trace:
            return self.backtrack(trace, offset)
        return []

    def get_diff_as_string(self):
        diffs = self.get_diff()
        added, removed = [], []

        for prev_x, prev_y, x, y in reversed(diffs):
            aline = self.a[prev_x] if prev_x < len(self.a) else None
            bline = self.b[prev_y] if prev_y < len(self.b) else None

            if prev_x == x:  # insertion into b
                added.append([prev_y, bline])
            elif prev_y == y:  # deletion from a
                removed.append([prev_x, aline])

        return added, removed

if __name__ == "__main__":
    import myersdiff


    # Example usage
    a = ["line1", "line2", "line3", "line4", "line5", "line6"]
    b = ["line1", "line2 modified", "line4", "line3", "line5"]

    myers = myersdiff.MyersDiff(a, b)
    added, removed = myers.get_diff_as_string()

    print("Added lines:", added)
    print("Removed lines:", removed)