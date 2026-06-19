from vispy import app, scene
import numpy as np


class LivePlotWidget:
    def __init__(self):
        self.canvas = scene.SceneCanvas(show=True, title="Live Signal")
        self.view = self.canvas.central_widget.add_view()

        self.view.camera = "panzoom"

        # --- CONFIG ---
        self.n_points = 200
        self.x = np.arange(self.n_points)

        # THIS will later come from TCP (32 channels)
        self.current_channel = 0

        # fake buffer (we simulate one channel for now)
        self.signal = np.zeros(self.n_points)

        # VisPy line
        self.line = scene.Line(
            pos=np.column_stack((self.x, self.signal)),
            parent=self.view.scene
        )

        # timer for live update
        self.t = 0
        self.timer = app.Timer(interval=0.05, connect=self.update, start=True)

    # -------------------------
    # THIS IS YOUR MAIN ENTRY POINT
    # later TCP data will call this
    # -------------------------
    def set_data(self, new_signal: np.ndarray):
        self.signal = new_signal

    def update(self, event):
        # fake live signal (replace later with TCP buffer)
        new_value = np.sin(self.t * 0.1)

        self.signal = np.roll(self.signal, -1)
        self.signal[-1] = new_value

        self.t += 1

        self.line.set_data(
            pos=np.column_stack((self.x, self.signal))
        )


if __name__ == "__main__":
    LivePlotWidget()
    app.run()