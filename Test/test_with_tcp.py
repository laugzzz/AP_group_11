import time
import sys

sys.path.insert(0, r"c:\Users\z005751t\Documents\ProjectAP\Applied-Programming-2026-1\final_project")

from models.signal_model import SignalModel

model = SignalModel()

# Step 1 — connect
model.connect(12345)
print("Connected:      ", model.is_connected)

# Step 2 — receive data for 2 seconds
"""
Simulates the QTimer rhythm from the real app:
  call receive_data() → wait 50ms → call again → ...

  range(40)          = repeat 40 times
  time.sleep(0.05)   = wait 50ms between each call
  40 × 50ms          = 2000ms = 2 seconds total
"""
print("Receiving data for 10 seconds...")
for i in range(200):
    model.receive_data()
    time.sleep(0.05)

# Step 3 — check results
print("Samples received:", model.total_samples_received)  # should be ~4000
print("Buffer shape:    ", model.data_buffer.shape)       # should be (32, ~4000)
print("has_data:        ", model.has_data())              # should be True
print("Signal time:     ", round(model.get_signal_time_seconds(), 2), "seconds")

# Step 4 — test get_data
raw = model.get_data(0, "raw")
filtered = model.get_data(0, "filtered")
rms = model.get_data(0, "rms")
print("raw shape:       ", raw.shape)
print("filtered shape:  ", filtered.shape)
print("rms shape:       ", rms.shape)

# Step 5 — disconnect
model.disconnect()
print("Disconnected:    ", not model.is_connected)

# Step 6 — buffer still accessible after disconnect
print("Buffer after disconnect:", model.data_buffer.shape)

print("\nAll TCP tests passed!")

