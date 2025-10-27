from sklearn.linear_model import LogisticRegression

from models.classification.LinearClassifierBase import LinearClassifierBase

class LRWrapper(LinearClassifierBase):
    def __init__(self, params=None, one_vs_rest=False):
        
        if params:
            model = LogisticRegression(**params)
        else:
            model = LogisticRegression(max_iter=1000, class_weight='balanced',random_state=42)

        super().__init__(model, one_vs_rest)
    