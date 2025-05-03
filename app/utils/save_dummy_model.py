# save_dummy_model.py

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, MaxPooling1D, Flatten, Dense, Input
import os

# Create a basic 1D CNN model for ECG classification
model = Sequential([
    Input(shape=(250, 1)),  # each ECG beat is 250 samples
    Conv1D(32, kernel_size=5, activation='relu'),
    MaxPooling1D(pool_size=2),
    Flatten(),
    Dense(16, activation='relu'),
    Dense(3, activation='softmax')  # 3 fake output classes (Normal, AFib, Other)
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Ensure models directory exists
os.makedirs("../../models", exist_ok=True)

# Save the model
model.save("models/arrhythmia_model.h5")

print("✅ Dummy ECG model saved to models/arrhythmia_model.h5")