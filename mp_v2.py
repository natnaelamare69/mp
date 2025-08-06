import vlc 
import time
import ctypes
import os 
import random
import requests
from tkinter import * 
from tkinter import filedialog, Tk, Menu, Listbox, Button, Frame, PhotoImage, END 

app = Tk()
app.title('mp_v2')
app.geometry ("500x500")
app.config(background="#1e1e1e")
menu_bar = Menu(app)
app.config(menu= menu_bar)

player = vlc.MediaPlayer()


#global variables 
folder = []
current_song = ""
is_paused = False

#load folder
def load_music():
    global current_song
    app.directory = filedialog.askdirectory()


    folder.clear() # this is gonna be replaced; json to read and write and remember previously added playlists 
    song_listbox.delete(0, END)

    for file in os.listdir(app.directory): #loads from folder to internal folder 
        name, ext = os.path.splitext(file) 
        if ext == '.mp3':
            folder.append(file)
    #load all songs in the internal folder into the listbox: is a simple ui to show list of songs 
    for song in folder:
        song_listbox.insert("end", song) 

    #the first song from the listbox 
    if folder: 
        song_listbox.selection_set(0)
        current_song = folder[song_listbox.curselection()[0]]

#play music
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
      

#check if music ended
def check_music_end():
    global player
    if not player.is_playing() and not is_paused and folder:
        next_song()
    app.after(100, check_music_end)

#pause 
def pause_music(event=None):
    global current_song, is_paused, player
    if not folder:
        return
    player.pause()
    is_paused = not is_paused   

#next
def next_song(event=None):
    global current_song, is_paused, selected_filename, next_index
    if not folder:
        return
    try:
        song_listbox.selection_clear(0,END)
        next_index = (folder.index(os.path.basename(current_song))+1)% len(folder)
        song_listbox.selection_set(next_index)
        selected_filename = folder[next_index]
        current_song = os.path.join(app.directory, selected_filename)
        
        is_paused = False
        play_music()    
    except Exception as e:
        print("error in next_song:", e)

#previous
def previous_song(event=None):
    global current_song, is_paused, selected_filename, previous_index
    if not folder:
        return
    try:
        song_listbox.selection_clear(0,END)
        previous_index = (folder.index(os.path.basename(current_song))-1)% len(folder)
        song_listbox.selection_set(previous_index)
        selected_filename = folder[previous_index]
        current_song = os.path.join(app.directory, selected_filename)
        
        is_paused = False
        play_music()    
    except Exception as e:
        print("error in previous_song:", e)

#shuffle 
def shuffle(event=None):
    global current_song, is_paused, selected_filename, previous_index
    if not folder:
        return
    try:
        song_listbox.selection_clear(0,END)
        shuffled_index = (folder.index(os.path.basename((random.choice(folder)))))
        song_listbox.selection_set(shuffled_index)
        selected_filename = folder[shuffled_index]
        current_song = os.path.join(app.directory, selected_filename)

        is_paused = False
        play_music()
    except:
        pass

#volume increase 
def volume_increase():
    global player, volume_level, new_volume
    try: 
        volume_level = player.audio_get_volume()
        new_volume = min(volume_level+10, 100)
        player.audio_set_volume(new_volume)
        print(volume_level, new_volume)
    except:
        pass
#volume decrease 
def volume_decrease():
    global player, volume_level, new_volume
    try:
        volume_level = player.audio_get_volume()
        new_volume = max(volume_level-10, 0)
        player.audio_set_volume(new_volume)
        print(volume_level, new_volume)
    except:
        pass
#display current time and display remaining time 
def display_time():
    global player, is_paused

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
        

#menu elements 
add_folder_menu = Menu(menu_bar, tearoff=FALSE)
add_folder_menu.add_command(label='select folder', command=load_music)
menu_bar.add_cascade(label='add folder', menu= add_folder_menu)

#temp lisbox to hold elements 
song_listbox = Listbox(app, bg ="black", fg="white", width= 100, height=13)
song_listbox.pack()

#selection event for the listbox 
song_listbox.bind("<<ListboxSelect>>", play_music)

#playbutton 
control_frame = Frame(app)
control_frame.pack()

play_button = Button(control_frame, text="play", command=play_music)
play_button.pack()

#pause button
pause_button = Button(control_frame, text = "pause", command=pause_music)
pause_button.pack()

#next button
next_button = Button(control_frame, text = "next", command=next_song)
next_button.pack()

#previouse button
previous_button = Button(control_frame, text = "previous", command = previous_song)
previous_button.pack()

#shuffle button
shuffle_button = Button(control_frame, text = "shuffle", command = shuffle)
shuffle_button.pack()

#volume increase button
volume_increase_button = Button(control_frame, text = "volume++", command = volume_increase)
volume_increase_button.pack()

#volume decrease button
volume_decrease_button = Button(control_frame, text = "volume--", command = volume_decrease)
volume_decrease_button.pack()
check_music_end()
app.mainloop()