import argparse
import tkinter as tk
from mido import Message, open_output

# Define MIDI note mapping
char_to_note = {
    '1': 64, '2': 66, '3': 68, '4': 70, '5': 72, '6': 74, '7': 76, '8': 78, '9': 80, '0': 82, "'": 84,
    'q': 59, 'w': 61, 'e': 63, 'r': 65, 't': 67, 'z': 69, 'u': 71, 'i': 73, 'o': 75, 'p': 77, 'ü': 79,
    'a': 54, 's': 56, 'd': 58, 'f': 60, 'g': 62, 'h': 64, 'j': 66, 'k': 68, 'l': 70, 'ö': 72, 'ä': 74,
    '<':48, 'y': 49, 'x': 51, 'c': 53, 'v': 55, 'b': 57, 'n': 59, 'm': 61, ',': 63, '.': 65, '-': 67
}


tuning_dict = {
                'wicki_hayden': [
                    ['E4', 'F#4', 'G#4', 'A#4', 'C5', 'D5', 'E5', 'F#5', 'G#5', 'A#5', 'C6'],  
                    ['B3', 'C#4', 'D#4', 'F4', 'G4', 'A4', 'B4', 'C#5', 'D#5', 'F5', 'G5'],  
                    ['F#3', 'G#3', 'A#3', 'C4', 'D4', 'E4', 'F#4', 'G#4', 'A#4', 'C5', 'D5'], 
                    ['C#3', 'D#3', 'F3', 'G3', 'A3', 'B3', 'C#4', 'D#4', 'F4', 'G4']],

                'harmonic_table': [
                    ['F#3', 'A#3',  'D4',  'F#4',  'A#4',  'D5',  'F#5',  'A#5',  'D6',  'F#6',  'A#6'],
                        ['D#3', 'G3',   'B3',  'D#4',  'G4',   'B4',  'D#5',  'G5',   'B5',  'D#6',  'G6'],
                            ['C3',  'E3',   'G#3', 'C4',   'E4',   'G#4', 'C5',   'E5',   'G#5', 'C6',   'E6'],
                        ['F2',  'A2',   'C#3', 'F3',   'A3',   'C#4', 'F4',   'A4',   'C#5', 'F5',   'A5']
                ],

                '19edo': [
                    ['G~4', 'G4', 'G~#4', 'A~4', 'A4', 'A~#4', 'B~4', 'B4', 'C5', 'C~5', 'D~5'],  
                    ['D5', 'D~#5', 'E~5', 'E5', 'F5', 'F~5', 'G~5', 'G5', 'G~#5', 'A~5', 'A5'],  
                    ['B3', 'C~4', 'D~4', 'C4', 'D4', 'D~#4', 'E~4', 'E4', 'F4', 'F~4', 'G~4'], 
                    ['G4', 'G~#4', 'A~4', 'A4', 'A~#4', 'B~4', 'B4', 'C5', 'C~5', 'D~5']],
                '31edo': [
                    ['G#4', 'G#^4', 'A4', 'A^4', 'A#4', 'A#^4', 'B4', 'C5', 'C^5', 'C#5', 'C#^5'],  
                    ['D5', 'D^5', 'D#5', 'D#^5', 'E5', 'F5', 'F^5', 'F#5', 'F#^5', 'G5', 'G^5'],  
                    ['A#3', 'A#^3', 'B3', 'C4', 'C^4', 'C#4', 'C#^4', 'D4', 'D^4', 'D#4', 'D#^4'], 
                    ['E4', 'F4', 'F^4', 'F#4', 'F#^4', 'G4', 'G^4', 'G#4', 'G#^4', 'A4']
                ]
            }


# MIDI Setup
try:
    midi_out = open_output()
    print(f"Sending MIDI to: {midi_out.name}")
except IOError:
    midi_out = None
    print("No MIDI output device found.")

def send_note_on(note):
    if midi_out:
        midi_out.send(Message('note_on', note=note, velocity=100))

def send_note_off(note):
    if midi_out:
        midi_out.send(Message('note_off', note=note))

