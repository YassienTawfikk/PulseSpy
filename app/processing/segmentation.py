import numpy as np
from biosppy.signals import ecg


def get_r_peaks(ecg_signal, sampling_rate=250):
    """
    Detect R-peaks in an ECG signal using biosppy.

    Args:
        ecg_signal (array): 1D ECG signal
        sampling_rate (int): Sampling frequency

    Returns:
        array: Indices of R-peaks
    """
    out = ecg.ecg(signal=ecg_signal, sampling_rate=sampling_rate, show=False)
    return out['rpeaks']


def extract_beats_around_r(ecg_signal, r_peaks, window_size=250, normalize=True):
    """
    Extracts windows of ECG data around R-peaks.

    Args:
        ecg_signal (array): Full 1D ECG signal
        r_peaks (array): Detected R-peak indices
        window_size (int): Number of samples per beat (centered)
        normalize (bool): Whether to z-normalize each beat

    Returns:
        list of arrays: Segmented and optionally normalized beats
    """
    half = window_size // 2
    beats = []
    for r in r_peaks:
        if r - half >= 0 and r + half < len(ecg_signal):
            beat = ecg_signal[r - half:r + half].astype(np.float32)
            if normalize:
                beat = (beat - np.mean(beat)) / (np.std(beat) + 1e-6)
            beats.append(beat)
    return beats


def segment_ecg_pipeline(signal, sampling_rate=250, window_size=250):
    """
    Full segmentation pipeline: detect peaks + extract clean beats.

    Args:
        signal (array): Raw or filtered ECG signal
        sampling_rate (int): Hz
        window_size (int): Beat window size

    Returns:
        list of np.array: Processed ECG beats
    """
    r_peaks = get_r_peaks(signal, sampling_rate=sampling_rate)
    beats = extract_beats_around_r(signal, r_peaks, window_size=window_size)
    return beats
