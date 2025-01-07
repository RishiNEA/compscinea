from tkinter import * #imported both tkinter as my gui and pygame allowing me to run audio files / other wdigets
import pygame

window = Tk() # set tkinter a TK and corrected the dimensions and titles of my site to personalise it
window.title("Reverbix")
window.geometry("500x400")    

pygame.mixer.init() # mixer initialised therefore it can be recognised

#creating a playlist box presenting all the songs that will be playing
playlist_box = Listbox(window, bg="black", fg="red", width=80)
playlist_box.grid(row=0, column=0, padx=20, pady=0, columnspan=5, sticky="ew")


#defining all buttons (functions)
def play_song():
    pygame.mixer.music.load("audio/It Was A Good Day.mp3")
    pygame.mixer.music.play(loops=0)

def stop_song():
    pygame.mixer.music.stop()

def pause_song():
    pygame.mixer.music.pause()

def rewind_song():
    pygame.mixer.music.rewind()

def unpause_song():
    pygame.mixer.music.unpause()

# Buttons
play_btn = Button(window, text="Play", font=("Arial", 10), command=play_song)
pause_btn = Button(window, text="Pause", font=("Arial", 10), command=pause_song)
stop_btn = Button(window, text="Stop", font=("Arial", 10), command=stop_song)
rewind_btn = Button(window, text="Rewind", font=("Arial", 10), command=rewind_song)
unpause_btn = Button(window, text="Unpause", font=("Arial", 10), command=unpause_song)

#placements on the gui 
play_btn.grid(row=1, column=0, padx=10, pady=0, sticky='ew')
pause_btn.grid(row=1, column=1, padx=10, pady=0, sticky='ew')
unpause_btn.grid(row=1, column=2, padx=10, pady=0, sticky='ew')
rewind_btn.grid(row=1, column=3, padx=10, pady=0, sticky='ew')
stop_btn.grid(row=1, column=4, padx=10, pady=0, sticky='ew')

#esential placements for gui so the width and lengths dont expand
for i in range(5):
    window.grid_columnconfigure(i, weight=1, uniform="equal")


window.grid_rowconfigure(0, weight=0, minsize=0)  
window.grid_rowconfigure(1, weight=0, minsize=0)

window.mainloop()