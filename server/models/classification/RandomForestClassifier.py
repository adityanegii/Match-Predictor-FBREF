from sklearn.ensemble import RandomForestClassifier

from models.classification.TreeBasedClassifier import TreeBasedClassifier

class RFC(TreeBasedClassifier):
    def __init__(self, params: dict = None):
        if params:
            super().__init__(RandomForestClassifier(**params))
        else:
            super().__init__(RandomForestClassifier(n_estimators=2400, min_samples_split=150, min_samples_leaf=10, class_weight='balanced', random_state=42))
