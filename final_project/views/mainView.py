from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from views.plotView import AllChannelsPlotWidget, VisPyPlotWidget


class MainView(QMainWindow):
    """
    Main application window.

    Contains:
    - Port input + Connect / Disconnect buttons
    - Status label
    - VisPy live plot
    - Channel dropdown
    - Signal mode buttons (Raw / Filtered / RMS)
    """

    def __init__(self, view_model):
        super().__init__()

        self.view_model = view_model

        self.setWindowTitle("EMG Signal Viewer")
        self.resize(1200, 700)

        # ── Global stylesheet ─────────────────────────────────────────────
        self.setStyleSheet("""
            QMainWindow { background-color: #f0f2f5; }
            QWidget      { font-family: 'Segoe UI', Arial, sans-serif;
                           font-size: 13px; color: #2c2c2c; }
            QPushButton  { padding: 5px 14px;
                           border: 1px solid #c8ccd0;
                           border-radius: 4px;
                           background-color: #ffffff;
                           min-width: 72px; }
            QPushButton:hover    { background-color: #e8f0fe;
                                   border-color: #2a7fd4; }
            QPushButton:pressed  { background-color: #c8dff8; }
            QPushButton:checked  { background-color: #2a7fd4;
                                   color: white;
                                   font-weight: bold;
                                   border: 1px solid #1a5fa0; }
            QPushButton:disabled { background-color: #f0f0f0;
                                   color: #aaaaaa;
                                   border-color: #ddd; }
            QLineEdit, QComboBox { border: 1px solid #c8ccd0;
                                   border-radius: 4px;
                                   padding: 4px 8px;
                                   background-color: white; }
        """)

        # ── Central widget and main layout ────────────────────────────────
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # ── Row 1: Connection controls ────────────────────────────────────
        conn_layout = QHBoxLayout()

        conn_layout.addWidget(QLabel("Port:"))
        self.port_input = QLineEdit("12345")
        self.port_input.setFixedWidth(80)
        conn_layout.addWidget(self.port_input)

        self.connect_button = QPushButton("Connect")
        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.setEnabled(False)
        conn_layout.addWidget(self.connect_button)
        conn_layout.addWidget(self.disconnect_button)
        conn_layout.addStretch()

        main_layout.addLayout(conn_layout)

        # ── Row 2: Status label ───────────────────────────────────────────
        self.status_label = QLabel("Not connected")
        main_layout.addWidget(self.status_label)

        # ── Row 3: Plot area — single channel or all channels ──────────────────
        # QStackedWidget holds two plot widgets; only one is visible at a time.
        self.plot_stack = QStackedWidget()
        self.plot_widget = VisPyPlotWidget()                   # index 0: single channel
        self.all_channels_widget = AllChannelsPlotWidget()     # index 1: all channels
        self.plot_stack.addWidget(self.plot_widget)
        self.plot_stack.addWidget(self.all_channels_widget)
        main_layout.addWidget(self.plot_stack, stretch=1)

        # ── Info note ───────────────────────────────────────────────────
        info_label = QLabel(
            "ⓘ  Live view shows a rolling window of the last 10 s.  "
            "The TCP server streams ~20 s of pre-recorded EMG data, then closes the connection."
        )
        info_label.setStyleSheet("color: #888; font-style: italic; font-size: 11px;")
        main_layout.addWidget(info_label)

        # ── Row 4: Channel selector + Lock View button ───────────────────
        ch_layout = QHBoxLayout()
        ch_layout.addWidget(QLabel("Channel:"))
        self.channel_combo = QComboBox()
        for i in range(32):
            self.channel_combo.addItem(f"Channel {i + 1}")
        ch_layout.addWidget(self.channel_combo)
        ch_layout.addStretch()
        # Lock View: when checked, auto-fit is disabled so user can freely zoom/pan
        self.lock_view_button = QPushButton("Lock View")
        self.lock_view_button.setCheckable(True)
        self.lock_view_button.setToolTip(
            "When active, the plot stops auto-fitting so you can zoom and pan freely."
        )
        ch_layout.addWidget(self.lock_view_button)

        # Grid toggle: show/hide background grid lines in the plot
        self.grid_button = QPushButton("Grid")
        self.grid_button.setCheckable(True)
        self.grid_button.setToolTip("Show or hide the background grid.")
        ch_layout.addWidget(self.grid_button)

        main_layout.addLayout(ch_layout)

        # ── Row 5: Signal mode buttons + view controls ────────────────────
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Mode:"))
        self.raw_button = QPushButton("Raw")
        self.filtered_button = QPushButton("Filtered")
        self.rms_button = QPushButton("RMS")
        # Make mode buttons behave like radio buttons: one is always active
        for btn in (self.raw_button, self.filtered_button, self.rms_button):
            btn.setCheckable(True)
        self.raw_button.setChecked(True)  # Raw is the default mode
        self.mode_group = QButtonGroup(self)
        self.mode_group.setExclusive(True)
        self.mode_group.addButton(self.raw_button)
        self.mode_group.addButton(self.filtered_button)
        self.mode_group.addButton(self.rms_button)
        self.all_channels_button = QPushButton("Plot All Channels")
        self.all_channels_button.setCheckable(True)   # toggles on/off
        self.offline_button = QPushButton("Inspect Offline")
        self.offline_button.setEnabled(False)         # enabled only after disconnect
        mode_layout.addWidget(self.raw_button)
        mode_layout.addWidget(self.filtered_button)
        mode_layout.addWidget(self.rms_button)
        mode_layout.addWidget(self.all_channels_button)
        mode_layout.addStretch()
        mode_layout.addWidget(self.offline_button)
        main_layout.addLayout(mode_layout)

        # ── Connect signals to ViewModel ──────────────────────────────────
        self.connect_button.clicked.connect(self._on_connect)
        self.disconnect_button.clicked.connect(self._on_disconnect)
        self.channel_combo.currentIndexChanged.connect(self.view_model.set_channel)
        self.raw_button.clicked.connect(lambda: self.view_model.set_mode("raw"))
        self.filtered_button.clicked.connect(lambda: self.view_model.set_mode("filtered"))
        self.rms_button.clicked.connect(lambda: self.view_model.set_mode("rms"))
        self.all_channels_button.toggled.connect(self._on_all_channels_toggled)
        self.offline_button.clicked.connect(self.view_model.open_offline_plot)
        self.lock_view_button.toggled.connect(self._on_lock_view_toggled)
        self.grid_button.toggled.connect(self._on_grid_toggled)

        # ── Receive signals from ViewModel ───────────────────────────────
        self.view_model.plot_updated.connect(self.plot_widget.update_plot)
        self.view_model.all_channels_updated.connect(self.all_channels_widget.update_plot)
        self.view_model.status_updated.connect(self._on_status_message)
        self.view_model.connection_changed.connect(self._on_connection_changed)

    def _on_connect(self):
        """Read port from input field and ask ViewModel to connect."""
        try:
            port = int(self.port_input.text())
        except ValueError:
            self._on_status_message("Invalid port — enter a number")
            return

        self.view_model.connect(port)

    def _on_disconnect(self):
        """Ask ViewModel to disconnect."""
        self.view_model.disconnect()

    def _on_connection_changed(self, connected):
        """Update button states whenever the connection status changes."""
        self.connect_button.setEnabled(not connected)
        self.disconnect_button.setEnabled(connected)
        # Re-enable auto-fit when a new connection starts
        if connected:
            self.lock_view_button.setChecked(False)
        # Offline inspection is only useful when disconnected and data is available
        self.offline_button.setEnabled(not connected and self.view_model.model.has_data())

    def _on_status_message(self, message):
        """Display a status message and colour it based on content."""
        self.status_label.setText(message)
        msg_lower = message.lower()
        if "connected" in msg_lower and "not" not in msg_lower and "dis" not in msg_lower:
            # Successful connection → green
            self.status_label.setStyleSheet("color: #2e7d32; font-weight: bold;")
        elif any(w in msg_lower for w in ("could not", "invalid", "no data", "error")):
            # Error / warning → red
            self.status_label.setStyleSheet("color: #c62828; font-weight: bold;")
        else:
            # Neutral (disconnected, waiting) → dark grey
            self.status_label.setStyleSheet("color: #555555; font-weight: normal;")

    def _on_lock_view_toggled(self, locked):
        """Propagate Lock View to both plot widgets."""
        self.plot_widget.autofit = not locked
        self.all_channels_widget.autofit = not locked

    def _on_grid_toggled(self, enabled):
        """Show or hide the background grid in both plot widgets."""
        self.plot_widget.show_grid = enabled
        self.all_channels_widget.show_grid = enabled

    def _on_all_channels_toggled(self, checked):
        """Switch between single-channel plot and all-channels plot."""
        self.view_model.set_all_channels_mode(checked)
        # QStackedWidget index 0 = single channel, index 1 = all channels
        self.plot_stack.setCurrentIndex(1 if checked else 0)
