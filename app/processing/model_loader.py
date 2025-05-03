import os

# For Scikit-learn models
import joblib

# For Keras models
from tensorflow.keras.models import load_model as keras_load_model


class ModelLoader:
    def __init__(self, model_path, model_type="keras"):
        self.model_path = model_path
        self.model_type = model_type.lower()
        self.model = self._load()

    def _load(self):
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found: {self.model_path}")

        if self.model_type == "keras":
            return keras_load_model(self.model_path)
        elif self.model_type == "sklearn":
            return joblib.load(self.model_path)
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")

    def get_model(self):
        return self.model
