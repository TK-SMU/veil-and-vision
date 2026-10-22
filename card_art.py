"""The 22-card Veil & Vision deck, built from shared frame/art/title layers.

The PNG faces are compiled local assets; runtime needs only Python/Tkinter.
Identity, not the random artwork seed, selects the illustration so saved readings
always retain the same animal and scene. No network or generation at runtime.
"""
import json
import tkinter as tk
from pathlib import Path

ASSETS=Path(__file__).resolve().parent/'assets'
MANIFEST=json.loads((ASSETS/'deck_manifest.json').read_text())
CARDS={card['name']:card for card in MANIFEST['cards']}

def image(app,card,width,height):
    name=card['name']
    if name not in CARDS:
        raise ValueError(f'Unknown tarot card: {name}')
    width,height=max(1,int(width)),max(1,int(height))
    background='#363780' if getattr(app,'screen','')=='draw' else '#fff8f2'
    key=('menagerie-v2',name,width,height,background)
    if key not in app.cache:
        source_key=('menagerie-source',name)
        if source_key not in app.cache:
            app.cache[source_key]=tk.PhotoImage(file=str(ASSETS/CARDS[name]['face']))
        source=app.cache[source_key]
        factor=min(width/source.width(),height/source.height())
        w,h=max(1,round(source.width()*factor)),max(1,round(source.height()*factor))
        scaled=app.resized(source,w,h,('menagerie-fit',name))
        result=tk.PhotoImage(width=width,height=height)
        result.put(background,to=(0,0,width,height))
        result.tk.call(str(result),'copy',str(scaled),'-to',(width-w)//2,(height-h)//2)
        app.cache[key]=result
    return app.cache[key]
