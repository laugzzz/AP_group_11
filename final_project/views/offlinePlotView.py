import matplotlib.pyplot as plt
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QButtonGroup, QComboBox, QFrame, QLabel, QPushButton, QToolBar


class OfflinePlotView:
    """Matplotlib-based offline signal inspection window."""

    MODES = {
        "Raw": "raw",
        "Filtered": "filtered",
        "RMS": "rms",
    }

    MODE_LABELS = {
        "raw": "Raw",
        "filtered": "Filtered",
        "rms": "RMS",
    }

    def __init__(self, view_model):
        self.view_model = view_model

    def show(self):
        """Open the offline plot for the buffered signal data."""
        if not self.view_model.has_offline_data():
            self.view_model.status_updated.emit("No data available for offline inspection")
            return

        channel = self.view_model.selected_channel
        mode = self.view_model.selected_mode
        x, y = self.view_model.get_offline_data(channel, mode)

        fig, ax = plt.subplots(figsize=(12, 4))
        (line,) = ax.plot(x, y)
        self._format_axes(ax, channel, mode, len(y), x)

        plt.tight_layout()
        self._add_controls(fig, ax, line, x)
        plt.show(block=False)

    def _format_axes(self, ax, channel, mode, sample_count, x):
        ax.set_title(
            f"Channel {channel + 1} - {mode.upper()} "
            f"({sample_count} samples, {x[-1] - x[0]:.1f}s)"
        )
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude")
        ax.grid(True, alpha=0.3)

    def _add_controls(self, fig, ax, line, x):
        window = getattr(fig.canvas.manager, "window", None)
        if window is None or not hasattr(window, "addToolBar"):
            return

        channel_combo = QComboBox()
        for channel_number in range(1, self.view_model.channel_count + 1):
            channel_combo.addItem(f"Channel {channel_number}")
        channel_combo.setCurrentIndex(self.view_model.selected_channel)
        channel_combo.setFixedHeight(34)

        raw_button = QPushButton("Raw")
        filtered_button = QPushButton("Filtered")
        rms_button = QPushButton("RMS")
        mode_buttons = {
            "Raw": raw_button,
            "Filtered": filtered_button,
            "RMS": rms_button,
        }

        mode_group = QButtonGroup()
        mode_group.setExclusive(True)
        for button in mode_buttons.values():
            button.setCheckable(True)
            button.setFixedHeight(34)
            mode_group.addButton(button)
        initial_mode_label = self.MODE_LABELS.get(self.view_model.selected_mode, "Raw")
        mode_buttons[initial_mode_label].setChecked(True)

        def selected_mode():
            for label, button in mode_buttons.items():
                if button.isChecked():
                    return self.MODES[label]
            return "raw"

        def redraw():
            channel = channel_combo.currentIndex()
            mode = selected_mode()
            _, y_data = self.view_model.get_offline_data(channel, mode)

            line.set_ydata(y_data)
            ax.relim()
            ax.autoscale_view(scalex=False, scaley=True)
            self._format_axes(ax, channel, mode, len(y_data), x)
            fig.canvas.draw_idle()

        channel_combo.currentIndexChanged.connect(redraw)
        raw_button.clicked.connect(redraw)
        filtered_button.clicked.connect(redraw)
        rms_button.clicked.connect(redraw)

        controls_toolbar = QToolBar("Offline Controls", window)
        controls_toolbar.setMovable(False)
        controls_toolbar.setFixedHeight(46)
        controls_toolbar.setStyleSheet("""
            QToolBar {
                background-color: #ffffff;
                border-top: 1px solid #d8e0ea;
                spacing: 6px;
                padding: 5px 10px;
            }
            QToolBar QLabel {
                color: #475569;
                font-size: 12px;
                font-weight: bold;
                padding: 0 2px;
            }
            QToolBar QComboBox {
                min-width: 145px;
                min-height: 26px;
                padding: 3px 8px;
                border: 1px solid #c8d1dc;
                border-radius: 4px;
                background-color: #f8fafc;
                color: #1f2937;
                font-size: 12px;
            }
            QToolBar QPushButton {
                min-width: 76px;
                min-height: 26px;
                padding: 3px 10px;
                border: 1px solid #c8d1dc;
                border-radius: 4px;
                background-color: #f8fafc;
                color: #334155;
                font-size: 12px;
                font-weight: bold;
            }
            QToolBar QPushButton:hover {
                background-color: #e8f0fe;
                border-color: #2a7fd4;
            }
            QToolBar QPushButton:checked {
                background-color: #1769aa;
                color: white;
                border-color: #125487;
            }
        """)

        channel_label = QLabel("Channel:")
        channel_label.setFixedHeight(34)
        channel_label.setAlignment(Qt.AlignVCenter)

        divider = QFrame()
        divider.setFixedSize(2, 34)
        divider.setStyleSheet("background-color: #1f2937; border: none;")

        mode_label = QLabel("Mode:")
        mode_label.setFixedHeight(34)
        mode_label.setAlignment(Qt.AlignVCenter)

        controls_toolbar.addWidget(channel_label)
        controls_toolbar.addWidget(channel_combo)
        controls_toolbar.addWidget(divider)
        controls_toolbar.addWidget(mode_label)
        controls_toolbar.addWidget(raw_button)
        controls_toolbar.addWidget(filtered_button)
        controls_toolbar.addWidget(rms_button)
        window.addToolBar(Qt.BottomToolBarArea, controls_toolbar)

        fig._offline_controls = (
            controls_toolbar,
            channel_combo,
            mode_group,
            raw_button,
            filtered_button,
            rms_button,
        )
