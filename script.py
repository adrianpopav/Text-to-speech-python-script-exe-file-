import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from gtts import gTTS
import os
from threading import Thread
import pygame
import time
from ttkbootstrap import Style
from PIL import Image, ImageTk  # Pentru lucrul cu imagini

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

# Fereastra nu mai este redimensionabilă
window.resizable(False, False)

# Setarea iconiței personalizate
icon_path = "img/1.ico"  # Asigură-te că fișierul se află în calea corectă
window.iconbitmap(icon_path)

# Încarcă imaginea de background
bg_image_path = "img/bg.jpg"  # Calea către imaginea de background
bg_image = Image.open(bg_image_path)
bg_image = bg_image.resize((500, 500), Image.Resampling.LANCZOS)  # Redimensionează imaginea la dimensiunea ferestrei
bg_photo = ImageTk.PhotoImage(bg_image)

# Creare Canvas pentru a afișa imaginea de background
canvas = tk.Canvas(window, width=500, height=500)
canvas.pack(fill="both", expand=True)

# Afișează imaginea de background pe Canvas
canvas.create_image(0, 0, image=bg_photo, anchor="nw")

# Adăugare widget-uri peste Canvas
canvas.create_text(250, 20, text="Write text:", font=("Arial", 12), fill="white")

text_box = tk.Text(window, height=5, width=50, bd=1, relief='solid')
canvas.create_window(250, 80, window=text_box)

# Ajustare spațiere între textul "Choose Language" și caseta text
canvas.create_text(250, 140, text="Choose Language:", font=("Arial", 12), fill="white")

language_var = tk.StringVar(value="English")
language_menu = ttk.Combobox(window, textvariable=language_var, values=list(languages.keys()), state="readonly")
canvas.create_window(250, 170, window=language_menu)

convert_button = ttk.Button(window, text="Convert", command=convert_text_to_speech)
canvas.create_window(250, 210, window=convert_button)

status_label = tk.Label(window, text="", fg="green", font=("Arial", 10))
canvas.create_window(250, 240, window=status_label)

download_button = ttk.Button(window, text="Download MP3", state=tk.DISABLED, command=download_mp3)
canvas.create_window(250, 270, window=download_button)

# Ajustare spațiere pentru player MP3
canvas.create_text(250, 320, text="Player MP3:", font=("Arial", 12), fill="white")

progress_var = tk.IntVar()
timeline_slider = ttk.Scale(window, from_=0, to=100, orient='horizontal', variable=progress_var, state=tk.DISABLED)
canvas.create_window(250, 350, window=timeline_slider)

play_button = ttk.Button(window, text="Play it", state=tk.DISABLED, command=play_audio)
canvas.create_window(250, 390, window=play_button)

# Rulare interfață grafică
window.mainloop()
