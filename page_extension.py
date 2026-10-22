"""Extend only unused page margins with existing reference border artwork.

Content and event coordinates never depend on this decorative underlay.
"""
import tkinter as tk
from page_frame import APP_WIDTH, APP_HEIGHT


def draw(app, scale):
    if app.screen in ('intro', 'draw'):
        return
    key=('extended-page-border', APP_WIDTH, APP_HEIGHT, scale)
    if key not in app.cache:
        # Use the existing diary's floral side edges and Intro's bottom flowers, excluding all text and controls.
        # Repeat pixels at their original scale; never stretch the composition.
        def crop(box):
            x,y,r,b=box
            raw=tk.PhotoImage(width=r-x,height=b-y)
            raw.tk.call(str(raw),'copy',str(app.board_source),'-from',x,y,r,b,'-to',0,0)
            return app.resized(raw,round((r-x)*scale),round((b-y)*scale),('border-source',box,scale))
        left=crop((409,795,423,970))
        right=crop((741,795,755,970))
        bottom=crop((29,371,99,378))
        layer=tk.PhotoImage(width=APP_WIDTH,height=APP_HEIGHT)
        def paste(image,x,y):
            w=min(image.width(),APP_WIDTH-x);h=min(image.height(),APP_HEIGHT-y)
            if w>0 and h>0:
                layer.tk.call(str(layer),'copy',str(image),'-from',0,0,w,h,'-to',x,y)
        for y in range(round(21*scale),APP_HEIGHT,left.height()):
            paste(left,2,y);paste(right,APP_WIDTH-right.width()-2,y)
        for x in range(2,APP_WIDTH-2,bottom.width()):
            paste(bottom,x,APP_HEIGHT-bottom.height()-2)
        app.cache[key]=layer
    image=app.cache[key];app.images.append(image)
    app.canvas.create_image(0,0,image=image,anchor='nw',tags='page-edge-extension',state='disabled')
