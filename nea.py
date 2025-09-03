import tkinter as tk
from tkinter import filedialog, Listbox, Scrollbar, simpledialog
import pygame
from PIL import Image, ImageTk
import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, APIC
import threading
import yt_dlp 
import certifi 

# ========== SETUP ==========
pygame.mixer.init()

root = tk.Tk()
root.title("Reverbix")
root.geometry("800x500")
root.configure(bg="black")

playlist = []
favorites = set()
current_song = None
song_background = None
is_playing = False

# Create folder for downloaded music
music_folder = os.path.expanduser("~/Music/ReverbixDownloads")
os.makedirs(music_folder, exist_ok=True)

# ========== THEMES ==========
themes = {
    "Mocha": {"bg": "#1e1e2e", "fg": "#cdd6f4", "button": "#89b4fa"},
    "Latte": {"bg": "#eff1f5", "fg": "#4c4f69", "button": "#7287fd"},
    "Frappe": {"bg": "#303446", "fg": "#c6d0f5", "button": "#99d1db"},
    "Macchiato":{"bg": "#24273a", "fg": "#cad3f5", "button": "#8aadf4"},
    "Default": {"bg": "black", "fg": "white", "button": "#89b4fa"},
}
current_theme = "Mocha"

# ========== GUI WIDGETS ==========

# Album cover
album_frame = tk.Frame(root, bg=themes[current_theme]["bg"], bd=2, relief="ridge")
album_frame.place(x=10, y=10, width=220, height=220)
album_label = tk.Label(album_frame, bg=themes[current_theme]["bg"])
album_label.pack(expand=True, fill="both")

# Playlist with scrollbar
playlist_frame = tk.Frame(root, bg=themes[current_theme]["bg"], bd=2, relief="ridge")
playlist_frame.place(x=250, y=10, width=540, height=220)
scrollbar = Scrollbar(playlist_frame)
scrollbar.pack(side="right", fill="y")

song_list = Listbox(
    playlist_frame,
    font=("Arial", 12),
    bg="white",
    fg="black",
    selectbackground=themes[current_theme]["button"],
    selectforeground="white",
    yscrollcommand=scrollbar.set,
)
song_list.pack(expand=True, fill="both")
scrollbar.config(command=song_list.yview)

# Metadata & time bar
metadata_label = tk.Label(
    root, text="", font=("Arial", 10),
    bg=themes[current_theme]["bg"], fg=themes[current_theme]["fg"]
)
metadata_label.place(x=250, y=240, width=540)

time_label = tk.Label(
    root, text="", font=("Arial", 10),
    bg=themes[current_theme]["bg"], fg=themes[current_theme]["fg"]
)
time_label.place(x=250, y=260, width=540)

# Control buttons
button_frame = tk.Frame(root, bg=themes[current_theme]["bg"])
button_frame.place(x=250, y=300, width=540, height=80)

button_names = ["Play", "Pause", "Unpause", "Rewind", "Previous", "Next", "Stop", "Favorite"]

def make_button(text, command, row, col):
    b = tk.Button(
        button_frame, text=text, command=command,
        bg=themes[current_theme]["button"], fg=themes[current_theme]["fg"],
        bd=0, relief="flat", highlightthickness=0
    )
    b.grid(row=row, column=col, padx=8, pady=5)

