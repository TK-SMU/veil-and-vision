from page_frame import shared_scale
"""Shared behaviour for the existing twelve painted panels."""
import tkinter as tk
from tkinter import messagebox
from tkinter import font as tkfont


def finish(app):
    """Enable title controls and apply state without changing geometry."""
    from page_frame import APP_WIDTH, CONTENT_SCALE
    # The header is shared chrome, not part of the centered page composition.
    sx=APP_WIDTH/371;sy=round(21*CONTENT_SCALE)/21
    for tag,left,right,action in [
        ('minimize',313,329,app.minimize),
        ('maximize',332,348,lambda:messagebox.showinfo('Presentation window',
            'All twelve screens share this fixed presentation window.',parent=app.root)),
        ('close',351,367,app.close)]:
        item=app.canvas.create_rectangle(round(left*sx),round(3*sy),round(right*sx),round(19*sy),
                                         fill='',outline='',tags='header-'+tag)
        app.canvas.tag_bind(item,'<Button-1>',lambda e,fn=action:app.run_action(fn))
    # Deck faces already contain the common title and numeral layers. Adding
    # the old sample-title cover here would obscure the new shared frame.
    factor=1+(app.settings.get('text_size',50)-50)/500
    for item in app.canvas.find_all():
        kind=app.canvas.type(item)
        if kind=='text':
            if factor!=1:
                font=tkfont.Font(font=app.canvas.itemcget(item,'font'))
                size=font.cget('size')
                app.canvas.itemconfigure(item,font=(app.font_family,round(size*factor)))
