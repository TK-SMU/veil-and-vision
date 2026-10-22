"""Inventory thumbnails from the existing wardrobe artwork; never alters Lumi."""
from pathlib import Path
import tkinter as tk

# Existing clean-head / empty-companion / empty-collar icons, without labels.
NONE_BOXES={
    'Hats':(386,650,466,719),
    'Buddies':(877,653,942,720),
    'Accessories':(1357,652,1436,720),
}

def thumbnail(app,category,choice,width=64,height=34):
    if category=='Backgrounds':
        return app.wardrobe_background(choice,width,height)
    if choice!='None':
        return app.wardrobe_sprite(category,choice,width,height)
    key=('inventory-none',category)
    if key not in app.cache:
        if not hasattr(app,'wardrobe_source'):
            app.wardrobe_source=tk.PhotoImage(file=str(Path(__file__).with_name('wardrobe_reference.png')))
        x,y,r,b=NONE_BOXES[category]
        icon=tk.PhotoImage(width=r-x,height=b-y)
        icon.tk.call(str(icon),'copy',str(app.wardrobe_source),'-from',x,y,r,b,'-to',0,0)
        # Remove only connected pale backing; preserve enclosed cream details.
        w,h=icon.width(),icon.height()
        pending=[(xx,yy) for xx in range(w) for yy in (0,h-1)]
        pending += [(xx,yy) for yy in range(h) for xx in (0,w-1)]
        seen=set()
        while pending:
            xx,yy=pending.pop()
            if (xx,yy) in seen or not(0<=xx<w and 0<=yy<h):continue
            seen.add((xx,yy))
            red,green,blue=icon.get(xx,yy)
            if red>215 and green>205 and blue>205:
                icon.transparency_set(xx,yy,True)
                pending.extend(((xx-1,yy),(xx+1,yy),(xx,yy-1),(xx,yy+1)))
        app.cache[key]=app.trim_sprite(icon)
    source=app.cache[key]
    ratio=min(width/source.width(),height/source.height())
    return app.resized(source,max(1,round(source.width()*ratio)),max(1,round(source.height()*ratio)),key)
