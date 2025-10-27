from abc import ABC, abstractmethod
import pandas as pd

class ClassifierBase(ABC):
    @abstractmethod
    def train(self, data: pd.DataFrame, features: list) -> None:
        """Train the model with the provided data and features."""
        pass

    @abstractmethod
    def predict(self, data: pd.DataFrame, features: list) -> pd.DataFrame:
        """Make predictions using the trained model."""
        pass

    @abstractmethod
    def evaluate_model(self, data: pd.DataFrame, features: list) -> pd.DataFrame:
        """Evaluate the model's performance."""
        pass