from .model import ThreatModel

class Predictor:
    def __init__(self):
        self.model = ThreatModel()

    def predict(self, features):
        return self.model.predict(features)
