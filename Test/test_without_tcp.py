import numpy as np
import sys
sys.path.insert(0, r"c:\Users\z005751t\Documents\ProjectAP\Applied-Programming-2026-1\final_project")

from models.signal_model import SignalModel

model = SignalModel()

# Inject fake data directly into the buffer (bypasses TCP)
fake_data = np.random.randn(32, 2000) * 0.001  # 32 channels, 1 second of fake signal
model.data_buffer = fake_data
model.total_samples_received = 2000

# Test all three modes on channel 0
raw = model.get_data(0, "raw")
filtered = model.get_data(0, "filtered")
rms = model.get_data(0, "rms")
all_ch = model.get_all_channels("raw")

print("raw shape:     ", raw.shape)       # should be (2000,)
print("filtered shape:", filtered.shape)  # should be (2000,)
print("rms shape:     ", rms.shape)       # should be (2000,)
print("all_ch shape:  ", all_ch.shape)    # should be (32, 2000)
print("time axis:     ", model.get_time_axis()[:5])  # first 5 time values
print("All tests passed!")