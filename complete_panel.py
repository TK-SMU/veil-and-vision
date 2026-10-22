"""Restore source-panel edges without changing the shared chrome or UI grid."""
import tkinter as tk

def restore_edges(app, source_box, ox, oy, scale):
    # The trace boxes cut a few border pixels from the original board. Include
    # that bleed, preserving the original transform used by every live control.
    left,top,right,bottom=source_box
    pad=3
    key=('complete-panel',source_box,scale)
    if key not in app.cache:
        raw=tk.PhotoImage(width=right-left+2*pad,height=bottom-top+pad-21)
        raw.tk.call(str(raw),'copy',str(app.board_source),'-from',left-pad,top+21,right+pad,bottom+pad,'-to',0,0)
        app.cache[key]=app.resized(raw,round(raw.width()*scale),round(raw.height()*scale),key)
    image=app.cache[key]
    from page_frame import APP_WIDTH
    left_x=ox-round(pad*scale)
    if left_x<0 or left_x+image.width()>APP_WIDTH:
        crop_key=('complete-panel-clipped',key,left_x,APP_WIDTH)
        if crop_key not in app.cache:
            start=max(0,-left_x);end=min(image.width(),APP_WIDTH-left_x)
            clipped=tk.PhotoImage(width=end-start,height=image.height())
            clipped.tk.call(str(clipped),'copy',str(image),'-from',start,0,end,image.height(),'-to',0,0)
            app.cache[crop_key]=clipped
        image=app.cache[crop_key];left_x=max(0,left_x)
    app.images.append(image)
    app.canvas.delete('page-content')
    item=app.canvas.create_image(left_x,oy+round(21*scale),image=image,anchor='nw',tags='page-content')
    app.canvas.tag_lower(item,'shared-title-bar')
    app.canvas.tag_raise('page-frame')
