from PySide6.QtCore import QObject, QTimer, Signal

try:
    from ..models.signal_model import SignalModel
except ImportError:
    from models.signal_model import SignalModel


class MainViewModel(QObject):
    # Signals emitted to the View
    plot_updated = Signal(object, object)          # x array, y array (single channel)
    all_channels_updated = Signal(object, object)  # x array, data_2d (all 32 channels)
    status_updated = Signal(str)                   # status message for the GUI label
    connection_changed = Signal(bool)              # True = connected, False = disconnected
    stream_stats_updated = Signal(str)             # live TCP/buffer stats for the GUI

    def __init__(self):
        super().__init__()

        # The backend model — handles TCP, buffering, and signal processing
        self.model = SignalModel()

        # Current GUI selections — updated when user changes dropdown/buttons
        self.selected_channel = 0       # 0-based index
        self.selected_mode = "raw"      # "raw", "filtered", or "rms"
        self.show_all_channels = False   # True = emit all_channels_updated each tick

        # QTimer drives the data loop: every 50ms → receive + plot update
        self.timer = QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self._on_timer_tick)
        #self.timer         = the alarm clock
        #.timeout           = the alarm ringing event
        #.connect(...)      = "when it rings, do this action"
        #self._on_timer_tick = the action (your function)
        # 50ms later → Qt fires timeout → _on_timer_tick() runs automatically

    def connect_to_server(self, port):
        """Called when user clicks the Connect button."""
        try:
            self.model.connect(port)
            self.timer.start()
            self.status_updated.emit(f"Connected on port {port} - receiving EMG packets")
            self.connection_changed.emit(True)
            self._emit_stream_stats()
        except ConnectionRefusedError:
            self.status_updated.emit(
                f"Could not connect on port {port}: start the TCP server first"
            )
        except OSError as error:
            self.status_updated.emit(f"Could not connect: {error}")

    def disconnect(self):
        """Called when user clicks the Disconnect button."""
        self.model.disconnect()
        self.timer.stop()
        self.status_updated.emit("Disconnected — buffer available for offline inspection")
        self.connection_changed.emit(False)
        self._emit_stream_stats()

    def set_channel(self, channel_index):
        """Called when user changes the channel dropdown (0-based)."""
        self.selected_channel = channel_index
        self._redraw_if_offline()

    def set_mode(self, mode):
        """Called when user clicks a mode button: 'raw', 'filtered', or 'rms'."""
        self.selected_mode = mode
        self._redraw_if_offline()

    def set_all_channels_mode(self, enabled):
        """Switch between single-channel view (False) and all-channels view (True)."""
        self.show_all_channels = enabled
        self._redraw_if_offline()

    def _redraw_if_offline(self):
        """
        When disconnected but data exists, immediately emit one plot update.

        The QTimer is stopped after disconnect, so changing channel/mode would
        otherwise have no visible effect on the plot. This triggers a single
        redraw so the user sees the new selection instantly.
        """
        if self.model.is_connected or not self.model.has_data():
            return

        x = self.model.get_time_axis()
        if self.show_all_channels:
            data_2d = self.model.get_all_channels(self.selected_mode)
            self.all_channels_updated.emit(x, data_2d)
        else:
            y = self.model.get_data(self.selected_channel, self.selected_mode)
            self.plot_updated.emit(x, y)

    @property
    def channel_count(self):
        """Number of channels available in the signal model."""
        return self.model.CHANNELS

    def has_offline_data(self):
        """Return True when the buffered data can be inspected offline."""
        return self.model.has_data()

    def get_offline_data(self, channel, mode):
        """Return time and signal arrays for offline plotting."""
        x = self.model.get_time_axis()
        y = self.model.get_data(channel, mode)
        return x, y

    def _on_timer_tick(self):
        """
        Called every 50ms by the QTimer.

        Steps:
        1. Ask the model to receive any new bytes from the socket.
        2. If enough data exists, get the current channel/mode data.
        3. Emit plot_updated so the View redraws the signal.
        
        If server disconnected during receive, stop the timer
        This happens when in receive_data() following code line is called:
         if not new_bytes:
             self.disconnect()
             return

        In receive_data() (backend):
           recv() returns empty bytes → server closed connection
            → self.disconnect() is called
            → self.is_connected = False

        Back in _on_timer_tick() (ViewModel):
        model.receive_data() just ran
       → checks: if not self.model.is_connected  ← True now
       → stops the timer
       → emits status message to GUI
        """
        self.model.receive_data()
        
        if not self.model.is_connected:
            self.timer.stop()
            self.status_updated.emit("Server disconnected — buffer available for offline inspection")
            self.connection_changed.emit(False)
            self._emit_stream_stats()
            return

        if not self.model.has_data():
            self._emit_stream_stats()
            return

        x = self.model.get_time_axis()

        if self.show_all_channels:
            # Emit all 32 channels for the all-channels plot widget
            data_2d = self.model.get_all_channels(self.selected_mode)
            self.all_channels_updated.emit(x, data_2d)
        else:
            # Emit only the selected channel for the single-channel plot widget
            y = self.model.get_data(self.selected_channel, self.selected_mode)
            self.plot_updated.emit(x, y)

        self._emit_stream_stats()

    def _emit_stream_stats(self):
        """Emit a compact summary of the current TCP stream and rolling buffer."""
        samples = self.model.total_samples_received
        elapsed = self.model.get_signal_time_seconds()
        buffer_samples = self.model.data_buffer.shape[1]
        buffer_seconds = buffer_samples / self.model.SAMPLING_RATE
        packets = samples // self.model.SAMPLES_PER_PACKET
        self.stream_stats_updated.emit(
            f"Signal time: {elapsed:5.2f} s   |   "
            f"Packets: {packets:4d}   |   "
            f"Samples: {samples:5d}   |   "
            f"Buffer: {buffer_seconds:4.1f} / {self.model.WINDOW_SECONDS} s"
        )
