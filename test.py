import wfdb
import numpy as np
import matplotlib.pyplot as plt

# Define the record name (e.g., "800") - Change based on the downloaded files
record_name = "D:\PyCharmProjects\PulseSpy\mit-bih-supraventricular-arrhythmia-database-1.0.0\800"  # Full path without extension

# Load the record (ECG signal)
record = wfdb.rdrecord(record_name)

# Load the annotation file (arrhythmia labels)
annotation = wfdb.rdann(record_name, "atr")

# Extract signal and sampling frequency
signal = record.p_signal[:, 0]  # Select first ECG lead
fs = record.fs  # Sampling frequency
time = np.arange(len(signal)) / fs  # Time axis

# Plot ECG signal
plt.figure(figsize=(12, 4))
plt.plot(time, signal, label="ECG Signal", color='b')
plt.scatter(annotation.sample / fs, np.zeros_like(annotation.sample), color='red', label="Arrhythmia Markers", marker='x')
plt.xlabel("Time (s)")
plt.ylabel("Amplitude (mV)")
plt.title(f"MIT-BIH Supraventricular Arrhythmia Database - Record {record_name}")
plt.legend()
plt.grid()
plt.show()
