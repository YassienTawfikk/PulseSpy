# Pulse Spy – Patient Monitor GUI  

## 🚀 Overview  
**Pulse Spy** is a biomedical desktop application that simulates a real-time patient monitoring system. It displays ECG signals, calculates heart rate, and automatically detects and classifies arrhythmias. The interface is designed for medical accuracy, real-time interaction, and clean visualization.

![Overview](https://github.com/user-attachments/assets/e843b8d5-dc87-43bc-9672-68e6d9f01aa6)


## 🎯 Features  
✔️ Real-time ECG signal visualization  
✔️ Live heart rate monitoring  
✔️ Arrhythmia detection and classification  
✔️ Alarm system with ON/OFF and pause functions  
✔️ Upload and playback of ECG recordings  
✔️ Reset, clear, and exit controls for session handling  
✔️ PyQt5-powered interface with clinical styling  

## 📌 Installation  
```bash
pip install -r requirements.txt
````

## 🛠 Tech Stack

* **Programming Language:** Python
* **GUI Framework:** PyQt5
* **Visualization:** pyqtgraph
* **Signal Processing:** NumPy, SciPy
* **Sound Alerts:** QSound (PyQt5.QtMultimedia)
* **ECG Data Handling:** pandas, wfdb

## 📊 Usage

1. Launch the app:

```bash
python main.py
```

2. Click **Upload** to import an ECG file.
3. Observe the live plot and heart rate counter.
4. Use **Alarm Pause**, **Reset**, or **Clear** as needed.
5. Close the app with the exit (X) button.

## 🧠 Arrhythmia Detection Algorithm

Pulse Spy uses a hybrid signal processing approach to detect cardiac events in real time:

* **Low-pass filtering** with a cutoff of 15 Hz is applied to isolate the QRS complex.
* **QRS detection** is performed using `scipy.signal.find_peaks()` with dynamic height and distance thresholds.
* **P-wave detection** uses a Butterworth bandpass filter (0.5–4 Hz) to isolate atrial activity.
* **Heart rate** is calculated based on valid RR intervals (0.3s to 1.5s).
* **Rhythm classification** uses a combination of RR variability and BPM thresholds.

### ✅ Detected Arrhythmias

1. **Tachycardia**

   * Condition: Heart rate > 100 BPM
   * Action: Alarm triggered and red-highlighted HR display

2. **Bradycardia**

   * Condition: Heart rate < 60 BPM
   * Action: Alarm triggered and red-highlighted HR display

3. **Atrial Fibrillation (AFib)**

   * Condition: Irregular RR intervals with high standard deviation
   * Action: Diagnosis labeled as "Atrial Fibrillation" with suppressed alarm to avoid false positives

The system continuously evaluates incoming ECG segments during playback and adapts the display and alert system based on detected cardiac activity.

## 🤝 Contributions

## Contributors
<div>
<table align="center">
  <tr>
        <td align="center">
      <a href="https://github.com/YassienTawfikk" target="_blank">
        <img src="https://avatars.githubusercontent.com/u/126521373?v=4" width="150px;" alt="Yassien Tawfik"/>
        <br />
        <sub><b>Yassien Tawfik</b></sub>
      </a>
    </td>
      <td align="center">
      <a href="https://github.com/Mazenmarwan023" target="_blank">
        <img src="https://avatars.githubusercontent.com/u/127551364?v=4" width="150px;" alt="Mazen Marwan"/>
        <br />
        <sub><b>Mazen Marwan</b></sub>
      </a>
    </td>    
    <td align="center">
      <a href="https://github.com/madonna-mosaad" target="_blank">
        <img src="https://avatars.githubusercontent.com/u/127048836?v=4" width="150px;" alt="Madonna Mosaad"/>
        <br />
        <sub><b>Madonna Mosaad</b></sub>
      </a>
    </td>
        <td align="center">
      <a href="https://github.com/nancymahmoud1" target="_blank">
        <img src="https://avatars.githubusercontent.com/u/125357872?v=4" width="150px;" alt="Nancy Mahmoud"/>
        <br />
        <sub><b>Nancy Mahmoud</b></sub>
      </a>
    </td>
    </td>
        <td align="center">
      <a href="https://github.com/mohamedddyasserr" target="_blank">
        <img src="https://avatars.githubusercontent.com/u/126451832?v=4" width="150px;" alt="Mohamed Yasser"/>
        <br />
        <sub><b>Mohamed Yasser</b></sub>
      </a>
    </td>    
      <td align="center">
      <a href="https://github.com/yousseftaha167" target="_blank">
        <img src="https://avatars.githubusercontent.com/u/128304243?v=4" width="150px;" alt="Youssef Taha"/>
        <br />
        <sub><b>Youssef Taha</b></sub>
      </a>
    </td>    
  </tr>
</table>
</div>
