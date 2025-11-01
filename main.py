import tkinter as tk
import winsound
import threading
import time

class Metronome:
    def __init__(self, root):
        self.root = root
        self.root.title("Metronome")

        self.tempo = 80
        self.beat = 1
        self.started = False
        self.thread = None
        self.stop_event = threading.Event()

        time_signatures = ["2/4", "3/4", "4/4", "5/4", "6/4"]
        self.time_signature = tk.StringVar(self.root, value="4/4")

        self.subdivision = tk.IntVar(self.root, value=1)
        subdivisions = [
            ("Quarter", 1),
            ("Eighth", 2),
            ("Triplet", 3),
            ("Sixteenth", 4),
        ]

        self.tempo_label = tk.Label(self.root, text=f"{self.tempo} bpm", bg="#d3d3d3", borderwidth=2, relief="ridge", font=("Arial", 36))
        self.tempo_label.grid(row=0, column=1, padx=10, pady=10)

        self.tempo_word = tk.Label(self.root, bg="#d3d3d3", borderwidth=2, font=("Arial", 14))
        self.tempo_word.grid(row=1, column=1, pady=5)

        start_btn = tk.Button(self.root, text="Start", command=self.play_start, bg="#90EE90", width=10)
        start_btn.grid(row=2, column=0, padx=5, pady=5)

        stop_btn = tk.Button(self.root, text="Stop", command=self.stop, bg="#FF7F7F", width=10)
        stop_btn.grid(row=2, column=2, padx=5, pady=5)

        self.slider = tk.Scale(self.root, length=300, from_=40, to=220, orient=tk.HORIZONTAL, command=self.update_label, bg="#ADD8E6", troughcolor="#d3d3d3")
        self.slider.set(self.tempo)
        self.slider.grid(row=2, column=1, padx=10, pady=5)

        ts_select = tk.OptionMenu(self.root, self.time_signature, *time_signatures)
        ts_select.config(bg="#ADD8E6")
        ts_select.grid(row=3, column=1, pady=5)

        sub_frame = tk.Frame(self.root, bg="#d3d3d3", padx=10, pady=5)
        sub_frame.grid(row=4, column=1)
        tk.Label(sub_frame, text="Subdivision:", bg="#d3d3d3").pack()
        for text, val in subdivisions:
            tk.Radiobutton(sub_frame, text=text, variable=self.subdivision, value=val, bg="#d3d3d3").pack(anchor="w")

        self.update_label()

    def run_metronome(self):
        self.stop_event.clear()
        self.beat = 1
        next_time = time.perf_counter()

        while not self.stop_event.is_set():
            tempo = self.slider.get()
            sub = self.subdivision.get()
            interval = 60.0 / float(tempo)
            sub_interval = interval / sub
            ts_numerator = int(self.time_signature.get().split('/')[0])

            for s in range(sub):
                if self.stop_event.is_set():
                    return

                now = time.perf_counter()
                wait = next_time - now
                if wait > 0:
                    time.sleep(wait)

                is_downbeat = (self.beat == 1 and s == 0)
                is_main_beat = (s == 0)

                if is_main_beat:
                    self.root.after(0, lambda downbeat=is_downbeat: self.flash_beat(downbeat))

                duration = 50 if tempo < 180 else 30
                try:
                    if is_downbeat:
                        winsound.Beep(880, duration)
                    elif is_main_beat:
                        winsound.Beep(660, duration)
                    else:
                        winsound.Beep(440, duration)
                except RuntimeError:
                    pass

                next_time += sub_interval

            self.beat += 1
            if self.beat > ts_numerator:
                self.beat = 1

    def play_start(self):
        if self.started:
            return
        self.started = True
        self.stop_event.clear()
        self.thread = threading.Thread(target=self.run_metronome, daemon=True)
        self.thread.start()

    def stop(self):
        if not self.started:
            return
        self.stop_event.set()
        self.started = False
        if self.thread is not None:
            self.thread.join(timeout=0.2)
            self.thread = None
        self.tempo_label.configure(bg="#d3d3d3")

    def flash_beat(self, downbeat: bool):
        color = "#FFD700" if downbeat else "#EEE8AA"
        self.tempo_label.configure(bg=color)
        self.root.after(70, lambda: self.tempo_label.configure(bg="#d3d3d3"))

    def update_label(self, event=None):
        self.tempo = int(self.slider.get())
        self.tempo_label.configure(text=f"{self.tempo} bpm")

        if self.tempo <= 60:
            text = "Largo"
        elif self.tempo <= 76:
            text = "Adagio"
        elif self.tempo <= 108:
            text = "Andante"
        elif self.tempo <= 120:
            text = "Allegretto"
        elif self.tempo <= 156:
            text = "Allegro"
        elif self.tempo <= 200:
            text = "Presto"
        else:
            text = "Prestissimo"

        self.tempo_word.configure(text=text)


def main():
    root = tk.Tk()
    Metronome(root)
    root.mainloop()

if __name__ == "__main__":
    main()