class JammerApp:
    def __init__(self, root, keyboard='qwertz', tuning='wicki_hayden'):
        self.keyboard = keyboard
        self.root = root
        self.char_to_widget = {}
        self.widget_bg_colors = {}  # Store original bg color
        self.tuning = tuning

        self.label = tk.Label(root, text="I need focus to play MIDI out", bg="grey")
        self.label.pack(fill='x')

        self.midi_label = tk.Label(root, text="MIDI", bg="#DDD", width=10)
        self.midi_label.pack()

        self.tuning_var = tk.StringVar(value=self.tuning)
        self.tuning_menu = tk.OptionMenu(root, self.tuning_var,
                                         'wicki_hayden', '19edo', '31edo', 'harmonic_table',
                                         command=self.change_tuning)
        self.tuning_menu.pack(pady=5)

        self.keyboard_frame = tk.Frame(root)
        self.keyboard_frame.pack(padx=10, pady=10)

        self.create_keyboard_layout()

        root.bind("<KeyPress>", self.on_key_press)
        root.bind("<KeyRelease>", self.on_key_release)
        root.bind("<FocusIn>", self.on_focus)
        root.bind("<FocusOut>", self.on_blur)

        self.active_notes = set()

    def tune(self, tuning):
        return tuning_dict[tuning]

    def create_keyboard_layout(self):
        for widget in self.keyboard_frame.winfo_children():
            widget.destroy()
        self.char_to_widget.clear()
        self.widget_bg_colors.clear()

        keyboard_rows = [
            list("1234567890'"),
            list("qwertzuiopü"),
            list("asdfghjklöä"),
            list("<yxcvbnm,.-")
        ]

        if self.keyboard != 'qwertz':
            keyboard_rows = [
                list("1234567890'"),
                list("qwertyuiopü"),
                list("asdfghjklöä"),
                list("<zxcvbnm,.-")
            ]

        tuning = self.tune(self.tuning)

        key_width = 50
        key_height = 50
        x_padding = 5
        y_padding = 5
        row_offset = key_width // 2

        for r, row in enumerate(tuning):
            for c, char in enumerate(row):
                x = c * (key_width + x_padding) + r * row_offset
                if r == len(tuning) - 1:
                    x = c * (key_width + x_padding) + row_offset
                y = r * (key_height + y_padding)

                # Determine background color
                if (self.tuning == 'harmonic_table' or self.tuning == 'wicki_hayden' ) and '#' in char:
                    bg_color = "#ababa7"
                else:
                    bg_color = "#EEE"

                label = tk.Label(self.keyboard_frame, text=char, width=4, height=2,
                                 relief="raised", borderwidth=2, bg=bg_color, font=("Courier", 14))
                label.place(x=x, y=y, width=key_width, height=key_height)

                if c < len(keyboard_rows[r]):
                    key = keyboard_rows[r][c]
                    self.char_to_widget[key] = label
                    self.widget_bg_colors[key] = bg_color

        total_width = len(keyboard_rows[0]) * (key_width + x_padding) + row_offset * len(keyboard_rows)
        total_height = len(keyboard_rows) * (key_height + y_padding)
        self.keyboard_frame.config(width=total_width, height=total_height)

    def change_tuning(self, new_tuning):
        self.tuning = new_tuning
        self.create_keyboard_layout()

    def on_key_press(self, event):
        self.midi_label.config(bg="lightgrey")
        char = event.char.lower()
        note = char_to_note.get(char)

        if note is not None and note not in self.active_notes:
            send_note_on(note)
            self.active_notes.add(note)

        if char in self.char_to_widget:
            self.char_to_widget[char].config(bg="lightblue")

    def on_key_release(self, event):
        self.midi_label.config(bg="#DDD")
        char = event.char.lower()
        note = char_to_note.get(char)

        if note is not None and note in self.active_notes:
            send_note_off(note)
            self.active_notes.remove(note)

        if char in self.char_to_widget:
            original_bg = self.widget_bg_colors.get(char, "#EEE")
            self.char_to_widget[char].config(bg=original_bg)

    def on_focus(self, event):
        self.label.config(text="listening to keyboard", bg="lightgrey")

    def on_blur(self, event):
        self.label.config(text="no focus, no midi", bg="grey")
        for key, label in self.char_to_widget.items():
            original_bg = self.widget_bg_colors.get(key, "#EEE")
            label.config(bg=original_bg)


def main():
    parser = argparse.ArgumentParser(description="Start the Jammer MIDI keyboard")
    parser.add_argument('--tuning', choices=['wicki_hayden', '19edo', '31edo', 'harmonic_table'], default='harmonic_table',
                        help='Choose tuning system: harmonic_table (default), wicki_hayden, 19edo, or 31edo')
    args = parser.parse_args()
    selected_tuning = args.tuning
    print(f"Using tuning: {selected_tuning}")

    root = tk.Tk()
    root.title("Jammer")

    if selected_tuning:
        app = JammerApp(root, tuning=selected_tuning)
    else:
        app = JammerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
