import colorsys
import math

import numpy as np
from PySide6.QtWidgets import QVBoxLayout, QWidget
from vispy import scene


def _nice_step(span, target_n=8):
    """Return a human-readable step size for ~target_n ticks across span."""
    if span <= 0:
        return 1.0
    raw = span / target_n
    mag = 10 ** math.floor(math.log10(raw))
    norm = raw / mag
    if norm < 1.5:
        nice = 1
    elif norm < 3.5:
        nice = 2
    elif norm < 7.5:
        nice = 5
    else:
        nice = 10
    return nice * mag


def _configure_axis_spacing(y_axis, x_axis):
    """Keep axis labels close while leaving readable room around tick numbers."""
    for axis_widget in (y_axis, x_axis):
        axis_widget.axis.major_tick_length = 6
        axis_widget.axis.minor_tick_length = 3
        axis_widget.axis.tick_label_margin = 18

    y_axis.width_max = 64
    x_axis.height_max = 44


class VisPyPlotWidget(QWidget):
    """VisPy canvas embedded in a PySide6 widget for live signal display."""

    MODE_STYLES = {
        "raw": (0.10, 0.35, 0.80, 1.0),
        "filtered": (0.00, 0.55, 0.32, 1.0),
        "rms": (0.55, 0.25, 0.75, 1.0),
    }

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create the VisPy canvas (the actual drawing surface)
        self.canvas = scene.SceneCanvas(
            keys="interactive",
            show=False,
            bgcolor="white",
            size=(1000, 500),
        )

        # Grid layout inside the canvas for axes + plot area
        grid = self.canvas.central_widget.add_grid(margin=10)

        self.y_axis = scene.AxisWidget(
            orientation="left", axis_color="black", tick_color="black", text_color="black"
        )
        self.x_axis = scene.AxisWidget(
            orientation="bottom", axis_color="black", tick_color="black", text_color="black"
        )
        _configure_axis_spacing(self.y_axis, self.x_axis)

        # col=0: rotated Y title, col=1: y_axis, col=2: plot view / x_axis
        y_label = scene.Label("Amplitude", color="black", rotation=-90)
        y_label.width_max = 20
        grid.add_widget(y_label, row=0, col=0)

        grid.add_widget(self.y_axis, row=0, col=1)
        self.view = grid.add_view(row=0, col=2)
        self.view.camera = "panzoom"
        grid.add_widget(self.x_axis, row=1, col=2)

        x_label = scene.Label("Time (s)", color="black")
        x_label.height_max = 20
        grid.add_widget(x_label, row=2, col=2)

        self.x_axis.link_view(self.view)
        self.y_axis.link_view(self.view)

        # Grid: pool of scene.Line visuals (hidden until needed).
        # Positioned at nice tick values based on the visible time and amplitude ranges.
        self._grid_show = False
        self._grid_visuals = []  # grown on demand, never shrunk
        self._grid_color = (0.65, 0.65, 0.65, 1.0)

        # The signal line — drawn after grid lines so it renders on top
        self._line_color = self.MODE_STYLES["raw"]
        self.line = scene.Line(
            pos=np.array([[0.0, 0.0], [1.0, 0.0]], dtype=float),
            color=self._line_color,
            parent=self.view.scene,
            width=1.5,
        )

        # Set a clean initial camera range so axes show 0..1 instead of VisPy's
        # internal default (random small negative values).
        self.view.camera.set_range(x=(0.0, 1.0), y=(0.0, 1.0), margin=0)

        layout.addWidget(self.canvas.native)

        # When True (default): axes auto-fit to the data on every update.
        # Set to False via the Lock View button to allow free zoom/pan.
        self.autofit = True

    def set_mode(self, mode):
        """Change the line color to make the active processing mode visible."""
        self._line_color = self.MODE_STYLES.get(mode, self.MODE_STYLES["raw"])
        self.line.set_data(color=self._line_color)
        self.canvas.native.update()

    def _get_or_create_grid_line(self, idx):
        while len(self._grid_visuals) <= idx:
            gl = scene.Line(
                pos=np.array([[0.0, 0.0], [1.0, 0.0]], dtype=np.float32),
                color=self._grid_color,
                parent=self.view.scene,
                width=1.0,
                connect="strip",
            )
            gl.visible = False
            self._grid_visuals.append(gl)
        return self._grid_visuals[idx]

    def _update_grid(self, x_min, x_max, y_min, y_max):
        """Draw grid lines at readable time and amplitude intervals."""
        x_step = _nice_step(x_max - x_min)
        y_step = _nice_step(y_max - y_min)

        x_ticks = np.arange(math.ceil(x_min / x_step) * x_step,
                            x_max + x_step * 0.01, x_step)
        y_ticks = np.arange(math.ceil(y_min / y_step) * y_step,
                            y_max + y_step * 0.01, y_step)

        needed = len(x_ticks) + len(y_ticks)
        # hide all first, then show only the ones we use
        for gl in self._grid_visuals:
            gl.visible = False

        idx = 0
        for xv in x_ticks:
            gl = self._get_or_create_grid_line(idx)
            gl.set_data(pos=np.array([[xv, y_min], [xv, y_max]], dtype=np.float32))
            gl.visible = True
            idx += 1
        for yv in y_ticks:
            gl = self._get_or_create_grid_line(idx)
            gl.set_data(pos=np.array([[x_min, yv], [x_max, yv]], dtype=np.float32))
            gl.visible = True
            idx += 1

    @property
    def show_grid(self):
        return self._grid_show

    @show_grid.setter
    def show_grid(self, value):
        self._grid_show = bool(value)
        if not value:
            for gl in self._grid_visuals:
                gl.visible = False
        self.canvas.native.update()

    def update_plot(self, x, y):
        """Redraw the signal line with new x/y data."""
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)

        pos = np.column_stack((x, y))
        self.line.set_data(pos=pos, color=self._line_color)

        # Auto-scale axes to fit the current data (only if not locked by user)
        if self.autofit:
            y_range = y.max() - y.min()
            y_pad = max(1.0, 0.1 * y_range)
            x_min, x_max = float(x.min()), float(x.max())
            y_min = float(y.min()) - y_pad
            y_max = float(y.max()) + y_pad
            self.view.camera.set_range(x=(x_min, x_max), y=(y_min, y_max), margin=0)
        else:
            rect = self.view.camera.rect
            x_min, x_max = rect.left, rect.right
            y_min, y_max = rect.bottom, rect.top

        if self._grid_show:
            self._update_grid(x_min, x_max, y_min, y_max)

        self.canvas.native.update()


