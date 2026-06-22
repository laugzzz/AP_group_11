# AP Group 11 - EMG Signal Viewer

PySide6 desktop application for live EMG signal visualization from a local TCP
server. The project uses an MVVM structure:

- `TCP_Server/` streams prerecorded EMG packets from `recording.pkl`
- `final_project/models/` handles TCP reception, buffering, and processing
- `final_project/viewmodels/` connects model state to the GUI
- `final_project/views/` contains the PySide6 and VisPy widgets

## Team

Group 11

Team members and responsibilities:

- Laura Uruci - frontend/UI, app launch flow
- TODO - TCP/backend, buffering
- TODO - signal processing, documentation/testing

## Setup

Use Python 3.10 or newer.

```bash
cd AP_group_11
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Windows, activate the environment with:

```powershell
.venv\Scripts\activate
```

## Run in VS Code

Open the project folder in VS Code, open `final_project/main.py`, and press
Run. The app starts a local TCP server automatically in the background.

In the GUI, keep the port set to `12345` and press **Connect**.

You can also use the Run and Debug panel and choose:

```text
Run EMG Signal Viewer
```

## Run from Terminal

If you prefer running the server and GUI separately, open two terminals in the
project folder.

Terminal 1 - start the TCP server:

```bash
python start_server.py
```

Leave this terminal open. It should print:

```text
Server started on 127.0.0.1:12345
```

Terminal 2 - start the GUI:

```bash
python start_gui.py
```

In the GUI, keep the port set to `12345` and press **Connect**.

## How to Use

- Press **Connect** to start receiving streamed EMG packets.
- Use the **Channel** dropdown to inspect one channel at a time.
- Press **Plot All Channels** to show all 32 channels with vertical offsets.
- Use **Raw**, **Filtered**, and **RMS** to switch signal modes.
- Use **Grid** to show/hide plot grid lines.
- Use **Lock View** to stop auto-fitting and manually pan/zoom the plot.
- After disconnecting or after the stream ends, press **Open Offline Plot** to
  inspect the buffered data with Matplotlib.

## Signal Processing

- Raw mode shows the received EMG signal after conversion to millivolts.
- Filtered mode applies a 4th-order Butterworth bandpass filter from 20 Hz to
  450 Hz.
- RMS mode first filters the signal, then computes the RMS envelope using a
  100 ms moving window.
- The live view keeps a rolling 10-second buffer.

## TCP Data Format

The TCP server sends raw bytes. The client expects the same data contract used
in Exercise 5:

- 32 channels
- 18 samples per packet
- `float64` values
- one packet = `32 x 18 x 8 = 4608` bytes

The client collects incoming bytes in a byte buffer, extracts complete packets,
reshapes them to `(32, 18)`, and appends them to the rolling data buffer.

## MVVM Structure

- Model: `final_project/models/signal_model.py`
  Handles TCP connection, byte buffering, packet reconstruction, rolling buffer,
  and signal processing.
- ViewModel: `final_project/viewmodels/mainViewModel.py`
  Owns GUI state, starts/stops the timer, asks the model for data, and emits Qt
  signals to the view.
- View: `final_project/views/mainView.py` and `final_project/views/plotView.py`
  Builds the GUI and displays live VisPy plots.
- App entry point: `final_project/main.py`
  Starts the Qt application and opens the main window.

## Notes

- `127.0.0.1` means the server and GUI run on the same computer.
- `recording.pkl` must stay in the project root next to this README.
- If the GUI says the connection was refused, start `python start_server.py`
  first or check that no other program is using port `12345`.
