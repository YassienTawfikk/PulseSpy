import numpy as np
from app.processing.model_loader import ModelLoader


class ECGClassifier:
    def __init__(self, model_path, model_type="keras", label_map=None):
        self.model = ModelLoader(model_path, model_type).get_model()
        self.label_map = label_map or {0: "Normal", 1: "AFib", 2: "PVC"}

    def predict(self, ecg_signal):
        """
        Takes a NumPy array of ECG signal data and returns prediction label.
        Assumes 1D ECG signal (reshaped internally).
        """
        # Ensure proper input shape: (1, length, 1) for CNN, or (1, length) for MLP
        signal = np.array(ecg_signal)
        if len(signal.shape) == 1:
            signal = signal.reshape(1, -1, 1)  # CNN style
        elif len(signal.shape) == 2:
            signal = signal.reshape(1, *signal.shape)

        # Make prediction
        pred = self.model.predict(signal)
        predicted_index = np.argmax(pred, axis=1)[0]

        return self.label_map.get(predicted_index, f"Unknown ({predicted_index})")
