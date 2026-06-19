import socket
import numpy as np
from scipy import signal


class SignalModel:
    """
    Backend model for the EMG TCP Signal Visualization Application.

    Responsibilities:
    - Connect to and disconnect from the TCP server
    - Receive raw bytes from the server and reconstruct them into numpy arrays
    - Store the last 10 seconds of data in a rolling buffer
    - Apply signal processing (bandpass filter, RMS) on demand

    Data format expected from the server:
    - 32 channels x 18 samples per packet
    - dtype: float64 (8 bytes per value)
    - packet size: 32 x 18 x 8 = 4608 bytes

    The server streams pre-recorded EMG data continuously.
    Each packet represents 18 consecutive time snapshots for all 32 electrodes.
    At a sampling rate of 2000 Hz, ~111 packets arrive per second.
    """

    # ─────────────────────────────────────────────
    # Constants matching the TCP server configuration
    # ─────────────────────────────────────────────
    HOST = "localhost"          # server runs on the same machine
    PORT = 12345                # must match EMGTCPServer port
    SAMPLING_RATE = 2000        # Hz — samples per second per channel
    CHANNELS = 32               # number of electrodes
    SAMPLES_PER_PACKET = 18     # time snapshots bundled per TCP packet
    WINDOW_SECONDS = 10         # how many seconds of history to keep
    DTYPE = np.float64          # must match server's .tobytes() dtype
    # Raw 16-bit ADC counts (−32768…32767) from recording.pkl → millivolts.
    # Value taken from recording.pkl: device_information['conversion_factor_biosignal']
    CONVERSION_FACTOR = 0.0002861  # mV per ADC count


    def __init__(self):
        # ── Socket state ──────────────────────────────────────────────────
        self.socket = None
        self.is_connected = False

        # ── Derived constants ─────────────────────────────────────────────
        # Total float64 values in one packet: 32 channels × 18 samples
        self.packet_size = self.CHANNELS * self.SAMPLES_PER_PACKET

        # Total bytes in one packet: 576 values × 8 bytes each = 4608 bytes
        self.packet_size_bytes = self.packet_size * np.dtype(self.DTYPE).itemsize

        # Maximum samples to keep per channel: 2000 Hz × 10 s = 20000
        self.window_size = int(self.SAMPLING_RATE * self.WINDOW_SECONDS)

        # ── Buffer 1: byte_buffer ─────────────────────────────────────────
        # Temporary tray for raw incoming bytes.
        # TCP does not guarantee that recv() returns exactly one packet.
        # We accumulate bytes here until we have at least 4608 (one full packet),
        # then extract and decode them into real numbers.
        self.byte_buffer = bytearray()

        # ── Buffer 2: data_buffer ─────────────────────────────────────────
        # Rolling history of decoded voltage values.
        # Shape: (32 channels, up to 20000 samples)
        # New data is appended on the right; oldest data is trimmed from the left.
        # This buffer is NOT cleared on disconnect — it stays for offline inspection.
        self.data_buffer = np.empty((self.CHANNELS, 0), dtype=self.DTYPE)

        # Counter used to reconstruct the absolute time axis.
        # Incremented by SAMPLES_PER_PACKET (18) with each decoded packet.
        self.total_samples_received = 0

    # ─────────────────────────────────────────────
    # Connection management
    # ─────────────────────────────────────────────

    def connect(self, port=None):
        """
        Open a TCP connection to the EMG server.

        Uses self.PORT by default. An optional port argument allows the user
        to override this from the GUI input field -> This is required 
        

        Non-blocking mode is set so that recv() returns immediately if no
        data is available, instead of freezing the GUI thread.

        Raises OSError if the server is not running or the port is wrong.
        The ViewModel should catch this and display a status message.
        """
        if self.is_connected:
            return

        # Reset all buffers so every new connection starts at t=0.
        # Without this, total_samples_received keeps accumulating across
        # sessions and the x-axis would start at 20s or 40s instead of 0.
        self.total_samples_received = 0
        self.data_buffer = np.empty((self.CHANNELS, 0), dtype=self.DTYPE)
        self.byte_buffer = bytearray()

        if port is not None:
           target_port = port      # use the port the user passed in
        else:
           target_port = self.PORT # use the default (12345)
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.HOST, target_port))

        # Non-blocking: recv() raises BlockingIOError instead of waiting
        # when no data is available. This keeps the GUI responsive.
        self.socket.setblocking(False)

        self.is_connected = True

    def disconnect(self):
        """
        Close the TCP connection.

        The data_buffer is intentionally NOT cleared here.
        After disconnecting, the buffer holds the last 10 seconds of recorded
        data and can still be queried via get_data() for offline inspection.
        """
        self.is_connected = False

        if self.socket is not None:
            self.socket.close()
            self.socket = None

    # ─────────────────────────────────────────────
    # Data reception  (called every ~50ms by QTimer)
    # ─────────────────────────────────────────────

    def receive_data(self):
        """
        Receive all bytes currently available in the socket buffer.

        This method is called repeatedly by a QTimer in the ViewModel (every ~50ms).
        It does NOT block — if no data is available, it returns immediately.

        Steps:
        1. Read bytes from the socket into byte_buffer until nothing is left.
        2. Extract complete 4608-byte packets from byte_buffer.
        3. Decode each packet into a (32, 18) numpy array.
        4. Append decoded data to data_buffer and trim to the rolling window.
        """
        if not self.is_connected or self.socket is None:
            return

        # Step 1 — drain the socket buffer
        while True:
            try:
                new_bytes = self.socket.recv(4096)

                if not new_bytes:
                    # Server closed the connection
                    self.disconnect()
                    return

                self.byte_buffer.extend(new_bytes)

            except BlockingIOError:
                # No more bytes available right now — this is normal, not an error.
                # It means we have read everything the OS had buffered so far.
                break

        # Step 2-4 — reconstruct packets from accumulated bytes
        self._extract_packets_from_buffer()

    def _extract_packets_from_buffer(self):
        """
        Extract complete packets from byte_buffer and append to data_buffer.

        One packet = 4608 bytes = 32 channels × 18 samples × 8 bytes (float64).
        Leftover bytes (incomplete packet) stay in byte_buffer for the next call.
        """
        packets = []

        while len(self.byte_buffer) >= self.packet_size_bytes:
            # Take exactly one packet worth of bytes
            packet_bytes = self.byte_buffer[:self.packet_size_bytes]
            del self.byte_buffer[:self.packet_size_bytes]

            # Decode bytes → flat array of 576 float64 values → reshape to (32, 18)
            packet = np.frombuffer(packet_bytes, dtype=self.DTYPE)
            packet = packet.reshape(self.CHANNELS, self.SAMPLES_PER_PACKET)
            # Convert raw ADC counts to millivolts
            packet = packet * self.CONVERSION_FACTOR

            packets.append(packet)

        if not packets:
            return

        # Concatenate all new packets along the time axis (axis=1)
        # new_data shape: (32, 18 * number_of_new_packets)
        new_data = np.concatenate(packets, axis=1)

        # Append new data to the right of the rolling buffer
        self.data_buffer = np.concatenate((self.data_buffer, new_data), axis=1)

        # Update the total sample counter (used for the time axis)
        self.total_samples_received += new_data.shape[1]

        # Trim the buffer from the left to keep only the last 10 seconds
        if self.data_buffer.shape[1] > self.window_size:
            self.data_buffer = self.data_buffer[:, -self.window_size:]

    # ─────────────────────────────────────────────
    # Data access  (called by ViewModel to get plot data)
    # ─────────────────────────────────────────────

    def has_data(self):
        """
        Return True if the buffer contains enough samples to plot.

        At least 2 samples are needed to draw a line. With only 1 sample,
        only a point can be drawn — not useful for signal visualization.
        """
        return self.data_buffer.shape[1] >= 2

    def get_data(self, channel, mode="raw"):
        """
        Return a 1D numpy array for one channel, processed according to mode.

        Parameters
        ----------
        channel : int
            Channel index (0-based). Channel 1 on the GUI = index 0 here.
        mode : str
            One of: "raw", "filtered", "rms"

        Returns
        -------
        np.ndarray, shape (N,)
            The signal for the requested channel and mode.
            N = number of samples currently in the buffer (up to 20000).
        """
        # data_buffer already holds values in mV (conversion applied at decode time)
        raw = self.data_buffer[channel, :]

        if mode == "raw":
            return raw

        elif mode == "filtered":
            return self._apply_bandpass_filter(raw)

        elif mode == "rms":
            # RMS is always computed on the filtered signal, not raw.
            # Filtering first removes noise before computing the energy envelope.
            filtered = self._apply_bandpass_filter(raw)
            return self._apply_rms(filtered)

        else:
            raise ValueError(f"Unknown mode '{mode}'. Use 'raw', 'filtered', or 'rms'.")

    def get_all_channels(self, mode="raw"):
        """
        Return data for all 32 channels at once.

        Used by the "Plot All Channels" button to show all electrodes
        simultaneously with a vertical offset between them.

        Returns
        -------
        np.ndarray, shape (32, N)
            One row per channel, processed according to mode.
        """
        return np.array([self.get_data(ch, mode) for ch in range(self.CHANNELS)])

    def get_time_axis(self):
        """
        Return the x-axis (time in seconds) for the current buffer contents.

        Time is reconstructed from total_samples_received and the sampling rate.
        The x-axis always covers the last WINDOW_SECONDS seconds (up to 10s).

        Returns
        -------
        np.ndarray, shape (N,)
            Time values in seconds corresponding to each sample in the buffer.
        """
        num_samples = self.data_buffer.shape[1] # number of samples currently in the buffer (up to 20000)
        # Index of the oldest sample still in the buffer (0-based, counting from stream start)
        oldest_sample_index = self.total_samples_received - num_samples
        # arange gives one timestamp per sample at exactly 1/SAMPLING_RATE spacing,
        # with no off-by-one: sample k → time k/SAMPLING_RATE.
        return (oldest_sample_index + np.arange(num_samples)) / self.SAMPLING_RATE

    def get_signal_time_seconds(self):
        """Return the total elapsed recording time in seconds."""
        return self.total_samples_received / self.SAMPLING_RATE

    # ─────────────────────────────────────────────
    # Signal processing  (internal helpers)
    # ─────────────────────────────────────────────

    def _apply_bandpass_filter(self, channel_data):
        """
        Apply a 4th-order Butterworth bandpass filter to a 1D signal.

        Keeps frequencies between 20 Hz and 450 Hz.
        - Below 20 Hz: movement artifacts and DC drift — not real EMG
        - Above 450 Hz: electrical noise — not real EMG

        Uses filtfilt (zero-phase, forward + backward pass) so the filtered
        signal has no time shift compared to the original.

        filtfilt works here because we filter the whole buffer at once
        (all samples are already in memory), not sample by sample.

        Parameters
        ----------
        channel_data : np.ndarray, shape (N,)
            Raw voltage values for one channel.

        Returns
        -------
        np.ndarray, shape (N,)
            Filtered voltage values.
        """
        low_cut = 20    # Hz — removes movement artifacts below this
        high_cut = 450  # Hz — removes high-frequency noise above this

        nyquist = self.SAMPLING_RATE / 2  # = 1000 Hz

        # Normalize cutoff frequencies to the range [0, 1] relative to Nyquist.
        # scipy.signal.butter expects normalized frequencies.
        low = low_cut / nyquist   # = 0.02
        high = high_cut / nyquist  # = 0.45

        # Design a 4th-order Butterworth bandpass filter.
        # b, a are the filter coefficients used by filtfilt.
        b, a = signal.butter(4, [low, high], btype="band")

        # filtfilt needs at least 3 * filter_order = 12 samples to work.
        # Return raw data unchanged if the buffer is too short (startup phase).
        if len(channel_data) < 3 * 8:  # 8 = len(a) for a 4th-order bandpass
            return channel_data

        # Apply filter forward and backward to cancel phase delay.
        return signal.filtfilt(b, a, channel_data)

    def _apply_rms(self, channel_data, window_ms=100):
        """
        Compute the RMS (Root Mean Square) envelope of a 1D signal.

        RMS converts the fast-oscillating filtered signal into a smooth curve
        showing "how much energy / muscle activity" exists at each moment.
        Like a volume meter — it shows the envelope, not the individual wiggles.

        Uses a vectorized cumulative-sum approach (O(N)) instead of a Python loop,
        which is critical for real-time performance with 20 000-sample buffers.

        Parameters
        ----------
        channel_data : np.ndarray, shape (N,)
            Filtered signal for one channel.
        window_ms : float
            Width of the sliding window in milliseconds. Default: 100ms.
            At 2000 Hz, 100ms = 200 samples.

        Returns
        -------
        np.ndarray, shape (N,)
            RMS envelope of the input signal.
        """
        # Convert window from milliseconds to number of samples
        window_size = int((window_ms / 1000) * self.SAMPLING_RATE)  # = 200 samples

        # Vectorized sliding-window RMS via cumulative sum of squares.
        # np.convolve with a uniform kernel gives the windowed sum in O(N).
        sq = channel_data ** 2
        kernel = np.ones(window_size) / window_size
        # 'same' keeps output length == input length; edges use partial windows.
        mean_sq = np.convolve(sq, kernel, mode="same")
        return np.sqrt(mean_sq)
