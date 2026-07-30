# AP_Group_11 TCP Signal Visualiser

A PySide6 desktop application for real-time visualisation and offline inspection of multi-channel EMG signals streamed over TCP.

**Group:11** 

-***Ekhlass Erouiah*** (matrikel no.- 23786741)

-***Laura Uruci*** (matrikel no.- 23839274)

-***Radhika Tawde*** (matrikel no.- 23831646)

Applied Programming, FAU Erlangen-Nürnberg (Summer Semester 2026)

---

# Table of Contents

- [Project Overview](#project-overview)
- [Team Responsibilities](#team-responsibilities)
- [Architecture (MVVM)](#architecture-mvvm)
- [Data Flow](#data-flow)
- [Signal Processing](#signal-processing)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Using the Application](#using-the-application)
- [Error Handling](#error-handling)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

# Project Overview

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
- Responsive PySide6 graphical interface

---

# Team Responsibilities

| Member | Primary Role | Contributions |
|---------|--------------|---------------|
| **Ekhlass** | Backend | Implemented the backend logic including TCP communication, signal buffering, signal processing |
| **Laura** | Frontend | Developed the PySide6 graphical interface, VisPy live plotting, offline plotting, and ViewModel integration. |
| **Radhika** | Repository & Documentation | Managed the GitHub repository, project integration, testing support, and project documentation. |

---

# Architecture (MVVM)

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

## Responsibilities

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

# Data Flow

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

# Signal Processing

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

# Prerequisites

Before running the project, ensure the following software is installed:

- Python **3.10 or later**
- Git
- pip (included with Python)

Verify the installation by running (***Windows***)

```bash
python --version
git --version
pip --version
```

Verify the installation by running (***Linux/ MacOS***)
```bash
python3 --version
git --version
pip3 --version
```

---

# Installation

Follow the steps below to install and run the project.

## Step 1 – Clone the Repository

The project is available from the repository’s default branch, **main**.

Clone the repository using:

```bash
git clone https://github.com/laugzzz/AP_group_11.git
```

Navigate to the project directory:

```bash
cd AP_group_11
```
---

## Step 2 – Create a Virtual Environment

Creating a virtual environment is recommended to avoid dependency conflicts.

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> **Note:** If you get a script execution error, run this first to allow the activation script:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
> ```
> Then run `.\.venv\Scripts\Activate.ps1` again.

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

After activation, your terminal prompt will show `(.venv)`.

---

## Step 3 – Install Dependencies

Install all required Python packages.

```bash
pip install -r requirements.txt
```

This command installs all dependencies listed in the `requirements.txt` file.

---

# Running the Application

The application has two parts that must be started in separate terminals:

1. **TCP Server** — streams the EMG data
2. **GUI Application** — receives and visualises the data

**The TCP Server must be started before the GUI application.**

```
AP_group_11/
├── TCP_Server/
│   └── main.py          ← TCP Server
└── final_project/
    └── main.py          ← GUI Application
```

---

## Terminal 1 – Start the TCP Server

### Windows
```bash
cd AP_group_11
python TCP_Server/main.py
```
### Linux/MacOS
```bash
cd AP_group_11
python3 TCP_Server/main.py
```

Keep this terminal running. The server listens on port **12345** by default.

---

## Terminal 2 – Launch the GUI Application

Open a second terminal:

### Windows
```bash
cd AP_group_11
python final_project/main.py
```
### Linux/ MacOS
```bash
cd AP_group_11
python3 final_project/main.py
```

The graphical user interface will open.

---

# Using the Application

## Typical Workflow

1. Start the TCP Server (`python TCP_Server/main.py`).
2. Launch the GUI (`python final_project/main.py`).
3. In the GUI, enter port **12345** (or the port shown in the server terminal) and click **Connect**.
4. The live plot starts updating automatically as data arrives.
5. Use the **Channel** dropdown to switch between the 32 available EMG channels.
6. Select **Raw**, **RMS**, or **Filtered** to change the signal processing mode.
7. Click **Plot All Channels** to see all 32 channels at once with vertical offsets. While this is active, the channel dropdown is disabled — turn it off to select a specific channel again.
8. Click **Disconnect** to stop streaming.
9. Click **Offline Inspection** to open the recorded signal in a Matplotlib window.

---

## Controls

| Control | Type | Description |
|----------|------|-------------|
| Port | Input Field | TCP server port number (default: 12345) |
| Connect | Button | Starts TCP communication and live streaming |
| Disconnect | Button | Stops data streaming |
| Signal Mode | Radio Buttons | Switch between Raw, RMS, and Filtered |
| Channel | Dropdown | Select the EMG channel to display (1–32) |
| Plot All Channels | Toggle | Show all 32 channels with vertical offsets |
| Offline Inspection | Button | Opens the full recording in Matplotlib |

---

# Error Handling

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

# Project Structure

```text
AP_group_11/
├── README.md
├── requirements.txt
├── recording.pkl
│
├── final_project/
│   ├── main.py                  ← Application entry point
│   ├── models/
│   │   └── signal_model.py      ← TCP client, buffer, signal processing
│   ├── viewmodels/
│   │   └── mainViewModel.py     ← Application state and logic
│   └── views/
│       ├── mainView.py          ← Main window and controls
│       ├── plotView.py          ← Live VisPy plot widget
│       └── offlinePlotView.py   ← Offline Matplotlib plot window
│
└── TCP_Server/
    └── main.py                  ← Provided TCP server (Exercise 5)
```

---

# Dependencies

| Package | Purpose |
|----------|---------|
| NumPy | Numerical computations and array manipulation |
| SciPy | Signal processing algorithms |
| Matplotlib | Offline visualization |
| PySide6 | Desktop graphical user interface |
| VisPy | High-performance real-time visualization |

Install all dependencies using:

```bash
pip install -r requirements.txt
```

---

# Troubleshooting

### Compilation errors when installing requirements.txt (numpy / vispy / pillow)

This is the most common installation problem. Some packages can fail with build or compilation errors on certain systems. Follow these steps in order:

**Step 1 — Upgrade pip, setuptools and wheel before anything else:**
```bash
python -m pip install --upgrade pip setuptools wheel
```

**Step 2 — Install the requirements:**
```bash
pip install -r requirements.txt
```

**Step 3 — If a specific package still fails, install it individually first:**
```bash
pip install numpy
pip install pillow
pip install vispy
pip install -r requirements.txt
```
---

### Application won't start / import errors

Make sure the venv is activated and `pip install -r requirements.txt` completed without errors. Run from the `AP_group_11/` directory:
```bash
python final_project/main.py
```

---

### Cannot connect to the server

- Make sure the TCP server is running in a separate terminal (`python TCP_Server/main.py`).
- Use port **12345** (the default). The server prints the port when it starts.
- Make sure no firewall is blocking localhost connections.

---

### VisPy shows a black canvas or crashes

VisPy requires an OpenGL-capable display driver. On Windows, ensure your graphics drivers are up to date. Running inside a remote session (e.g. RDP without GPU forwarding) may cause VisPy to fail.

---

### Note for Mac Users
Clone this project into a local (non-iCloud-synced) directory. If the project or virtual environment is stored in an iCloud-synced folder (e.g., Desktop or Documents), Qt plugins may fail to load due to a known macOS/Qt issue.

---

# License

This project was developed as the final project for the **Applied Programming** course at **Friedrich-Alexander-Universität Erlangen–Nürnberg (FAU)** during the **Summer Semester 2026**.

The project is intended for educational purposes only.
