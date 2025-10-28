from xgboost import XGBClassifier

from models.classification.TreeBasedClassifier import TreeBasedClassifier

class XGBC(TreeBasedClassifier):
    def __init__(self, params=None):
        if params:
            super().__init__(XGBClassifier(**params))
        else:
            super().__init__(XGBClassifier(n_estimators=4000, subsample=0.95, random_state=42))
        