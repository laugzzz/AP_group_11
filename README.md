# AP_Group_11 TCP Signal Visualiser

A PySide6 desktop application for real-time visualisation and offline inspection of multi-channel EMG signals streamed over TCP.

**Group:** Ekhlass · Laura · Radhika 

Applied Programming, FAU Erlangen-Nürnberg (Summer Semester 2026)

---

# Table of Contents:-

- Project Overview
- Team Responsibilities
- Architecture (MVVM)
- Data Flow
- Features
- Signal Processing
- Prerequisites 
- Installation
- Running the Application
- Using the Application
- Testing
- Error Handling
- Project Structure
- Dependencies
- License

---

# Project Overview:-

TCP Signal Visualizer is a desktop application developed using **PySide6** to receive, process, and visualize Electromyography (EMG) signals transmitted over a TCP connection in real time.

The application acts as a TCP client that continuously receives streamed EMG packets from a TCP server, processes the incoming data, and visualizes it using **VisPy** for high-performance real-time rendering. Once the recording session has finished, users can inspect the complete recording offline using **Matplotlib**.

The software follows the **Model-View-ViewModel (MVVM)** architecture, providing a clear separation between the graphical interface, business logic, and data processing components. This improves maintainability, scalability, and code organization.

### Key Features

- Real-time TCP communication
- Live EMG visualization using VisPy
- Offline recording inspection using Matplotlib
- Raw signal visualization
- RMS signal visualization
- Bandpass filtered signal visualization
- Single-channel visualization
- Multi-channel visualization
- Thread-safe signal buffering
- Clean MVVM architecture
- Automated testing
- Responsive PySide6 graphical interface

---

# Team Responsibilities:-

| Member | Primary Role | Contributions |
|---------|--------------|---------------|
| **Ekhlass** | Backend | Implemented the backend logic including TCP communication, signal buffering, signal processing |
| **Laura** | Frontend | Developed the PySide6 graphical interface, VisPy live plotting, offline plotting, and ViewModel integration. |
| **Radhika** | Repository & Documentation | Managed the GitHub repository, project integration, testing support, and project documentation. |

---

# Architecture (MVVM):-

The project follows the **Model–View–ViewModel (MVVM)** architecture, ensuring that each component has a clearly defined responsibility.

```text
+--------------------------------------------------------------+
|                           VIEW                               |
|                                                              |
|  • PySide6 User Interface                                    |
|  • Live VisPy Plot                                           |
|  • Offline Matplotlib Plot                                   |
|  • User Controls                                              |
+---------------------------+----------------------------------+
                            |
                     Qt Signals / Slots
                            |
+---------------------------v----------------------------------+
|                       VIEWMODEL                              |
|                                                              |
|  • Application State                                         |
|  • Signal Mode Selection                                     |
|  • Channel Selection                                         |
|  • Communication with Model                                  |
+---------------------------+----------------------------------+
                            |
                        Method Calls
                            |
+---------------------------v----------------------------------+
|                          MODEL                               |
|                                                              |
|  • TCP Communication                                         |
|  • Data Buffer                                                |
|  • Signal Processing                                          |
|  • Recording Management                                       |
+--------------------------------------------------------------+
```

# Responsibilities:-

### View

Responsible for all graphical components of the application.

- Displays the live EMG signal.
- Displays the offline recording.
- Handles buttons, dropdowns, and user interaction.
- Never communicates directly with the TCP socket.

### ViewModel

Acts as the bridge between the View and the Model.

Responsibilities include:
- Managing application state.
- Selecting signal processing modes.
- Providing processed data to the GUI.
- Updating plots through Qt signals.

### Model

Responsible for backend functionality.

This layer performs:

- TCP communication
- Signal buffering
- Signal processing
- Recording management
- Data storage

---

# Data Flow:-

The following diagram illustrates how EMG data moves through the application.

```text
TCP Server
      │
      ▼
TCP Client
      │
      ▼
Signal Buffer
      │
      ▼
Signal Processing
      │
      ▼
Main ViewModel
      │
      ▼
PySide6 GUI
      │
      ▼
VisPy Live Plot
      │
      ▼
Offline Matplotlib Plot
```

### Data Flow Description

1. The TCP server continuously streams EMG packets.

2. The TCP client receives incoming packets.

3. The Model stores incoming data inside a thread-safe signal buffer.

4. Signal processing (Raw, RMS or Filtered) is applied.

5. The ViewModel requests processed data from the Model.

6. The View updates the VisPy live plot.

7. After disconnecting, the recorded buffer becomes available for offline inspection using Matplotlib.

---

# Signal Processing:-

The application provides three different signal processing modes, allowing users to inspect the EMG data from different perspectives.

## Data Format

Each packet received from the TCP server contains multi-channel EMG data.

| Parameter | Value |
|------------|-------|
| Channels | 32 |
| Samples per Channel | 18 |
| Data Type | Float64 |
| Transmission | TCP |

The incoming packets are reconstructed into NumPy arrays before being processed.

---

## Raw Signal

The **Raw** mode displays the incoming EMG signal exactly as it is received from the TCP server without any additional processing.

This mode is useful when inspecting the original recording.

---

## RMS (Root Mean Square)

The RMS mode computes the Root Mean Square over a moving window to produce a smoother representation of muscle activity.

**RMS Parameters**

