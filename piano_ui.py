import tkinter as tk

KEY_MIN = 36
KEY_MAX = 96

WHITE_NOTES = {0, 2, 4, 5, 7, 9, 11}
BLACK_NOTES = {1, 3, 6, 8, 10}


class PianoCanvas(tk.Canvas):
    def __init__(self, master, on_note_pressed, **kwargs):
        super().__init__(master, **kwargs)
        self.on_note_pressed = on_note_pressed
        self.key_items = {}
        self.item_to_note = {}
        self.colors = [(0, 0, 0)] * 61

        self.bind("<Configure>", lambda _e: self.redraw())
        self.bind("<Button-1>", self._click)

    def redraw(self):
        self.delete("all")
        self.key_items.clear()
        self.item_to_note.clear()

        width = max(800, self.winfo_width())
        height = max(240, self.winfo_height())

        notes = list(range(KEY_MIN, KEY_MAX + 1))
        whites = [n for n in notes if n % 12 in WHITE_NOTES]
        white_w = width / len(whites)
        black_w = white_w * 0.62
        black_h = height * 0.60

        white_x = {}
        wi = 0

        # White keys first.
        for note in notes:
            if note % 12 not in WHITE_NOTES:
                continue
            x0 = wi * white_w
            x1 = x0 + white_w
            white_x[note] = x0
            item = self.create_rectangle(
                x0, 0, x1, height,
                fill=self._fill_for(note, default="white"),
                outline="#777",
                width=1,
            )
            self.key_items[note] = item
            self.item_to_note[item] = note

            # Label C notes and endpoints.
            if note % 12 == 0 or note in {KEY_MIN, KEY_MAX}:
                self.create_text(
                    (x0 + x1) / 2, height - 15,
                    text=self.note_name(note),
                    fill="black",
                    font=("Segoe UI", 9),
                )
            wi += 1

        # Black keys overlay.
        previous_white_x = None
        wi = 0
        for note in notes:
            pc = note % 12
            if pc in WHITE_NOTES:
                previous_white_x = white_x[note]
                continue
            if pc not in BLACK_NOTES or previous_white_x is None:
                continue

            x_center = previous_white_x + white_w
            x0 = x_center - black_w / 2
            x1 = x_center + black_w / 2
            item = self.create_rectangle(
                x0, 0, x1, black_h,
                fill=self._fill_for(note, default="#111"),
                outline="#333",
                width=1,
            )
            self.key_items[note] = item
            self.item_to_note[item] = note

        # Small LED guide dots at the top, one per note.
        for note in notes:
            item = self.key_items.get(note)
            if not item:
                continue
            x0, y0, x1, y1 = self.coords(item)
            cx = (x0 + x1) / 2
            rgb = self.colors[note - KEY_MIN]
            fill = self.rgb_hex(rgb) if rgb != (0, 0, 0) else "#444"
            self.create_oval(
                cx - 4, 5, cx + 4, 13,
                fill=fill, outline=""
            )

    def set_colors(self, colors):
        self.colors = list(colors)
        self.redraw()

    def _fill_for(self, note, default):
        rgb = self.colors[note - KEY_MIN]
        if rgb == (0, 0, 0):
            return default
        # Use a lightened version for white keys so labels remain visible.
        if note % 12 in WHITE_NOTES:
            r, g, b = rgb
            r = 150 + r * 105 // 255
            g = 150 + g * 105 // 255
            b = 150 + b * 105 // 255
            return self.rgb_hex((r, g, b))
        return self.rgb_hex(rgb)

    def _click(self, event):
        # Canvas find_overlapping returns in stacking order; pick topmost piano key.
        items = self.find_overlapping(event.x, event.y, event.x, event.y)
        for item in reversed(items):
            if item in self.item_to_note:
                self.on_note_pressed(self.item_to_note[item])
                return

    @staticmethod
    def rgb_hex(rgb):
        return "#%02x%02x%02x" % rgb

    @staticmethod
    def note_name(midi_note):
        names = ["C", "C#", "D", "D#", "E", "F",
                 "F#", "G", "G#", "A", "A#", "B"]
        return f"{names[midi_note % 12]}{midi_note // 12 - 1}"
