import vlc
import os
import random
import json
from tkinter import Tk,Listbox, Button, Frame, filedialog, Menu, END


app = Tk()
app.title('mp_v2')
app.geometry("500x300")
app.config(background="#1e1e1e")
menu_bar = Menu(app)
app.config(menu=menu_bar)

player = vlc.MediaPlayer()
directories = "directories.json"

# Global variables
folder = []
current_song = ""
is_paused = False

# Load folder
def load_music():
    global current_song
    app.directory = filedialog.askdirectory()
    if not app.directory:
        return
    saves_folders_path(app.directory)
    folder.clear()
    song_listbox.delete(0, END)
    for file in os.listdir(app.directory):
        name, ext = os.path.splitext(file)
        if ext == '.mp3':
            folder.append(file)
    for song in folder:
        song_listbox.insert(END, song)
    if folder:
        song_listbox.selection_set(0)
        current_song = folder[song_listbox.curselection()[0]]

# Choose folder from saved directories
def choose_folders(event):
    global folder, current_song
    folder_list = load_directories_path()
    selection = folder_listbox.curselection()
    if not selection:
        return
    index = selection[0]
    selected_folder = folder_list[index]
    app.directory = selected_folder
    folder.clear()
    song_listbox.delete(0, END)
    for file in os.listdir(selected_folder):
        name, ext = os.path.splitext(file)
        if ext == '.mp3':
            folder.append(file)
    for song in folder:
        song_listbox.insert(END, song)
    if folder:
        song_listbox.selection_set(0)
        current_song = os.path.join(app.directory, folder[0])
    song_listbox.pack()

def load_directories_path():
    if not os.path.exists(directories):
        return []
    try:
        with open(directories, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def saves_folders_path(path):
    folders_list = load_directories_path()
    if path not in folders_list:
        folders_list.append(path)
    with open(directories, "w") as f:
        json.dump(folders_list, f)

# Music controls
def play_music(event=None):
    global current_song, is_paused, player
    if not folder:
        return
    selection_index = song_listbox.curselection()
    if selection_index:
        selected_filename = folder[selection_index[0]]
        current_song = os.path.join(app.directory, selected_filename)
    if is_paused:
        player.play()
        is_paused = False
    else:
        player.set_media(vlc.Media(current_song))
        player.play()
    display_time()
#auto next 
def check_music_end():
    if not player.is_playing() and not is_paused and folder:
        next_song()
    app.after(100, check_music_end)
#pause 
def pause_music(event=None):
    global is_paused
    if not folder:
        return
    player.pause()
    is_paused = not is_paused
#next 
def next_song(event=None):
    global current_song
    if not folder:
        return
    try:
        song_listbox.selection_clear(0, END)
        next_index = (folder.index(os.path.basename(current_song)) + 1) % len(folder)
        song_listbox.selection_set(next_index)
        current_song = os.path.join(app.directory, folder[next_index])
        is_paused = False
        play_music()
    except Exception as e:
        print("error in next_song:", e)
#prev
def previous_song(event=None):
    global current_song
    if not folder:
        return
    try:
        song_listbox.selection_clear(0, END)
        previous_index = (folder.index(os.path.basename(current_song)) - 1) % len(folder)
        song_listbox.selection_set(previous_index)
        current_song = os.path.join(app.directory, folder[previous_index])
        is_paused = False
        play_music()
    except Exception as e:
        print("error in previous_song:", e)
#shuffle 
def shuffle(event=None):
    global current_song
    if not folder:
        return
    try:
        song_listbox.selection_clear(0, END)
        shuffled_index = folder.index(os.path.basename(random.choice(folder)))
        song_listbox.selection_set(shuffled_index)
        current_song = os.path.join(app.directory, folder[shuffled_index])
        is_paused = False
        play_music()
    except:
        pass
#volume controls 
#volume increase
def volume_increase():
    try:
        volume_level = player.audio_get_volume()
        new_volume = min(volume_level + 10, 100)
        player.audio_set_volume(new_volume)
        print(volume_level, new_volume)
    except:
        pass
#volume decrease
def volume_decrease():
    try:
        volume_level = player.audio_get_volume()
        new_volume = max(volume_level - 10, 0)
        player.audio_set_volume(new_volume)
        print(volume_level, new_volume)
    except:
        pass
# display current time and length
# currently only prints into terminal cause there is a bug 
# in the future in to the UI elements 
def display_time():
    if not is_paused:
        length = player.get_length()
        current_time = player.get_time()
        if length > 0 and current_time >= 0:
            cm = current_time // 60000
            cs = (current_time % 60000) // 1000
            lm = length // 60000
            ls = (length % 60000) // 1000
            print(f"{cm}:{cs:02d} / {lm}:{ls:02d}")
        else:
            print("...")
    app.after(1000, display_time)

#mostly used ai for below 
# Menu
add_folder_menu = Menu(menu_bar, tearoff=False)
add_folder_menu.add_command(label='Select folder', command=load_music)
menu_bar.add_cascade(label='Add folder', menu=add_folder_menu)

# Folder listbox
folder_listbox = Listbox(app, bg="black", fg="white", width=100, height=5)
folder_listbox.pack()
saved_folders = load_directories_path()
for folder_path in saved_folders:
    folder_listbox.insert(END, os.path.basename(folder_path))
folder_listbox.bind("<<ListboxSelect>>", choose_folders)

# Song listbox (hidden initially)
song_listbox = Listbox(app, bg="black", fg="white", width=100, height=13)
song_listbox.bind("<<ListboxSelect>>", play_music)

# Control buttons in a single row at bottom
control_frame = Frame(app, bg="black")
control_frame.pack(side="bottom", pady=10)

buttons = [
    ("Shuffle", shuffle),
    ("Previous", previous_song),
    ("Play", play_music),
    ("Pause", pause_music),
    ("Next", next_song),
    ("Vol -", volume_decrease),
    ("Vol +", volume_increase)
]

for text, cmd in buttons:
    Button(control_frame, text=text, command=cmd).pack(side="left", padx=5)

check_music_end()
app.mainloop()
