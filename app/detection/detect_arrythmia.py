import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks
from tabulate import tabulate


def arrhythmia_detection(time, voltage):
    """
    Input: time (array), voltage (array)
    Returns: List of detected arrhythmias with timestamps.
    """
    # 1. Detect R-peaks (heartbeats)
    peaks, _ = find_peaks(voltage, height=np.mean(voltage) + 2 * np.std(voltage), distance=100)

    # 2. Calculate RR intervals (time between beats)
    rr_intervals = np.diff(time[peaks])

    # 3. Classify based on rules
    arrhythmias = []
    mean_hr = 60 / np.mean(rr_intervals)  # Avg heart rate (bpm)

    for i, rr in enumerate(rr_intervals):
        hr = 60 / rr  # Instantaneous heart rate

        # Bradycardia (HR < 60 bpm)
        if hr < 60:
            arrhythmias.append({
                "type": "Bradycardia",
                "time": time[peaks[i]],
                "heart_rate": hr
            })

        # Tachycardia (HR > 100 bpm)
        elif hr > 100:
            arrhythmias.append({
                "type": "Tachycardia",
                "time": time[peaks[i]],
                "heart_rate": hr
            })

        # PVC (Premature Ventricular Contraction)
        if i > 0 and rr < 0.8 * rr_intervals[i - 1]:  # Sudden short interval
            arrhythmias.append({
                "type": "PVC",
                "time": time[peaks[i]],
                "rr_interval": rr
            })

    return arrhythmias


def print_arrhythmia_results(results):
    """
    Prints detected arrhythmias in a structured format with severity colors.
    Input: List of arrhythmia dictionaries from rule_based_arrhythmia_detection()
    """
    if not results:
        print("\033[92m✓ No arrhythmias detected - Normal rhythm\033[0m")
        return

    # Convert to DataFrame for pretty printing
    df = pd.DataFrame(results)

    # Add emoji/icons based on arrhythmia type
    df['Icon'] = df['type'].map({
        "Bradycardia": "🫀↓",
        "Tachycardia": "🫀↑",
        "PVC": "💥"
    })

    # Color coding
    def color_row(row):
        if row['type'] == "PVC":
            return '\033[91m'  # Red for PVCs
        elif "cardia" in row['type']:
            return '\033[93m'  # Yellow for HR issues
        else:
            return '\033[0m'  # Default

    df['Color'] = df.apply(color_row, axis=1)

    # Print summary header
    print(f"\n\033[1mARRHYTHMIA REPORT ({len(df)} EVENTS DETECTED)\033[0m")
    print("=" * 50)

    # Print table
    print(tabulate(
        df[['Icon', 'type', 'time', 'heart_rate', 'rr_interval']],
        headers=["", "Type", "Time (s)", "HR (bpm)", "RR (s)"],
        tablefmt="grid",
        showindex=False,
        floatfmt=".2f"
    ))

    # Print color-coded details
    print("\n\033[1mDETAILS:\033[0m")
    for _, row in df.iterrows():
        print(f"{row['Color']}{row['Icon']} \033[1m{row['type']}\033[0m at {row['time']:.2f}s: ", end="")
        if 'heart_rate' in row:
            print(f"Heart rate = {row['heart_rate']:.0f} bpm")
        else:
            print(f"RR interval = {row['rr_interval']:.3f}s ({(row['rr_interval'] / 0.8) * 100:.0f}% of previous)")
        print("\033[0m", end="")  # Reset color


df = pd.read_csv("/Users/macbook/Documents/Med_Equipments/ECG_Person_69_rec_2_raw.csv")  # path of the file
results = arrhythmia_detection(df['Time'].values, df['FHR'].values)

# Example usage:
print_arrhythmia_results(results)