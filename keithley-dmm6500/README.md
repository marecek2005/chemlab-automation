# Keithley DMM6500 Laboratory Automation (`vslab`)

Python instrumentation suite for controlling a **Keithley DMM6500 6½-digit digital multimeter** over USB-VISA using **TSP (Test Script Processor)** hardware-timed trigger models, live visualization, and sampling-interval diagnostics.

## Features

- **Hardware-timed Trigger Model (`src/dmm6500_logger.py`)**: Configures the DMM6500 internal `defbuffer1` (up to 100,000 points) with `trigger.model.load('SimpleLoop', ...)` for accurate instrument-side timestamps rather than host-OS sleep loops, streaming readings continuously to `measurements_dmm.csv`.
- **Cross-platform VISA Discovery**: Automatically queries both native NI-VISA and pure-Python `pyvisa-py` (`@py`) backends and matches the target instrument by USB serial number (with single-device fallback).
- **Tkinter Desktop Controller (`src/gui_controller.py`)**: Simple lab bench GUI to launch DC Voltage / Current acquisition and open the live plot window.
- **Real-Time Live Plotter (`src/realtime_plot.py`)**: `matplotlib.animation.FuncAnimation` viewer polling `measurements_dmm.csv` every 500 ms with dynamic axis autoscaling.
- **Timing & Jitter Diagnostics (`src/analyze_intervals.py`)**: Evaluates actual hardware inter-sample intervals (`defbuffer1.relativetimestamps`), mean deviation, relative timing error, and min/max jitter spread against the target sampling period.
- **Experimental Prototypes (`experiments/`)**: Earlier USB/macOS and TSP trigger-loop test iterations kept for reference (`usb_test_dmm2.py`, `usb_test3.py`, `usb_test_mac.py`).

## Environment Setup

Using Conda:
```bash
conda env create -f environment.yml
conda activate vslab
```

Or using `pip`:
```bash
pip install pyvisa pyvisa-py pyusb matplotlib
```

## Usage

```bash
# Launch the desktop controller GUI
python src/gui_controller.py

# Or run the hardware-timed DC voltage logger directly (Ctrl+C aborts the trigger model safely)
python src/dmm6500_logger.py

# Open live plotting in a separate terminal
python src/realtime_plot.py

# Evaluate timing precision after recording
python src/analyze_intervals.py
```

> **Note:** Update `TARGET_SERIAL` in `src/dmm6500_logger.py` to match your benchtop Keithley DMM6500 serial number, or connect a single USB VISA instrument for automatic fallback detection.