class AllChannelsPlotWidget(QWidget):
    """
    VisPy canvas showing all 32 channels stacked with a vertical offset.

    Each channel is drawn as a separate colored line, shifted upward by
    a fixed spacing so they don't overlap. The spacing adapts automatically
    to the signal amplitude.
    """

    N_CHANNELS = 32

    MODE_ALPHA = {
        "raw": 0.85,
        "filtered": 0.95,
        "rms": 0.75,
    }

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.canvas = scene.SceneCanvas(
            keys="interactive",
            show=False,
            bgcolor="white",
            size=(1000, 500),
        )

        grid = self.canvas.central_widget.add_grid(margin=10)

        self.y_axis = scene.AxisWidget(
            orientation="left", axis_color="black", tick_color="black", text_color="black"
        )
        self.x_axis = scene.AxisWidget(
            orientation="bottom", axis_color="black", tick_color="black", text_color="black"
        )
        _configure_axis_spacing(self.y_axis, self.x_axis)

        # col=0: rotated Y title, col=1: y_axis, col=2: plot view / x_axis
        y_label = scene.Label("Amplitude", color="black", rotation=-90)
        y_label.width_max = 20
        grid.add_widget(y_label, row=0, col=0)

        grid.add_widget(self.y_axis, row=0, col=1)
        self.view = grid.add_view(row=0, col=2)
        self.view.camera = "panzoom"
        grid.add_widget(self.x_axis, row=1, col=2)

        x_label = scene.Label("Time (s)", color="black")
        x_label.height_max = 20
        grid.add_widget(x_label, row=2, col=2)

        self.x_axis.link_view(self.view)
        self.y_axis.link_view(self.view)

        # Grid visuals — same approach as VisPyPlotWidget, drawn before channel lines
        self._grid_show = False
        self._grid_visuals = []
        self._grid_color = (0.65, 0.65, 0.65, 1.0)

        # Create one line per channel — colored by cycling through hues
        flat = np.array([[0.0, 0.0], [1.0, 0.0]], dtype=float)
        self._lines = []
        self._line_colors = []
        self._mode_alpha = self.MODE_ALPHA["raw"]
        for i in range(self.N_CHANNELS):
            r, g, b = colorsys.hsv_to_rgb(i / self.N_CHANNELS, 0.8, 0.7)
            color = (r, g, b, self._mode_alpha)
            line = scene.Line(
                pos=flat,
                color=color,
                parent=self.view.scene,
                width=1.0,
            )
            self._lines.append(line)
            self._line_colors.append((r, g, b))

        layout.addWidget(self.canvas.native)

        self.autofit = True

    def set_mode(self, mode):
        """Adjust line opacity to show that the all-channel mode changed."""
        self._mode_alpha = self.MODE_ALPHA.get(mode, self.MODE_ALPHA["raw"])
        for line, (r, g, b) in zip(self._lines, self._line_colors):
            line.set_data(color=(r, g, b, self._mode_alpha))
        self.canvas.native.update()

    def _get_or_create_grid_line(self, idx):
        while len(self._grid_visuals) <= idx:
            gl = scene.Line(
                pos=np.array([[0.0, 0.0], [1.0, 0.0]], dtype=np.float32),
                color=self._grid_color,
                parent=self.view.scene,
                width=1.0,
                connect="strip",
            )
            gl.visible = False
            self._grid_visuals.append(gl)
        return self._grid_visuals[idx]

    def _update_grid(self, x_min, x_max, y_min, y_max):
        x_step = _nice_step(x_max - x_min)
        y_step = _nice_step(y_max - y_min)

        x_ticks = np.arange(math.ceil(x_min / x_step) * x_step,
                            x_max + x_step * 0.01, x_step)
        y_ticks = np.arange(math.ceil(y_min / y_step) * y_step,
                            y_max + y_step * 0.01, y_step)

        for gl in self._grid_visuals:
            gl.visible = False

        idx = 0
        for xv in x_ticks:
            gl = self._get_or_create_grid_line(idx)
            gl.set_data(pos=np.array([[xv, y_min], [xv, y_max]], dtype=np.float32))
            gl.visible = True
            idx += 1
        for yv in y_ticks:
            gl = self._get_or_create_grid_line(idx)
            gl.set_data(pos=np.array([[x_min, yv], [x_max, yv]], dtype=np.float32))
            gl.visible = True
            idx += 1

    @property
    def show_grid(self):
        return self._grid_show

    @show_grid.setter
    def show_grid(self, value):
        self._grid_show = bool(value)
        if not value:
            for gl in self._grid_visuals:
                gl.visible = False
        self.canvas.native.update()

    def update_plot(self, x, data_2d):
        """
        Redraw all 32 channel lines with new data.

        Parameters
        ----------
        x       : 1D array, shape (N,)  — time axis in seconds
        data_2d : 2D array, shape (32, N) — one row per channel
        """
        x = np.asarray(x, dtype=float)
        data_2d = np.asarray(data_2d, dtype=float)

        # Vertical spacing: 3 standard deviations of the full signal amplitude.
        # This auto-adapts so channels are readable without overlapping.
        spacing = max(3.0 * np.std(data_2d), 1e-6)

        y_min = float("inf")
        y_max = float("-inf")

        for i, line in enumerate(self._lines):
            # Shift channel i upward by i * spacing
            y = data_2d[i] + i * spacing
            line.set_data(pos=np.column_stack((x, y)))
            y_min = min(y_min, float(y.min()))
            y_max = max(y_max, float(y.max()))

        if self.autofit:
            y_range = y_max - y_min
            y_pad = max(1.0, 0.02 * y_range)
            cam_x_min, cam_x_max = float(x.min()), float(x.max())
            cam_y_min = y_min - y_pad
            cam_y_max = y_max + y_pad
            self.view.camera.set_range(
                x=(cam_x_min, cam_x_max),
                y=(cam_y_min, cam_y_max),
                margin=0,
            )
        else:
            rect = self.view.camera.rect
            cam_x_min, cam_x_max = rect.left, rect.right
            cam_y_min, cam_y_max = rect.bottom, rect.top

        if self._grid_show:
            self._update_grid(cam_x_min, cam_x_max, cam_y_min, cam_y_max)

        self.canvas.native.update()
