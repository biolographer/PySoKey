import tkinter as tk
from mido import Message, open_output

# Define the mappings
alphabet_keycodes = dict(zip(range(65, 91), "abcdefghijklmnopqrstuvwxyz"))
numeric_keycodes = {
    49: '1', 50: '2', 51: '3', 52: '4', 53: '5',
    54: '6', 55: '7', 56: '8', 57: '9', 48: '0'
}

def keycode_to_char(keycode):
    return alphabet_keycodes.get(keycode, numeric_keycodes.get(keycode, keycode))

char_to_note = {
    '1': 64, '2': 66, '3': 68, '4': 70, '5': 72, '6': 74, '7': 76, '8': 78, '9': 80, '0': 82,
    'q': 59, 'w': 61, 'e': 63, 'r': 65, 't': 67, 'y': 69, 'u': 71, 'i': 73, 'o': 75, 'p': 77,
    'a': 54, 's': 56, 'd': 58, 'f': 60, 'g': 62, 'h': 64, 'j': 66, 'k': 68, 'l': 70,
    'z': 49, 'x': 51, 'c': 53, 'v': 55, 'b': 57, 'n': 59, 'm': 61,
    ',': 63, '.': 65
}

def keycode_to_midinote(keycode):
    char = keycode_to_char(keycode)
    return char_to_note.get(char)

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
    def __init__(self, root):
        self.root = root
        self.label = tk.Label(root, text="I need focus to play MIDI out", bg="grey")
        self.label.pack(fill='both', expand=True)
        self.midi_label = tk.Label(root, text="MIDI", bg="#DDD", width=10)
        self.midi_label.pack(side='right')

        root.bind("<KeyPress>", self.on_key_press)
        root.bind("<KeyRelease>", self.on_key_release)

        root.bind("<FocusIn>", self.on_focus)
        root.bind("<FocusOut>", self.on_blur)

    def on_key_press(self, event):
        self.midi_label.config(bg="lightgrey")
        note = keycode_to_midinote(event.keycode)
        print(f'pressed {event.keycode}')
        if note is not None:
            send_note_on(note)

    def on_key_release(self, event):
        self.midi_label.config(bg="#DDD")
        note = keycode_to_midinote(event.keycode)
        if note is not None:
            send_note_off(note)

    def on_focus(self, event):
        self.label.config(text="listening to keyboard", bg="lightgrey")

    def on_blur(self, event):
        self.label.config(text="no focus, no midi", bg="grey")

def main():
    root = tk.Tk()
    root.title("Jammer")
    app = JammerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