for i, name in enumerate(button_names):
    make_button(name, lambda n=name: handle_button(n), i//4, i%4)

# Settings bottom left
settings_button = tk.Button(
    root, text="Settings", command=lambda: open_settings(),
    bg=themes[current_theme]["button"], fg=themes[current_theme]["fg"],
    bd=0, relief="flat", highlightthickness=0
)
settings_button.place(x=10, y=470)

# ========== FUNCTIONS ==========

def update_theme():
    root.configure(bg=themes[current_theme]["bg"])
    album_frame.config(bg=themes[current_theme]["bg"])
    playlist_frame.config(bg=themes[current_theme]["bg"])
    album_label.config(bg=themes[current_theme]["bg"])
    metadata_label.config(bg=themes[current_theme]["bg"], fg=themes[current_theme]["fg"])
    time_label.config(bg=themes[current_theme]["bg"], fg=themes[current_theme]["fg"])
    button_frame.config(bg=themes[current_theme]["bg"])
    settings_button.config(bg=themes[current_theme]["button"], fg=themes[current_theme]["fg"])
    for i in range(song_list.size()):
        song_list.itemconfig(i, fg="yellow" if playlist[i] in favorites else "black")

def open_settings():
    win = tk.Toplevel(root)
    win.title("Settings")
    win.geometry("300x300")
    win.configure(bg=themes[current_theme]["bg"])

    for i, theme in enumerate(themes):
        b = tk.Button(
            win, text=theme, command=lambda t=theme: set_theme(t),
            bg=themes[theme]["button"], fg=themes[theme]["fg"],
            bd=0, relief="flat", highlightthickness=0
        )
        b.pack(pady=5, padx=20, fill="x")

    tk.Button(win, text="Open Folder", command=add_songs,
        bg=themes[current_theme]["button"], fg=themes[current_theme]["fg"],
        bd=0, relief="flat", highlightthickness=0).pack(pady=5, padx=20, fill="x")

    tk.Button(win, text="Change Folder", command=add_songs,
        bg=themes[current_theme]["button"], fg=themes[current_theme]["fg"],
        bd=0, relief="flat", highlightthickness=0).pack(pady=5, padx=20, fill="x")

    tk.Button(win, text="Search YouTube", command=download_youtube,
        bg=themes[current_theme]["button"], fg=themes[current_theme]["fg"],
        bd=0, relief="flat", highlightthickness=0).pack(pady=5, padx=20, fill="x")

def set_theme(theme):
    global current_theme
    current_theme = theme
    update_theme()

def add_songs():
    files = filedialog.askopenfilenames(filetypes=[("MP3 Files", "*.mp3")])
    for file in files:
        playlist.append(file)
        update_song_list()

def update_song_list():
    song_list.delete(0, tk.END)
    for song in playlist:
        title = get_song_title(song)
        song_list.insert(tk.END, title)
        if song in favorites:
            song_list.itemconfig(tk.END, fg="yellow")

def get_song_title(path):
    try:
        audio = MP3(path, ID3=ID3)
        return audio.tags.get("TIT2", os.path.basename(path)).text[0]
    except:
        return os.path.basename(path)

def handle_button(name):
    if name == "Play": play_song()
    elif name == "Pause": pygame.mixer.music.pause()
    elif name == "Unpause": pygame.mixer.music.unpause()
    elif name == "Stop": stop_song()
    elif name == "Rewind": pygame.mixer.music.rewind()
    elif name == "Previous": prev_song()
    elif name == "Next": next_song()
    elif name == "Favorite": toggle_favorite()

def play_song():
    global current_song, is_playing
    sel = song_list.curselection()
    if not sel: return
    idx = sel[0]
    current_song = playlist[idx]
    pygame.mixer.music.load(current_song)
    pygame.mixer.music.play()
    is_playing = True
    load_album_cover(current_song)
    show_metadata(current_song)
    root.after(500, update_progress)

def stop_song():
    global is_playing
    pygame.mixer.music.stop()
    is_playing = False
    time_label.config(text="")
    metadata_label.config(text="")

def prev_song():
    sel = song_list.curselection()
    if not sel: return
    idx = (sel[0]-1) % len(playlist)
    song_list.selection_clear(0, tk.END)
    song_list.selection_set(idx)
    play_song()

def next_song():
    sel = song_list.curselection()
    if not sel: return
    idx = (sel[0]+1) % len(playlist)
    song_list.selection_clear(0, tk.END)
    song_list.selection_set(idx)
    play_song()

def load_album_cover(song):
    try:
        audio = MP3(song, ID3=ID3)
        for tag in audio.tags.values():
            if isinstance(tag, APIC):
                with open("cover.jpg", "wb") as f:
                    f.write(tag.data)
                img = Image.open("cover.jpg").resize((220,220))
                img = ImageTk.PhotoImage(img)
                album_label.config(image=img)
                album_label.image = img
                return
    except:
        pass
    album_label.config(image="", bg=themes[current_theme]["bg"])

def show_metadata(song):
    try:
        audio = MP3(song, ID3=ID3)
        title = audio.tags.get("TIT2", os.path.basename(song)).text[0]
        length = int(audio.info.length)
        metadata_label.config(text=f"{title} — {length//60}:{length%60:02d}")
    except:
        metadata_label.config(text=os.path.basename(song))

def update_progress():
    if is_playing and pygame.mixer.music.get_busy():
        pos = pygame.mixer.music.get_pos()//1000
        time_label.config(text=f"Time: {pos//60}:{pos%60:02d}")
        root.after(500, update_progress)
    else:
        time_label.config(text="")

def toggle_favorite():
    sel = song_list.curselection()
    if not sel: return
    song = playlist[sel[0]]
    if song in favorites:
        favorites.remove(song)
    else:
        favorites.add(song)
    update_song_list()

# ✅ Fixed SSL for yt_dlp
def download_youtube():
    query = simpledialog.askstring("Search YouTube", "Enter song name or URL:")
    if not query:
        return

    # Sanitize filename
    safe_filename = "".join(c for c in query if c.isalnum() or c in (" ", "_", "-")).rstrip()
    output_template = os.path.join(music_folder, f"{safe_filename}.%(ext)s")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_template,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
        'ca_certs': certifi.where(), # ✅ use certifi bundle
    }

    def thread_download():
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if query.startswith("http://") or query.startswith("https://"):
                    ydl.download([query])
                else:
                    ydl.download([f"ytsearch1:{query}"])

            # Find the converted file
            mp3_file = os.path.join(music_folder, f"{safe_filename}.mp3")
            if os.path.exists(mp3_file):
                playlist.append(mp3_file)
                update_song_list()

        except Exception as e:
            print(f"Download failed: {e}")

    threading.Thread(target=thread_download, daemon=True).start()

# Start
update_theme()
root.mainloop()
