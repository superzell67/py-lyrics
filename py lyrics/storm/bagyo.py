import tkinter as tk
import pygame
import time
import random
import os

os.system("cls")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LYRICS = [
    (0, "Ako ang bagyooooo"),
    (2.5, "Kulimlim ng langit"),
    (4.5, "sa inyong dalawa"),
    (8, "Bulong ko sa hangin"),
    (10, "sana 'di kayo masaya"),
    (14, "Sa tibay ng bahay"),
    (16, "na titirhan niyo"),
    (19, "Tatangayin ko bawat yeroooo"),
]

BOX_W, BOX_H = 350, 300
FONT = ("Helvetica", 25, "bold")
BG_COLOR = "#fdfdf5"
FG_COLOR = "#111111"
TRANSPARENT = "#010101"
CLOUD_OUTLINE = "#111111"

BOLT_LAYERS = [
    (9, "#6f9bff"),
    (5, "#bcd4ff"),
    (2, "#ffffff"),
]

BOLT_ANCHORS = [
    ((62, 95), (82, 215)),
    ((292, 90), (268, 218)),
    ((150, 178), (172, 222)),
]

CLOUD_PARTS = [
    (15, 120, 335, 235),
    (30, 85, 150, 210),
    (95, 30, 260, 190),
    (205, 65, 325, 205),
]

RISE_SPEED = 125
BOTTOM_SPAWN_OFFSET = 0
GAP = 40


def jagged(x1, y1, x2, y2, rough=22, depth=5):
    pts = [(x1, y1), (x2, y2)]

    for _ in range(depth):
        new = [pts[0]]

        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            mx = (ax + bx) / 2 + random.uniform(-rough, rough)
            my = (ay + by) / 2 + random.uniform(-rough, rough) * 0.3
            new.extend([(mx, my), (bx, by)])

        pts = new
        rough *= 0.55

    return pts


