"""Settings-only actions; preserve diary and independent audio preferences."""
import tkinter as tk
from tkinter import messagebox
from selection_state import fresh
from sound_events import play
SIZES={'Small':25,'Medium':50,'Large':75}

def choose_size(app,label):
    app.store.settings(text_size=SIZES[label])
    play(app,'ui_click')
    app.render()

def size_menu(app,event):
    menu=tk.Menu(app.root,tearoff=False,bg='#fff8f2',fg='#3f3a8a',activebackground='#ffd8eb',font=(app.font_family,12))
    value=app.settings.get('text_size',50)
    current=min(SIZES,key=lambda key:abs(SIZES[key]-value))
    selected=tk.StringVar(app.root,value=current)
    for label in SIZES:
        menu.add_radiobutton(label=label,variable=selected,value=label,command=lambda label=label:choose_size(app,label))
    app._size_menu=menu;menu.selection=selected
    menu.tk_popup(event.x_root,event.y_root)

def about(app):
    play(app,'select_crystal')
    messagebox.showinfo('About Veil & Vision',
        'Veil & Vision is an interactive tarot-inspired reflection experience.\n\n'
        'Readings are designed for creativity, reflection and entertainment '
        'rather than fixed predictions.',parent=app.root)

def reset(app):
    app._quiet_action=True
    if not messagebox.askyesno('Reset Progress','Reset the current reading and oracle customization?\nYour Moon Diary and audio/text settings will stay.',parent=app.root):return
    fresh(app)
    app.reading=None;app.chosen=set();app.question.set('');app.note='';app.intention='General'
    app.followup_drafts={}
    app.message='A fresh beginning ♡'
    play(app,'ui_click')
    app.render()
