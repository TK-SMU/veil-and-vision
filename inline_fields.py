from page_frame import shared_scale, page_origin
"""Editable fields placed inside the existing painted input borders."""
import tkinter as tk
from tkinter import font as tkfont

# Stable pastel fill: sampling artwork can accidentally pick up blue icons/text.
TEXTBOX_BACKGROUND = '#eee8fa'

def panel_color(app, x, y, fit):
    """Shared lavender field color, independent of nearby artwork pixels."""
    return TEXTBOX_BACKGROUND



def show_value(app, box, text, fit, ox, oy):
    if not text:return
    x,y,r,b=box
    app.canvas.create_rectangle(ox+round(x*fit),oy+round(y*fit),ox+round(r*fit),oy+round(b*fit),fill=panel_color(app,x-2,(y+b)/2,fit),outline='')
    font=(app.font_family,-max(10,round(10*fit)))
    measure=tkfont.Font(root=app.root,font=font)
    visible=text
    while visible and measure.measure(visible)>round((r-x-4)*fit):
        visible=visible[:-2].rstrip('…')+'…'
    app.canvas.create_text(ox+round((x+2)*fit),oy+round((y+b)/2*fit),text=visible,anchor='w',fill='#3f3a8a',font=font)


def edit(app, name, box, base, value, changed, limit):
    previous=getattr(app,name,None)
    if previous is not None and previous.winfo_exists():
        previous.focus_set();return
    w,h=app.desktop_viewport;fit=shared_scale(app)
    ox,oy=page_origin(app)
    x,y,r,b=box
    variable=tk.StringVar(app.root,value=value)
    entry=tk.Entry(app.canvas,textvariable=variable,relief='flat',bd=0,
                   bg=panel_color(app,x-2,(y+b)/2,fit),fg='#3f3a8a',insertbackground='#3f3a8a',
                   highlightthickness=0,selectbackground='#efbfdc',selectforeground='#3f3a8a',
                   font=(app.font_family,-max(10,round(10*fit))))
    def update(*_):
        text=variable.get()
        if len(text)>limit:
            variable.set(text[:limit]);text=text[:limit]
        changed(text)
    variable.trace_add('write',update)
    entry.variable=variable
    app.canvas.create_window(ox+round(x*fit),oy+round(y*fit),anchor='nw',window=entry,width=round((r-x)*fit),height=round((b-y)*fit))
    app.widgets.append(entry);setattr(app,name,entry)
    entry.bind('<Return>',lambda event:app.canvas.focus_set())
    entry.focus_set();entry.icursor('end')