class LyricCard:
    def __init__(self, parent, text, x, y):
        self.win = tk.Toplevel(parent)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.configure(bg=TRANSPARENT)

        try:
            self.win.attributes("-transparentcolor", TRANSPARENT)
        except tk.TclError:
            pass

        self.win.geometry(f"{BOX_W}x{BOX_H}+{int(x)}+{int(y)}")
        self.win.resizable(False, False)
        self.full_text = text

        self.canvas = tk.Canvas(
            self.win,
            width=BOX_W,
            height=BOX_H,
            bg=TRANSPARENT,
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack(fill="both", expand=True)

        self.outline_ids = [
            self.canvas.create_rectangle(
                0,
                0,
                BOX_W,
                BOX_H,
                fill=CLOUD_OUTLINE,
                outline=CLOUD_OUTLINE
            )
        ]

        self.fill_ids = [
            self.canvas.create_rectangle(
                4,
                4,
                BOX_W - 4,
                BOX_H - 4,
                fill=BG_COLOR,
                outline=BG_COLOR
            )
        ]

        self.bolt_ids = []

        self.text_id = self.canvas.create_text(
            BOX_W // 2,
            BOX_H // 2,
            text="",
            font=FONT,
            fill=FG_COLOR,
            width=BOX_W - 50,
            justify="center"
        )

        self.x = x
        self.y = float(y)
        self.flip_state = False
        self.typewriter_index = 0

        self.strike()
        self.typewriter()

    def strike(self):
        for item in self.bolt_ids:
            self.canvas.delete(item)

        self.bolt_ids = []

        if random.random() < 0.35:
            return

        anchors = random.sample(
            BOLT_ANCHORS,
            random.choice([1, 2])
        )

        for (sx, sy), (ex, ey) in anchors:
            main = jagged(
                sx + random.uniform(-6, 6),
                sy,
                ex + random.uniform(-6, 6),
                ey
            )

            paths = [main]

            for _ in range(random.choice([1, 2])):
                k = random.randint(
                    len(main) // 5,
                    len(main) * 2 // 3
                )

                px, py = main[k]
                direction = random.choice([-1, 1])
                bx = px + direction * random.uniform(22, 42)
                by = min(py + random.uniform(25, 50), 222)

                paths.append(
                    jagged(px, py, bx, by, rough=10, depth=3)
                )

            for width, color in BOLT_LAYERS:
                for index, path in enumerate(paths):
                    line_width = (
                        width
                        if index == 0
                        else max(1, int(width * 0.6))
                    )

                    flat = [
                        coordinate
                        for point in path
                        for coordinate in point
                    ]

                    self.bolt_ids.append(
                        self.canvas.create_line(
                            *flat,
                            fill=color,
                            width=line_width,
                            capstyle="round",
                            joinstyle="round"
                        )
                    )

        self.canvas.tag_raise(self.text_id)

    def set_colors(self, cloud_fill, cloud_outline, text_color):
        for item in self.fill_ids:
            self.canvas.itemconfig(
                item,
                fill=cloud_fill,
                outline=cloud_fill
            )

        for item in self.outline_ids:
            self.canvas.itemconfig(
                item,
                fill=cloud_outline,
                outline=cloud_outline
            )

        self.canvas.itemconfig(
            self.text_id,
            fill=text_color
        )

    def typewriter(self):
        if not self.win.winfo_exists():
            return

        if self.typewriter_index <= len(self.full_text):
            self.canvas.itemconfig(
                self.text_id,
                text=self.full_text[:self.typewriter_index]
            )

            self.typewriter_index += 1
            self.win.after(75, self.typewriter)

    def rise(self, dy):
        self.y -= dy

        self.win.geometry(
            f"{BOX_W}x{BOX_H}+{int(self.x)}+{int(self.y)}"
        )

    def is_offscreen(self):
        return self.y + BOX_H < -50


class LyricFloatApp:
    def __init__(self, root):
        self.root = root
        self.screen_w = root.winfo_screenwidth()
        self.screen_h = root.winfo_screenheight()

        self.next_lyric_idx = 0
        self.boxes = []
        self.last_frame_time = None
        self.current_side = "left"
        self.closed = False
        self.after_ids = set()
        self.audio_ready = False

        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.bind_all("<Escape>", self.handle_escape)
        self.root.withdraw()

        self.start()

    def schedule(self, delay, callback):
        if self.closed:
            return

        after_id_holder = []

        def run_callback():
            if after_id_holder:
                self.after_ids.discard(after_id_holder[0])

            if not self.closed:
                callback()

        after_id = self.root.after(delay, run_callback)
        after_id_holder.append(after_id)
        self.after_ids.add(after_id)

    def handle_escape(self, event=None):
        self.close()

    def random_safe_x(self):
        center_x = self.screen_w // 2
        spacing = BOX_W + 60
        left_x = center_x - spacing
        right_x = center_x + 60

        if self.current_side == "left":
            self.current_side = "right"
            return left_x

        self.current_side = "left"
        return right_x

    def start(self):
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(
                os.path.join(BASE_DIR, "sound.mp3")
            )
            pygame.mixer.music.play()
            self.audio_ready = True

        except pygame.error as error:
            print(f"Audio error: {error}")
            self.audio_ready = False

        self.start_time = time.time()
        self.last_frame_time = self.start_time

        self.tick()
        self.flip_all()
        self.schedule(250, self.check_finished)

    def flip_all(self):
        if self.closed:
            return

        for box in self.boxes:
            if box.flip_state:
                box.set_colors("white", "#222222", "black")
            else:
                box.set_colors("#2b2b33", "white", "white")

            box.flip_state = not box.flip_state
            box.strike()

        if self.next_lyric_idx < len(LYRICS) or self.boxes:
            self.schedule(150, self.flip_all)

    def tick(self):
        if self.closed:
            return

        now = time.time()
        elapsed = now - self.start_time
        dt = now - self.last_frame_time
        self.last_frame_time = now

        while (
            self.next_lyric_idx < len(LYRICS)
            and LYRICS[self.next_lyric_idx][0] <= elapsed
        ):
            _, text = LYRICS[self.next_lyric_idx]
            x = self.random_safe_x()

            if self.boxes:
                y = self.boxes[-1].y + BOX_H + GAP
            else:
                y = (
                    self.screen_h
                    - BOX_H
                    - BOTTOM_SPAWN_OFFSET
                )

            box = LyricCard(self.root, text, x, y)
            self.boxes.append(box)
            self.next_lyric_idx += 1

        dy = RISE_SPEED * dt

        for box in self.boxes:
            box.rise(dy)

        still_visible = []

        for box in self.boxes:
            if box.is_offscreen():
                try:
                    box.win.destroy()
                except tk.TclError:
                    pass
            else:
                still_visible.append(box)

        self.boxes = still_visible

        if self.next_lyric_idx < len(LYRICS) or self.boxes:
            self.schedule(16, self.tick)

    def check_finished(self):
        if self.closed:
            return

        audio_finished = (
            not self.audio_ready
            or not pygame.mixer.get_init()
            or not pygame.mixer.music.get_busy()
        )

        lyrics_finished = (
            self.next_lyric_idx >= len(LYRICS)
            and not self.boxes
        )

        if lyrics_finished and audio_finished:
            self.close()
            return

        self.schedule(250, self.check_finished)

    def close(self):
        if self.closed:
            return

        self.closed = True

        for after_id in list(self.after_ids):
            try:
                self.root.after_cancel(after_id)
            except tk.TclError:
                pass

        self.after_ids.clear()

        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                pygame.mixer.quit()
        except pygame.error:
            pass

        for box in self.boxes:
            try:
                box.win.destroy()
            except tk.TclError:
                pass

        self.boxes.clear()

        try:
            self.root.destroy()
        except tk.TclError:
            pass


if __name__ == "__main__":
    root = tk.Tk()
    app = LyricFloatApp(root)
    root.mainloop()