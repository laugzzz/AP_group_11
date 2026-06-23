from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

try:
    from .offlinePlotView import OfflinePlotView
    from .plotView import AllChannelsPlotWidget, VisPyPlotWidget
except ImportError:
    from views.offlinePlotView import OfflinePlotView
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
        self.offline_plot_view = OfflinePlotView(view_model)

        self.setWindowTitle("EMG Signal Viewer")
        self.resize(1200, 700)
        self.setMinimumSize(900, 560)

        # ── Global stylesheet ─────────────────────────────────────────────
        self.setStyleSheet("""
            QMainWindow { background-color: #e9edf2; }
            QWidget      { font-family: 'Segoe UI', Arial, sans-serif;
                           font-size: 13px; color: #252a31; }
            QFrame#TopBar, QFrame#ControlBar {
                background-color: #ffffff;
                border: 1px solid #d7dde5;
                border-radius: 6px;
            }
            QFrame#PlotPanel {
                background-color: #ffffff;
                border: 1px solid #cfd7e2;
                border-radius: 6px;
            }
            QLabel#AppTitle { color: #1f2933;
                              font-size: 20px;
                              font-weight: bold; }
            QLabel#AppSubtitle { color: #697386;
                                 font-size: 12px; }
            QLabel#SectionLabel { color: #5f6872;
                                  font-size: 11px;
                                  font-weight: bold; }
            QLabel#StatusLabel  { padding: 6px 12px;
                                  border-radius: 4px;
                                  background-color: #f4f6f8; }
            QLabel#InfoLabel { color: #6b7280;
                               font-size: 11px;
                               padding-left: 2px; }
            QLabel#MetaLabel { color: #475569;
                               background-color: #f4f7fb;
                               border: 1px solid #d8e0ea;
                               border-radius: 4px;
                               padding: 4px 8px; }
            QLabel#ViewSummary { color: #334155;
                                 font-weight: bold; }
            QLabel#StatsLabel { color: #475569;
                                background-color: #f8fafc;
                                border: 1px solid #e2e8f0;
                                border-radius: 4px;
                                padding: 5px 8px;
                                font-family: Menlo, Consolas, monospace;
                                font-size: 11px; }
            QLabel#ModeExplanation { color: #334155;
                                      background-color: #f8fafc;
                                      border-left: 4px solid #1769aa;
                                      padding: 5px 8px; }
            QPushButton  { padding: 6px 14px;
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
            QPushButton#PrimaryButton { background-color: #1769aa;
                                        color: white;
                                        border-color: #125487;
                                        font-weight: bold; }
            QPushButton#PrimaryButton:hover { background-color: #1f7cc7; }
            QPushButton#SecondaryDanger { color: #8a2b2b; }
            QPushButton:disabled { background-color: #f0f0f0;
                                   color: #aaaaaa;
                                   border-color: #ddd; }
            QLineEdit, QComboBox { border: 1px solid #c8ccd0;
                                   border-radius: 4px;
                                   padding: 4px 8px;
                                   background-color: white; }
            QComboBox QAbstractItemView {
                font-size: 13px;
                min-width: 130px;
                selection-background-color: #2a7fd4;
                selection-color: white;
            }
            QComboBox QAbstractItemView::item {
                min-height: 24px;
                padding: 3px 8px;
            }
        """)

        # ── Central widget and main layout ────────────────────────────────
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # ── Header: app title + connection controls + status ──────────────
        top_bar = QFrame()
        top_bar.setObjectName("TopBar")
        top_layout = QVBoxLayout(top_bar)
        top_layout.setSpacing(8)
        top_layout.setContentsMargins(14, 10, 14, 10)

        header_row = QHBoxLayout()
        header_row.setSpacing(12)
        title_layout = QVBoxLayout()
        title_layout.setSpacing(1)
        title = QLabel("EMG Signal Viewer")
        title.setObjectName("AppTitle")
        subtitle = QLabel("Live TCP stream, signal modes, and offline inspection")
        subtitle.setObjectName("AppSubtitle")
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        header_row.addLayout(title_layout)
        header_row.addStretch()

        meta_layout = QHBoxLayout()
        meta_layout.setSpacing(6)
        for text in ("32 channels", "18 samples/packet", "4608 bytes", "10 s window"):
            meta_label = QLabel(text)
            meta_label.setObjectName("MetaLabel")
            meta_layout.addWidget(meta_label)
        header_row.addLayout(meta_layout)
        top_layout.addLayout(header_row)

        conn_layout = QHBoxLayout()
        conn_layout.setSpacing(8)

        connection_label = QLabel("CONNECTION")
        connection_label.setObjectName("SectionLabel")
        conn_layout.addWidget(connection_label)
        conn_layout.addWidget(QLabel("Port:"))
        self.port_input = QLineEdit("12345")
        self.port_input.setFixedWidth(80)
        conn_layout.addWidget(self.port_input)

        self.connect_button = QPushButton("Connect")
        self.connect_button.setObjectName("PrimaryButton")
        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.setObjectName("SecondaryDanger")
        self.disconnect_button.setEnabled(False)
        conn_layout.addWidget(self.connect_button)
        conn_layout.addWidget(self.disconnect_button)
        conn_layout.addStretch()

        self.status_label = QLabel("Ready - press Connect to start streaming")
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setMinimumWidth(320)
        conn_layout.addWidget(self.status_label)
        top_layout.addLayout(conn_layout)

        main_layout.addWidget(top_bar)

        # ── Plot area: single channel or all channels ─────────────────────
        plot_panel = QFrame()
        plot_panel.setObjectName("PlotPanel")
        plot_layout = QVBoxLayout(plot_panel)
        plot_layout.setContentsMargins(8, 8, 8, 8)
        plot_layout.setSpacing(6)

        self.view_summary_label = QLabel()
        self.view_summary_label.setObjectName("ViewSummary")
        plot_layout.addWidget(self.view_summary_label)

        self.stream_stats_label = QLabel(
            "Signal time:  0.00 s   |   Packets:    0   |   "
            "Samples:     0   |   Buffer:  0.0 / 10 s"
        )
        self.stream_stats_label.setObjectName("StatsLabel")
        plot_layout.addWidget(self.stream_stats_label)

        # QStackedWidget holds two plot widgets; only one is visible at a time.
        self.plot_stack = QStackedWidget()
        self.plot_widget = VisPyPlotWidget()                   # index 0: single channel
        self.all_channels_widget = AllChannelsPlotWidget()     # index 1: all channels
        self.plot_stack.addWidget(self.plot_widget)
        self.plot_stack.addWidget(self.all_channels_widget)
        plot_layout.addWidget(self.plot_stack, stretch=1)
        main_layout.addWidget(plot_panel, stretch=1)

        # ── Info note ───────────────────────────────────────────────────
        info_label = QLabel(
            "Live view shows the last 10 seconds of streamed EMG data."
        )
        info_label.setObjectName("InfoLabel")
        main_layout.addWidget(info_label)

        # ── Bottom controls ──────────────────────────────────────────────
        control_bar = QFrame()
        control_bar.setObjectName("ControlBar")
        control_layout = QVBoxLayout(control_bar)
        control_layout.setSpacing(10)
        control_layout.setContentsMargins(12, 10, 12, 10)

        view_layout = QHBoxLayout()
        view_layout.setSpacing(8)

        view_label = QLabel("VIEW")
        view_label.setObjectName("SectionLabel")
        view_layout.addWidget(view_label)
        view_layout.addWidget(QLabel("Channel:"))
        self.channel_combo = QComboBox()
        for i in range(32):
            self.channel_combo.addItem(f"Channel {i + 1}")
        self.channel_combo.setToolTip("Select one EMG channel for the single-channel plot.")
        view_layout.addWidget(self.channel_combo)

        self.all_channels_button = QPushButton("Plot All Channels")
        self.all_channels_button.setCheckable(True)   # toggles on/off
        self.all_channels_button.setToolTip("Show all 32 EMG channels with vertical offsets.")
        view_layout.addWidget(self.all_channels_button)

        # Grid toggle: show/hide background grid lines in the plot
        self.grid_button = QPushButton("Grid")
        self.grid_button.setCheckable(True)
        self.grid_button.setToolTip("Show or hide the background grid.")
        view_layout.addWidget(self.grid_button)

        # Lock View: when checked, auto-fit is disabled so user can freely zoom/pan
        self.lock_view_button = QPushButton("Lock View")
        self.lock_view_button.setCheckable(True)
        self.lock_view_button.setToolTip(
            "When active, the plot stops auto-fitting so you can zoom and pan freely."
        )
        view_layout.addWidget(self.lock_view_button)
        view_layout.addStretch()

        control_layout.addLayout(view_layout)

        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(8)
        signal_label = QLabel("SIGNAL")
        signal_label.setObjectName("SectionLabel")
        mode_layout.addWidget(signal_label)
        mode_layout.addWidget(QLabel("Mode:"))
        self.raw_button = QPushButton("Raw")
        self.filtered_button = QPushButton("Filtered")
        self.rms_button = QPushButton("RMS")
        self.raw_button.setToolTip("Show the received EMG signal without extra processing.")
        self.filtered_button.setToolTip("Show the EMG signal after a 20-450 Hz bandpass filter.")
        self.rms_button.setToolTip("Show the RMS amplitude envelope using a 100 ms window.")
        # Make mode buttons behave like radio buttons: one is always active
        for btn in (self.raw_button, self.filtered_button, self.rms_button):
            btn.setCheckable(True)
        self.raw_button.setChecked(True)  # Raw is the default mode
        self.mode_group = QButtonGroup(self)
        self.mode_group.setExclusive(True)
        self.mode_group.addButton(self.raw_button)
        self.mode_group.addButton(self.filtered_button)
        self.mode_group.addButton(self.rms_button)
        self.offline_button = QPushButton("Open Offline Plot")
        self.offline_button.setEnabled(False)         # enabled only after disconnect
        mode_layout.addWidget(self.raw_button)
        mode_layout.addWidget(self.filtered_button)
        mode_layout.addWidget(self.rms_button)
        self.mode_explanation_label = QLabel()
        self.mode_explanation_label.setObjectName("ModeExplanation")
        mode_layout.addWidget(self.mode_explanation_label)
        mode_layout.addStretch()
        mode_layout.addWidget(self.offline_button)
        control_layout.addLayout(mode_layout)

        main_layout.addWidget(control_bar)

        # ── Connect signals to ViewModel ──────────────────────────────────
        self.connect_button.clicked.connect(self._on_connect)
        self.disconnect_button.clicked.connect(self._on_disconnect)
        self.channel_combo.currentIndexChanged.connect(self._on_channel_changed)
        self.raw_button.clicked.connect(lambda: self._on_mode_selected("raw"))
        self.filtered_button.clicked.connect(lambda: self._on_mode_selected("filtered"))
        self.rms_button.clicked.connect(lambda: self._on_mode_selected("rms"))
        self.all_channels_button.toggled.connect(self._on_all_channels_toggled)
        self.offline_button.clicked.connect(self.offline_plot_view.show)
        self.lock_view_button.toggled.connect(self._on_lock_view_toggled)
        self.grid_button.toggled.connect(self._on_grid_toggled)

        # ── Receive signals from ViewModel ───────────────────────────────
        self.view_model.plot_updated.connect(self.plot_widget.update_plot)
        self.view_model.all_channels_updated.connect(self.all_channels_widget.update_plot)
        self.view_model.status_updated.connect(self._on_status_message)
        self.view_model.connection_changed.connect(self._on_connection_changed)
        self.view_model.stream_stats_updated.connect(self.stream_stats_label.setText)
        self._apply_mode_style("raw")
        self._refresh_view_summary()

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

    def _on_channel_changed(self, channel_index):
        """Update selected channel and refresh the visible view summary."""
        self.view_model.set_channel(channel_index)
        self._refresh_view_summary()

    def _on_mode_selected(self, mode):
        """Update selected signal mode and refresh the visible view summary."""
        self.view_model.set_mode(mode)
        self._apply_mode_style(mode)
        self._refresh_view_summary()

    def _on_connection_changed(self, connected):
        """Update button states whenever the connection status changes."""
        self.connect_button.setEnabled(not connected)
        self.disconnect_button.setEnabled(connected)
        # Re-enable auto-fit when a new connection starts
        if connected:
            self.lock_view_button.setChecked(False)
        # Offline inspection is only useful when disconnected and data is available
        self.offline_button.setEnabled(not connected and self.view_model.model.has_data())
        self._refresh_view_summary()

    def _on_status_message(self, message):
        """Display a status message and colour it based on content."""
        self.status_label.setText(message)
        msg_lower = message.lower()
        if "connected" in msg_lower and "not" not in msg_lower and "dis" not in msg_lower:
            # Successful connection → green
            self.status_label.setStyleSheet(
                "color: #2e7d32; font-weight: bold; "
                "background-color: #edf7ed; padding: 6px 12px; border-radius: 4px;"
            )
        elif any(w in msg_lower for w in ("could not", "invalid", "no data", "error")):
            # Error / warning → red
            self.status_label.setStyleSheet(
                "color: #c62828; font-weight: bold; "
                "background-color: #fdecec; padding: 6px 12px; border-radius: 4px;"
            )
        else:
            # Neutral (disconnected, waiting) → dark grey
            self.status_label.setStyleSheet(
                "color: #555555; font-weight: normal; "
                "background-color: #f4f6f8; padding: 6px 12px; border-radius: 4px;"
            )

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
        self.channel_combo.setEnabled(not checked)
        # QStackedWidget index 0 = single channel, index 1 = all channels
        self.plot_stack.setCurrentIndex(1 if checked else 0)
        self._refresh_view_summary()

    def _refresh_view_summary(self):
        """Show the current plot configuration in plain user-facing text."""
        mode = self.view_model.selected_mode.upper()
        connection = "streaming" if self.view_model.model.is_connected else "ready"
        if self.view_model.show_all_channels:
            view_text = "All 32 channels"
        else:
            view_text = f"Channel {self.view_model.selected_channel + 1}"
        self.view_summary_label.setText(
            f"Viewing: {view_text} | {mode} | rolling 10 s window | {connection}"
        )

    def _apply_mode_style(self, mode):
        """Make the active signal-processing mode visually obvious."""
        descriptions = {
            "raw": ("Raw mode: received EMG signal", "#1769aa"),
            "filtered": ("Filtered mode: 20-450 Hz bandpass applied", "#00875a"),
            "rms": ("RMS mode: filtered signal converted to a 100 ms envelope", "#7e3fa1"),
        }
        text, color = descriptions.get(mode, descriptions["raw"])
        self.mode_explanation_label.setText(text)
        self.mode_explanation_label.setStyleSheet(
            f"border-left: 4px solid {color}; "
            "background-color: #f8fafc; color: #334155; padding: 5px 8px;"
        )
        self.plot_widget.set_mode(mode)
        self.all_channels_widget.set_mode(mode)