| Parameter | Value |
|------------|-------|
| Window Type | Moving Window |
| Window Size | 100 ms (200 samples) |
| Sampling Rate | 2000 Hz |



Advantages:

- Reduces signal fluctuations
- Highlights muscle activation
- Produces a smoother waveform
- Makes comparisons easier

---

## Bandpass Filter

The Filtered mode applies a Butterworth Bandpass Filter to remove unwanted frequencies while preserving the useful EMG signal.

**Filter Parameters**

| Parameter | Value |
|------------|-------|
| Filter Type | Butterworth Bandpass |
| Filter Order | 4th Order |
| Low Cutoff Frequency | 20 Hz |
| High Cutoff Frequency | 450 Hz |
| Filtering Method | Zero-phase (`filtfilt`) |

Filtering improves the quality of the visualization by reducing low-frequency drift and high-frequency noise while preserving the EMG signal.

---

# Prerequisites:-

Before running the project, ensure the following software is installed:

- Python **3.10 or later**
- Git
- pip (included with Python)

Verify the installation by running:

```bash
python --version
git --version
pip --version
```

# Installation:-

Follow the steps below to install and run the project.

## Step 1 – Clone the Repository

The final submission is available in the **final-submission** branch.

Clone the repository using:

```bash
git clone --branch final-submission https://github.com/laugzzz/AP_group_11.git
```

Navigate to the project directory:

```bash
cd AP_group_11
```

The command above automatically checks out the **final-submission** branch.

---

## Step 2 – Create a Virtual Environment

Creating a virtual environment is recommended to avoid dependency conflicts.

### Windows

```bash
python -m venv .venv

\.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
python3 -m venv .venv

source .venv/bin/activate
```

After activation, your terminal should display:

```text
(.venv)
```

---

## Step 3 – Install Dependencies

Install all required Python packages.

```bash
pip install -r requirements.txt
```

This command installs all dependencies listed in the `requirements.txt` file.

---

# Running the Application:-

The application consists of two separate programs:

1. TCP Server
2. GUI Application

**The TCP Server must always be started before launching the client application.**
```
AP_group_11/
├── main.py                 ← GUI Application
├── TCP_Server/
│   └── main.py             ← TCP Server
```
---

## Terminal 1 – Start the TCP Server

Open a terminal.
Navigate to the project root directory and start the TCP Server (TCP_Server/main.py):

Run:

```bash
cd AP_group_11
python TCP_Server/main.py
```

Keep this terminal running while using the application.

---

## Terminal 2 – Launch the GUI

Open another terminal.
Navigate to the project root directory, and start the GUI application (main.py in the project root):

Run:

```bash
cd AP_group_11
python main.py
```

The graphical user interface will open.

---

# Using the Application:-

## Controls

| Control | Type | Description |
|----------|------|-------------|
| Port | Input Field | Enter the TCP server port number |
| Connect | Button | Starts TCP communication |
| Disconnect | Button | Stops data streaming |
| Signal Mode | Radio Buttons | Raw, RMS and Filtered modes |
| Channel | Dropdown | Select the desired EMG channel |
| Plot View | Toggle | Switch between single and multi-channel views |
| Offline Inspection | Button | Opens the recorded signal in Matplotlib |

---

# Typical Workflow:-

# Using the Application

1. Start the TCP Server.
2. Launch the GUI application.
3. Enter the TCP server port number and click **Connect** to begin receiving live EMG data.
4. The live plot will start updating automatically as data is received.
5. Use the **Channel** dropdown to switch between the 32 available EMG channels.
6. Select **Raw**, **RMS**, or **Filtered** to change the signal processing mode.
7. Switch between the single-channel and multi-channel views as required.
8. Click **Disconnect** to stop data streaming.
9. Click **Offline Inspection** to open the recorded signal in a Matplotlib window for offline analysis.    
****Note:**** When ***Plot All Channels*** is enabled, individual channel selection is disabled. To select a specific channel, first turn **Plot All Channels** off.
---


# Error Handling:-

The application handles the following situations without crashing:

| Situation | Behaviour |
|-----------|-----------|
| Invalid Port | Displays an appropriate error message |
| Server Not Running | Connection fails gracefully |
| Lost Connection | Streaming stops safely |
| Empty Recording | Offline plotting is disabled |
| Invalid Channel | Input validation prevents errors |
| Socket Exceptions | Errors are reported to the user |

---

# Project Structure:-

```text
AP_group_11/
│
├── main.py
├── Constants.py
├── requirements.txt
├── README.md
│
├── TCP_Server/
│   └── main.py
│
├── models/
│
├── viewmodels/
│
├── views/
│
├── tests/
│   ├── test_with_tcp.py
│   └── test_without_tcp.py
│
└── assets/
```

---

# Dependencies:-

| Package | Purpose |
|----------|---------|
| NumPy | Numerical computations and array manipulation |
| SciPy | Signal processing algorithms |
| Matplotlib | Offline visualization |
| PySide6 | Desktop graphical user interface |
| VisPy | High-performance real-time visualization |
| PyOpenGL | OpenGL backend required by VisPy |

Install all dependencies using:

```bash
pip install -r requirements.txt
```

---

# License:-

This project was developed as the final project for the **Applied Programming** course at **Friedrich-Alexander-Universität Erlangen–Nürnberg (FAU)** during the **Summer Semester 2026**.

The project is intended for educational purposes only.
