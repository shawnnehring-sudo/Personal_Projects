from dataclasses import dataclass
import time

from song_parser import SongEvent, KEY_MIN, KEY_MAX

OFF = (0, 0, 0)
CURRENT = (0, 255, 0)       # press now
NEXT = (255, 180, 0)        # next event
LATER = (0, 90, 255)        # event after next
WRONG = (255, 0, 0)


@dataclass
class PlaybackState:
    event_index: int = 0
    running: bool = False
    mode: str = "guided"
    started_at: float = 0.0
    pause_offset: float = 0.0


class PlaybackEngine:
    def __init__(self, on_lights_changed=None, on_status_changed=None):
        self.events: list[SongEvent] = []
        self.state = PlaybackState()
        self.remaining: set[int] = set()
        self.on_lights_changed = on_lights_changed
        self.on_status_changed = on_status_changed
        self.wrong_note = None
        self.wrong_until = 0.0

    def load(self, events: list[SongEvent]):
        self.events = events
        self.restart(start_running=False)

    def restart(self, start_running=False):
        self.state = PlaybackState(
            event_index=0,
            running=start_running,
            mode=self.state.mode,
            started_at=time.monotonic(),
            pause_offset=0.0,
        )
        self._reset_remaining()
        self._emit()

    def set_mode(self, mode: str):
        if mode not in {"guided", "timed"}:
            raise ValueError("mode must be 'guided' or 'timed'")
        self.state.mode = mode
        self.restart(start_running=False)

    def start(self):
        if not self.events:
            return
        if self.state.running:
            return
        self.state.running = True
        self.state.started_at = time.monotonic() - self.state.pause_offset
        self._emit()

    def pause(self):
        if not self.state.running:
            return
        self.state.pause_offset = time.monotonic() - self.state.started_at
        self.state.running = False
        self._emit()

    def elapsed(self) -> float:
        if self.state.running:
            return time.monotonic() - self.state.started_at
        return self.state.pause_offset

    def note_pressed(self, midi_note: int):
        if not self.events or self.finished:
            return

        if self.state.mode != "guided":
            return

        if midi_note in self.remaining:
            self.remaining.remove(midi_note)
            if not self.remaining:
                self._advance_guided()
        else:
            self.wrong_note = midi_note
            self.wrong_until = time.monotonic() + 0.25

        self._emit()

    def update(self):
        if self.state.running and self.state.mode == "timed" and self.events:
            now = self.elapsed()
            # Advance through all events whose next start time has arrived.
            while (
                self.state.event_index + 1 < len(self.events)
                and now >= self.events[self.state.event_index + 1].time
            ):
                self.state.event_index += 1
                self._reset_remaining()

        if self.wrong_note is not None and time.monotonic() >= self.wrong_until:
            self.wrong_note = None

        self._emit()

    def _advance_guided(self):
        if self.state.event_index + 1 < len(self.events):
            self.state.event_index += 1
            self._reset_remaining()
        else:
            self.state.event_index = len(self.events)

    def _reset_remaining(self):
        if self.events and self.state.event_index < len(self.events):
            self.remaining = set(self.events[self.state.event_index].notes)
        else:
            self.remaining = set()

    @property
    def finished(self):
        return bool(self.events) and self.state.event_index >= len(self.events)

    def led_frame(self):
        frame = [OFF for _ in range(61)]

        if not self.events or self.finished:
            return frame

        i = self.state.event_index

        # Current event.
        current_notes = (
            self.remaining
            if self.state.mode == "guided"
            else set(self.events[i].notes)
        )
        for note in current_notes:
            frame[note - KEY_MIN] = CURRENT

        # Preview next two events.
        if i + 1 < len(self.events):
            for note in self.events[i + 1].notes:
                idx = note - KEY_MIN
                if frame[idx] == OFF:
                    frame[idx] = NEXT

        if i + 2 < len(self.events):
            for note in self.events[i + 2].notes:
                idx = note - KEY_MIN
                if frame[idx] == OFF:
                    frame[idx] = LATER

        if self.wrong_note is not None and KEY_MIN <= self.wrong_note <= KEY_MAX:
            frame[self.wrong_note - KEY_MIN] = WRONG

        return frame

    def status_text(self):
        if not self.events:
            return "Load a song to begin."
        if self.finished:
            return "Song complete!"
        event = self.events[self.state.event_index]
        return (
            f"Event {self.state.event_index + 1}/{len(self.events)}  |  "
            f"t={self.elapsed():.2f}s  |  "
            f"notes={', '.join(note_name(n) for n in event.notes)}"
        )

    def _emit(self):
        if self.on_lights_changed:
            self.on_lights_changed(self.led_frame())
        if self.on_status_changed:
            self.on_status_changed(self.status_text())


def note_name(midi_note: int):
    names = ["C", "C#", "D", "D#", "E", "F",
             "F#", "G", "G#", "A", "A#", "B"]
    octave = midi_note // 12 - 1
    return f"{names[midi_note % 12]}{octave}"
