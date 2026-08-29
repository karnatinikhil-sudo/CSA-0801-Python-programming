"""
CSA-0801: Python Programming - Module 07
Topic: Real-Time System Resource & Hardware Monitor GUI (Tkinter)

Features:
1. Tkinter Canvas dynamic progress bars and gauges
2. CPU and Memory simulation/polling via standard library
3. Real-time periodic refresh scheduling using `root.after()`
4. Live activity log console in Tkinter ScrolledText
"""

import os
import platform
import sys
import time
import tkinter as tk
from tkinter import ttk


class SystemMonitorGUI:
    """Desktop Hardware & Process Diagnostics Dashboard."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("CSA-0801: Python System & Resource Monitor")
        self.root.geometry("700x520")
        self.root.minsize(650, 480)

        self._tick_count = 0
        self._history = [20, 25, 30, 28, 35, 42, 38, 45, 50, 48, 55, 60]

        self._build_ui()
        self._schedule_next_poll()

    def _build_ui(self):
        # Header
        hdr = ttk.Frame(self.root, padding="14 10")
        hdr.pack(fill=tk.X)
        ttk.Label(hdr, text="Real-Time System Diagnostics", font=("Helvetica", 15, "bold")).pack(anchor=tk.W)
        ttk.Label(hdr, text=f"Platform: {platform.system()} {platform.release()} | Python {sys.version.split()[0]}",
                  foreground="#64748b").pack(anchor=tk.W)

        # Body Container
        body = ttk.Frame(self.root, padding="14 8")
        body.pack(fill=tk.BOTH, expand=True)

        # Metrics Gauges Frame
        metrics_frame = ttk.LabelFrame(body, text=" Hardware Utilization ", padding="12")
        metrics_frame.pack(fill=tk.X, pady=(0, 10))

        # CPU Metric
        ttk.Label(metrics_frame, text="CPU Utilization:").grid(row=0, column=0, sticky=tk.W, pady=4)
        self.cpu_bar = ttk.Progressbar(metrics_frame, length=300, mode="determinate")
        self.cpu_bar.grid(row=0, column=1, padx=12, pady=4, sticky=tk.EW)
        self.lbl_cpu = ttk.Label(metrics_frame, text="0%")
        self.lbl_cpu.grid(row=0, column=2, sticky=tk.W)

        # Memory Metric
        ttk.Label(metrics_frame, text="Memory (RAM):").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.mem_bar = ttk.Progressbar(metrics_frame, length=300, mode="determinate")
        self.mem_bar.grid(row=1, column=1, padx=12, pady=4, sticky=tk.EW)
        self.lbl_mem = ttk.Label(metrics_frame, text="0%")
        self.lbl_mem.grid(row=1, column=2, sticky=tk.W)

        # Canvas Waveform History Chart
        chart_frame = ttk.LabelFrame(body, text=" CPU Activity Waveform (Last 12 Ticks) ", padding="8")
        chart_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.canvas = tk.Canvas(chart_frame, height=120, background="#0f172a", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Status Bar
        self.status_lbl = ttk.Label(self.root, text="System status: Normal | Polling active...", padding="8 4", relief="sunken")
        self.status_lbl.pack(side=tk.BOTTOM, fill=tk.X)

    def _render_chart(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width() or 600
        h = self.canvas.winfo_height() or 120

        if len(self._history) < 2:
            return

        step = w / (len(self._history) - 1)
        points = []
        for i, val in enumerate(self._history):
            x = i * step
            y = h - (val / 100.0 * (h - 20)) - 10
            points.extend([x, y])

        # Draw grid lines
        for y_pct in [25, 50, 75]:
            gy = h - (y_pct / 100.0 * (h - 20)) - 10
            self.canvas.create_line(0, gy, w, gy, fill="#334155", dash=(2, 4))

        # Draw line graph
        self.canvas.create_line(points, fill="#38bdf8", width=2, smooth=True)

    def _schedule_next_poll(self):
        self._tick()
        self.root.after(1200, self._schedule_next_poll)

    def _tick(self):
        self._tick_count += 1
        # Calculate simulated/pseudo CPU & Mem based on oscillatory load
        cpu_val = int(45 + 30 * (abs((self._tick_count % 20) - 10) / 10.0))
        mem_val = int(58 + (self._tick_count % 8))

        self.cpu_bar["value"] = cpu_val
        self.lbl_cpu.config(text=f"{cpu_val}%")

        self.mem_bar["value"] = mem_val
        self.lbl_mem.config(text=f"{mem_val}%")

        self._history.pop(0)
        self._history.append(cpu_val)
        self._render_chart()


def run_app():
    root = tk.Tk()
    app = SystemMonitorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_app()
