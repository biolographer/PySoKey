import argparse
import tkinter as tk
from mido import Message, open_output

# Define MIDI note mapping
char_to_note = {
    '1': 64, '2': 66, '3': 68, '4': 70, '5': 72, '6': 74, '7': 76, '8': 78, '9': 80, '0': 82, "'": 84,
    'q': 59, 'w': 61, 'e': 63, 'r': 65, 't': 67, 'z': 69, 'u': 71, 'i': 73, 'o': 75, 'p': 77, 'ü': 79,
    'a': 54, 's': 56, 'd': 58, 'f': 60, 'g': 62, 'h': 64, 'j': 66, 'k': 68, 'l': 70, 'ö': 72, 'ä': 74,
    'y': 49, 'x': 51, 'c': 53, 'v': 55, 'b': 57, 'n': 59, 'm': 61, ',': 63, '.': 65, '-': 67
}

edo_12_pitch = {
    '1': 'E4',  '2': 'F#4', '3': 'G#4', '4': 'A#4', '5': 'C5',  '6': 'D5',
    '7': 'E5',  '8': 'F#5', '9': 'G#5', '0': 'A#5', "'": 'C6',
    'q': 'B3',  'w': 'C#4', 'e': 'D#4', 'r': 'F4',  't': 'G4',
    'z': 'A4',  'u': 'B4',  'i': 'C#5', 'o': 'D#5', 'p': 'F5',
    'ü': 'G5',
    'a': 'F#3', 's': 'G#3', 'd': 'A#3', 'f': 'C4',  'g': 'D4',
    'h': 'E4',  'j': 'F#4', 'k': 'G#4', 'l': 'A#4', 'ö': 'C5',
    'ä': 'D5',
    'y': 'C#3', 'x': 'D#3', 'c': 'F3',  'v': 'G3',  'b': 'A3',
    'n': 'B3',  'm': 'C#4', ',': 'D#4', '.': 'F4',  '-': 'G4'
}

tuning_dict = {
                '12edo': [
                    ['E4', 'F#4', 'G#4', 'A#4', 'C5', 'D5', 'E5', 'F#5', 'G#5', 'A#5', 'C6'],  
                    ['B3', 'C#4', 'D#4', 'F4', 'G4', 'A4', 'B4', 'C#5', 'D#5', 'F5', 'G5'],  
                    ['F#3', 'G#3', 'A#3', 'C4', 'D4', 'E4', 'F#4', 'G#4', 'A#4', 'C5', 'D5'], 
                    ['C#3', 'D#3', 'F3', 'G3', 'A3', 'B3', 'C#4', 'D#4', 'F4', 'G4']],
                '19edo': [
                    ['C4', 'C~4', 'D~4', 'D4', 'D~#4', 'E~4', 'E4', 'F4', 'F~4', 'G~4', 'G4'],  
                    ['G~#4', 'A~4', 'A4', 'A~#4', 'B~4', 'B4', 'C5', 'C~5', 'D~5', 'D5', 'D~#5'],  
                    ['E~5', 'E5', 'F5', 'F~5', 'G~5', 'G5', 'G~#5', 'A~5', 'A5', 'A~#5', 'B~5'], 
                    ['B5', 'C6', 'C~6', 'D~6', 'D6', 'D~#6', 'E~6', 'E6', 'F6', 'F~6']],
                '31edo': [
                    ['C4', 'C^4', 'C#4', 'C#^4', 'D4', 'D^4', 'D#4', 'D#^4', 'E4', 'F4', 'F^4'],  
                    ['F#4', 'F#^4', 'G4', 'G^4', 'G#4', 'G#^4', 'A4', 'A^4', 'A#4', 'A#^4', 'B4'],  
                    ['C5', 'C^5', 'C#5', 'C#^5', 'D5', 'D^5', 'D#5', 'D#^5', 'E5', 'F5', 'F^5'], 
                    ['F#5', 'F#^5', 'G5', 'G^5', 'G#5', 'G#^5', 'A5', 'A^5', 'A#5', 'A#^5']]
            }


# MIDI Setup
try:
    midi_out = open_output()
except IOError:
    midi_out = None
    print("No MIDI output device found.")

def send_note_on(note):
    if midi_out:
        midi_out.send(Message('note_on', note=note, velocity=100))

def send_note_off(note):
    if midi_out:
        midi_out.send(Message('note_off', note=note))

# GUI setup
class JammerApp:
    def __init__(self, root, keyboard='qwertz', tuning='12edo'):
        self.keyboard = keyboard
        self.root = root
        self.char_to_widget = {}
        self.tuning = tuning

        self.label = tk.Label(root, text="I need focus to play MIDI out", bg="grey")
        self.label.pack(fill='x')

        self.midi_label = tk.Label(root, text="MIDI", bg="#DDD", width=10)
        self.midi_label.pack()

        self.keyboard_frame = tk.Frame(root)
        self.keyboard_frame.pack(padx=10, pady=10)

        self.create_keyboard_layout()

        root.bind("<KeyPress>", self.on_key_press)
        root.bind("<KeyRelease>", self.on_key_release)
        root.bind("<FocusIn>", self.on_focus)
        root.bind("<FocusOut>", self.on_blur)

    def create_keyboard_layout(self):
        # Define visual rows
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
        
        key_width = 50  # Width of each key in pixels
        key_height = 50
        x_padding = 5
        y_padding = 5
        row_offset = key_width // 2  # Half a key width

        for r, row in enumerate(tuning):
            for c, char in enumerate(row):
                x = c * (key_width + x_padding) + r * row_offset
                y = r * (key_height + y_padding)
                label = tk.Label(self.keyboard_frame, text=char, width=4, height=2,
                                 relief="raised", borderwidth=2, bg="#EEE", font=("Courier", 14))
                label.place(x=x, y=y, width=key_width, height=key_height)
                self.char_to_widget[keyboard_rows[r][c]] = label

        # Set a fixed size to avoid clipping
        total_width = len(keyboard_rows[0]) * (key_width + x_padding) + row_offset * len(keyboard_rows)
        total_height = len(keyboard_rows) * (key_height + y_padding)
        self.keyboard_frame.config(width=total_width, height=total_height)

    def tune(self, tuning):
        return tuning_dict[tuning]

    def on_key_press(self, event):
        self.midi_label.config(bg="lightgrey")
        char = event.char.lower()
        note = char_to_note.get(char)
        if note is not None:
            send_note_on(note)
        if char in self.char_to_widget:
            self.char_to_widget[char].config(bg="lightblue")

    def on_key_release(self, event):
        self.midi_label.config(bg="#DDD")
        char = event.char.lower()
        note = char_to_note.get(char)
        if note is not None:
            send_note_off(note)
        if char in self.char_to_widget:
            self.char_to_widget[char].config(bg="#EEE")

    def on_focus(self, event):
        self.label.config(text="listening to keyboard", bg="lightgrey")

    def on_blur(self, event):
        self.label.config(text="no focus, no midi", bg="grey")
        # reset visual keys
        for label in self.char_to_widget.values():
            label.config(bg="#EEE")

def main():
    parser = argparse.ArgumentParser(description="Start the Jammer MIDI keyboard")
    parser.add_argument('--tuning', choices=['12edo', '19edo', '31edo'], default='12edo',
                        help='Choose tuning system: 12edo (default), 19edo, or 31edo')
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
