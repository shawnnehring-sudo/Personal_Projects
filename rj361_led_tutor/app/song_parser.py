from dataclasses import dataclass
from pathlib import Path
import json

KEY_MIN = 36   # C2 on the RJ361
KEY_MAX = 96   # C7 on the RJ361


@dataclass
class SongEvent:
    time: float
    notes: list[int]
    duration: float = 0.5


def _validate(events: list[SongEvent]) -> list[SongEvent]:
    cleaned = []
    for event in events:
        notes = sorted(set(int(n) for n in event.notes))
        bad = [n for n in notes if n < KEY_MIN or n > KEY_MAX]
        if bad:
            raise ValueError(
                f"Song contains notes outside the RJ361 range C2-C7 "
                f"(MIDI {KEY_MIN}-{KEY_MAX}): {bad}"
            )
        if notes:
            cleaned.append(
                SongEvent(float(event.time), notes, float(event.duration))
            )
    return cleaned


def load_json_song(path: str | Path) -> list[SongEvent]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    events = [
        SongEvent(
            time=item["time"],
            notes=item["notes"],
            duration=item.get("duration", 0.5),
        )
        for item in data
    ]
    return _validate(events)


def load_midi_song(path: str | Path, group_window: float = 0.015) -> list[SongEvent]:
    """
    Convert MIDI note-on messages into groups of notes that begin together.

    Mido's MidiFile iterator exposes delta times in seconds, taking tempo
    changes into account. Notes whose start times are within group_window
    seconds are treated as one chord/event.
    """
    try:
        import mido
    except ImportError as exc:
        raise RuntimeError(
            "MIDI support requires mido. Install it with: pip install mido"
        ) from exc

    midi = mido.MidiFile(str(path))
    absolute_time = 0.0
    starts: list[tuple[float, int]] = []

    for msg in midi:
        absolute_time += float(msg.time)
        if msg.type == "note_on" and msg.velocity > 0:
            starts.append((absolute_time, int(msg.note)))

    if not starts:
        raise ValueError("No note-on events were found in this MIDI file.")

    groups: list[tuple[float, list[int]]] = []
    current_time, first_note = starts[0]
    current_notes = [first_note]

    for event_time, note in starts[1:]:
        if abs(event_time - current_time) <= group_window:
            current_notes.append(note)
        else:
            groups.append((current_time, current_notes))
            current_time = event_time
            current_notes = [note]
    groups.append((current_time, current_notes))

    events: list[SongEvent] = []
    for i, (start, notes) in enumerate(groups):
        if i + 1 < len(groups):
            duration = max(0.05, groups[i + 1][0] - start)
        else:
            duration = 0.5
        events.append(SongEvent(start, notes, duration))

    # Normalize so the first note starts at t=0.
    offset = events[0].time
    for event in events:
        event.time -= offset

    return _validate(events)


def load_song(path: str | Path) -> list[SongEvent]:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".json":
        return load_json_song(path)
    if suffix in {".mid", ".midi"}:
        return load_midi_song(path)
    raise ValueError("Supported song formats are .json, .mid, and .midi.")
