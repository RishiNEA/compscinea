import tkinter as tk
from tkinter import filedialog, Listbox
import pygame
from PIL import Image, ImageTk
import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC

# Initialize Pygame Mixer
pygame.mixer.init()

# Main Tkinter Window
root = tk.Tk()
root.title("Reverbix")
root.geometry("800x500")
root.configure(bg="black")

# Global Variables
playlist = []
current_song = None
song_background = None

# Function to Add Songs
def add_songs():
    files = filedialog.askopenfilenames(filetypes=[("MP3 Files", "*.mp3")])
    for file in files:
        playlist.append(file)
        song_list.insert(tk.END, os.path.basename(file))

# Function to Play Selected Song
def play_song():
    global current_song, song_background
    
    selected_index = song_list.curselection()
    if not selected_index:
        return
    
    song_index = selected_index[0]
    current_song = playlist[song_index]
    
    pygame.mixer.music.load(current_song)
    pygame.mixer.music.play()
    
    song_label.config(text=f"Playing: {os.path.basename(current_song)}")
    
    # Extract album cover and update background
    root.after(100, extract_album_cover, current_song)

# Function to Extract Album Art from MP3
def extract_album_cover(song_path):
    global song_background

    try:
        # Load MP3 file metadata
        audio = MP3(song_path, ID3=ID3)
        for tag in audio.tags.values():
            if isinstance(tag, APIC):
                # Extract album art
                image_data = tag.data
                with open("album_cover.jpg", "wb") as img_file:
                    img_file.write(image_data)

                # Load and set the album cover as the background
                img = Image.open("album_cover.jpg").resize((800, 500), Image.Resampling.LANCZOS)
                song_background = ImageTk.PhotoImage(img)
                background_label.config(image=song_background)
                background_label.lower()  # Ensure it's behind all widgets
                return
    except Exception as e:
        print(f"Error extracting album cover: {e}")

    # Reset background if no cover found
    background_label.config(image="", bg="black")

# Function to Pause Song
def pause_song():
    pygame.mixer.music.pause()

# Function to Unpause Song
def unpause_song():
    pygame.mixer.music.unpause()

# Function to Stop Song
def stop_song():
    pygame.mixer.music.stop()
    song_label.config(text="No Song Playing")
    background_label.config(image="", bg="black")  # Reset background

# Function to Play Next Song
def next_song():
    selected_index = song_list.curselection()
    if not selected_index:
        return
    
    next_index = (selected_index[0] + 1) % len(playlist)
    song_list.selection_clear(0, tk.END)
    song_list.selection_set(next_index)
    play_song()

# Function to Play Previous Song
def prev_song():
    selected_index = song_list.curselection()
    if not selected_index:
        return
    
    prev_index = (selected_index[0] - 1) % len(playlist)
    song_list.selection_clear(0, tk.END)
    song_list.selection_set(prev_index)
    play_song()

# Function to Rewind Song
def rewind_song():
    pygame.mixer.music.rewind()

# UI Components

# Background Label
background_label = tk.Label(root, bg="black")
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# Song Label
song_label = tk.Label(root, text="No Song Playing", font=("Arial", 16), fg="white", bg="black")
song_label.pack(pady=10)

# Playlist Box
song_list = Listbox(root, font=("Arial", 12), width=50, height=10, bg="white", fg="black", selectbackground="gray", selectmode=tk.SINGLE)
song_list.pack(pady=10)

# Buttons Styling
button_style = {"font": ("Arial", 12), "bd": 0, "relief": "flat", "highlightthickness": 0, "takefocus": False}

# Button Frame
button_frame = tk.Frame(root, bg="black")
button_frame.pack(pady=20)

# Buttons
play_button = tk.Button(button_frame, text="Play", command=play_song, **button_style)
pause_button = tk.Button(button_frame, text="Pause", command=pause_song, **button_style)
unpause_button = tk.Button(button_frame, text="Unpause", command=unpause_song, **button_style)
rewind_button = tk.Button(button_frame, text="Rewind", command=rewind_song, **button_style)
prev_button = tk.Button(button_frame, text="Previous", command=prev_song, **button_style)
add_button = tk.Button(button_frame, text="Add Songs", command=add_songs, **button_style)
next_button = tk.Button(button_frame, text="Next", command=next_song, **button_style)
stop_button = tk.Button(button_frame, text="Stop", command=stop_song, **button_style)

# Grid Layout for Buttons
buttons = [play_button, pause_button, unpause_button, rewind_button, prev_button, add_button, next_button, stop_button]
row, col = 0, 0

for button in buttons:
    button.grid(row=row, column=col, padx=10, pady=5)
    col += 1
    if col > 3:  # Arrange in 2 rows
        col = 0
        row += 1

# Run Tkinter Mainloop
root.mainloop()
