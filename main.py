from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from song_parser import load_song
from playback_engine import PlaybackEngine
from piano_ui import PianoCanvas
from esp32_client import ESP32Client


class TutorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RJ361 LED Piano Tutor")
        self.geometry("1180x520")
        self.minsize(900, 430)

        self.client = ESP32Client()
        self.last_frame = None

        self.engine = PlaybackEngine(
            on_lights_changed=self._lights_changed,
            on_status_changed=self._status_changed,
        )

        self._build_ui()
        self.after(20, self._tick)

        # Load bundled demo automatically if found.
        demo = Path(__file__).resolve().parent.parent / "songs" / "demo_song.json"
        if demo.exists():
            self._load_path(demo)

    def _build_ui(self):
        controls = ttk.Frame(self, padding=10)
        controls.pack(fill="x")

        ttk.Button(controls, text="Load Song", command=self._load_song).grid(
            row=0, column=0, padx=4
        )
        ttk.Button(controls, text="Start", command=self.engine.start).grid(
            row=0, column=1, padx=4
        )
        ttk.Button(controls, text="Pause", command=self.engine.pause).grid(
            row=0, column=2, padx=4
        )
        ttk.Button(
            controls, text="Restart",
            command=lambda: self.engine.restart(start_running=False)
        ).grid(row=0, column=3, padx=4)

        ttk.Label(controls, text="Mode:").grid(row=0, column=4, padx=(20, 4))
        self.mode = tk.StringVar(value="guided")
        ttk.Radiobutton(
            controls, text="Guided", variable=self.mode,
            value="guided", command=self._mode_changed
        ).grid(row=0, column=5)
        ttk.Radiobutton(
            controls, text="Timed", variable=self.mode,
            value="timed", command=self._mode_changed
        ).grid(row=0, column=6)

        ttk.Label(controls, text="ESP32 IP:").grid(
            row=0, column=7, padx=(25, 4)
        )
        self.host = tk.StringVar()
        host_entry = ttk.Entry(controls, width=15, textvariable=self.host)
        host_entry.grid(row=0, column=8)
        ttk.Button(
            controls, text="Apply", command=self._apply_host
        ).grid(row=0, column=9, padx=4)

        legend = ttk.Label(
            self,
            text="Green = press now    Yellow = next    Blue = later    Red = wrong key",
            padding=(10, 0, 10, 8),
        )
        legend.pack(anchor="w")

        self.song_label = ttk.Label(self, text="Song: none", padding=(10, 0, 10, 4))
        self.song_label.pack(anchor="w")

        self.status = tk.StringVar(value="Load a song to begin.")
        ttk.Label(
            self, textvariable=self.status,
            font=("Segoe UI", 11, "bold"),
            padding=(10, 0, 10, 8)
        ).pack(anchor="w")

        self.piano = PianoCanvas(
            self,
            on_note_pressed=self.engine.note_pressed,
            background="#222",
            highlightthickness=0,
        )
        self.piano.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _load_song(self):
        path = filedialog.askopenfilename(
            title="Load song",
            filetypes=[
                ("Supported songs", "*.json *.mid *.midi"),
                ("JSON song", "*.json"),
                ("MIDI song", "*.mid *.midi"),
                ("All files", "*.*"),
            ],
        )
        if path:
            self._load_path(path)

    def _load_path(self, path):
        try:
            events = load_song(path)
            self.engine.load(events)
            self.song_label.config(
                text=f"Song: {Path(path).name} ({len(events)} note events)"
            )
        except Exception as exc:
            messagebox.showerror("Could not load song", str(exc))

    def _mode_changed(self):
        self.engine.set_mode(self.mode.get())

    def _apply_host(self):
        self.client.set_host(self.host.get())
        if self.client.enabled:
            self.status.set(
                f"ESP32 target set to {self.client.host}:4210. "
                "Start the ESP32 firmware and use its Serial Monitor to find its IP."
            )

    def _lights_changed(self, frame):
        # Avoid redrawing/transmitting identical frames at 50 Hz.
        if frame == self.last_frame:
            return
        self.last_frame = list(frame)
        self.piano.set_colors(frame)
        try:
            self.client.send_frame(frame)
        except OSError as exc:
            self.status.set(f"ESP32 network error: {exc}")

    def _status_changed(self, text):
        self.status.set(text)

    def _tick(self):
        self.engine.update()
        self.after(20, self._tick)


if __name__ == "__main__":
    TutorApp().mainloop()
