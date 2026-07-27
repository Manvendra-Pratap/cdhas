import math
import random
from typing import List

class IsolationTree:
    def __init__(self, feature_idx: int = -1, split_value: float = 0.0, left=None, right=None, size: int = 0):
        self.feature_idx = feature_idx
        self.split_value = split_value
        self.left = left
        self.right = right
        self.size = size

def c_factor(n: int) -> float:
    if n <= 1:
        return 0.0
    if n == 2:
        return 1.0
    return 2.0 * (math.log(n - 1) + 0.5772156649) - (2.0 * (n - 1) / n)

class IsolationForestEngine:
    def __init__(self, n_estimators: int = 50, max_samples: int = 256):
        self.n_estimators = n_estimators
        self.max_samples = max_samples
        self.trees: List[IsolationTree] = []

    def fit(self, X: List[List[float]]):
        if not X:
            return
        n_samples = len(X)
        sample_size = min(self.max_samples, n_samples)
        max_depth = int(math.ceil(math.log2(max(sample_size, 2))))

        self.trees = []
        random.seed(42)

        for _ in range(self.n_estimators):
            subsample = random.sample(X, sample_size)
            tree = self._build_tree(subsample, 0, max_depth)
            self.trees.append(tree)

    def _build_tree(self, X: List[List[float]], current_depth: int, max_depth: int) -> IsolationTree:
        n_samples = len(X)
        if current_depth >= max_depth or n_samples <= 1:
            return IsolationTree(size=n_samples)

        n_features = len(X[0])
        feature_idx = random.randint(0, n_features - 1)
        values = [x[feature_idx] for x in X]
        min_val, max_val = min(values), max(values)

        if min_val == max_val:
            return IsolationTree(size=n_samples)

        split_value = random.uniform(min_val, max_val)
        left_X = [x for x in X if x[feature_idx] < split_value]
        right_X = [x for x in X if x[feature_idx] >= split_value]

        left_node = self._build_tree(left_X, current_depth + 1, max_depth)
        right_node = self._build_tree(right_X, current_depth + 1, max_depth)

        return IsolationTree(feature_idx=feature_idx, split_value=split_value, left=left_node, right=right_node)

    def path_length(self, x: List[float], tree: IsolationTree, current_depth: int) -> float:
        if tree.left is None or tree.right is None or tree.feature_idx == -1:
            return current_depth + c_factor(tree.size)
        if x[tree.feature_idx] < tree.split_value:
            return self.path_length(x, tree.left, current_depth + 1)
        else:
            return self.path_length(x, tree.right, current_depth + 1)

    def compute_anomaly_score(self, x: List[float], n_total_samples: int) -> float:
        if not self.trees or n_total_samples <= 1:
            return 0.5
        avg_path_length = sum(self.path_length(x, tree, 0) for tree in self.trees) / len(self.trees)
        c = c_factor(n_total_samples)
        if c == 0:
            return 0.5
        score = 2.0 ** (- (avg_path_length / c))
        return min(1.0, max(0.0, round(score, 3)))
