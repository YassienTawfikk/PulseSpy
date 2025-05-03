from scipy.signal import butter, filtfilt


def bandpass_filter(signal, lowcut=0.5, highcut=40.0, fs=250, order=2):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, signal)
