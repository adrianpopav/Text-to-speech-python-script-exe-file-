import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from gtts import gTTS
import os
from threading import Thread
import pygame
import time
from ttkbootstrap import Style

# Dicționar pentru maparea limbilor umane la codurile de limbă
languages = {"English": "en", "Romanian": "ro", "French": "fr", "Spanish": "es"}

# Variabile globale pentru controlul playerului
is_playing = False
paused = False
mp3_file_path = ""  # Variabilă globală pentru calea fișierului MP3

# Funcție pentru conversia text-to-speech
def convert_text_to_speech():
    global mp3_file_path
    text = text_box.get("1.0", tk.END).strip()
    selected_lang = language_var.get()  # Obține limba selectată (umană)
    lang = languages.get(selected_lang, "en")  # Maparea la codul limbii

    if not text:
        messagebox.showwarning("Allert", "Insert text")
        return

    # Afișează mesajul de "loading"
    status_label.config(text="Converting, please wait...", fg="blue")
    window.update_idletasks()

    def convert_and_save():
        global mp3_file_path
        try:
            # Conversie text-to-speech
            tts = gTTS(text=text, lang=lang)
            mp3_file_path = os.path.join(os.getcwd(), "output.mp3")  # Salvează calea fișierului
            tts.save(mp3_file_path)
            status_label.config(text="Conversion successful!", fg="green")

            # Activarea butoanelor de descărcare și redare
            play_button.config(state=tk.NORMAL)
            download_button.config(state=tk.NORMAL)  # Activăm butonul de descărcare
        except Exception as e:
            status_label.config(text=f"Error: {str(e)}", fg="red")

    # Folosește un thread pentru a nu bloca interfața grafică
    Thread(target=convert_and_save).start()

# Funcție pentru descărcarea fișierului mp3
def download_mp3():
    global mp3_file_path
    file_path = filedialog.asksaveasfilename(defaultextension=".mp3", filetypes=[("MP3 files", "*.mp3")])
    if file_path:
        try:
            os.rename(mp3_file_path, file_path)  # Folosește calea fișierului MP3 stocat
            status_label.config(text="File saved successfully!", fg="green")
            mp3_file_path = file_path  # Actualizăm calea fișierului MP3 salvat
        except Exception as e:
            status_label.config(text=f"Error: {str(e)}", fg="red")

# Funcție pentru actualizarea timeline-ului playerului
def update_timeline():
    while is_playing:
        current_time = pygame.mixer.music.get_pos() // 1000  # Timpul curent în secunde
        progress_var.set(current_time)
        timeline_slider.config(to=int(current_time))  # Actualizează sliderul
        window.update_idletasks()
        time.sleep(1)

# Funcție pentru redarea fișierului MP3
def play_audio():
    global is_playing, paused
    pygame.mixer.init()
    pygame.mixer.music.load(mp3_file_path)  # Folosește calea fișierului stocat
    pygame.mixer.music.play()
    is_playing = True
    paused = False

    # Setează durata și începe actualizarea timeline-ului
    track_length = pygame.mixer.Sound(mp3_file_path).get_length()  # Folosește calea fișierului stocat
    timeline_slider.config(to=int(track_length))
    Thread(target=update_timeline).start()

# Funcție pentru a pune pe pauză/redare
def toggle_pause():
    global paused
    if paused:
        pygame.mixer.music.unpause()
        paused = False
    else:
        pygame.mixer.music.pause()
        paused = True

# Crearea ferestrei principale cu ttkbootstrap
window = tk.Tk()
style = Style(theme="flatly")  # Alege un tema modern
window.title("Text to Speech Player by Adi")
window.geometry("500x500")

# Etichetă și câmp de text
tk.Label(window, text="Write text:", font=("Arial", 12)).pack(pady=5)
text_box = tk.Text(window, height=5, width=50, bd=1, relief='solid')
text_box.pack(pady=5)

# Selectarea limbii
tk.Label(window, text="Choose Language:", font=("Arial", 12)).pack(pady=5)
language_var = tk.StringVar(value="English")
language_menu = ttk.Combobox(window, textvariable=language_var, values=list(languages.keys()), state="readonly")
language_menu.pack(pady=5)

# Buton de conversie
convert_button = ttk.Button(window, text="Convert", command=convert_text_to_speech)
convert_button.pack(pady=10)

# Etichetă pentru status
status_label = tk.Label(window, text="", fg="green", font=("Arial", 10))
status_label.pack()

# Buton de descărcare (inițial dezactivat)
download_button = ttk.Button(window, text="Download MP3", state=tk.DISABLED, command=download_mp3)
download_button.pack(pady=10)

# Player audio cu timeline
tk.Label(window, text="Player MP3:", font=("Arial", 12)).pack(pady=5)

# Timeline slider
progress_var = tk.IntVar()
timeline_slider = ttk.Scale(window, from_=0, to=100, orient='horizontal', variable=progress_var, state=tk.DISABLED)
timeline_slider.pack(pady=10)

play_button = ttk.Button(window, text="Play it", state=tk.DISABLED, command=play_audio)
play_button.pack(pady=5)

# Rulare interfață grafică
window.mainloop()
