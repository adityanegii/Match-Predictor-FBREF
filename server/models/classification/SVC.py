from sklearn.svm import SVC

from models.classification.LinearClassifierBase import LinearClassifierBase

class SVCWrapper(LinearClassifierBase):
    def __init__(self, params: dict = None, one_vs_rest: bool = False):

        if params:
            model = SVC(**params)
        else:
            model = SVC(kernel='linear', class_weight='balanced', random_state=42)

        super().__init__(model, one_vs_rest)

