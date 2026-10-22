"""Shared pastel selection styling; application state remains the source of truth."""
import tkinter as tk

NORMAL='#fffbf2'
PINK='#ffc6e3'
BORDER='#d65aa0'


def apply(app, item, selected, group, overlay=False, normal_fill=NORMAL, outline_only=False):
    canvas=app.canvas
    canvas.itemconfigure(item,fill='' if overlay else (PINK if selected and not outline_only else normal_fill),
                         outline=BORDER if selected else ('' if overlay else '#c8b5ea'),
                         stipple='')
    parts=[item]
    x,y,r,b=canvas.coords(item)
    if selected and overlay and not outline_only:
        source=app.panel_photo;px,py=app.panel_origin
        left,top,right,bottom=[round(v) for v in (x-px,y-py,r-px,b-py)]
        key=('selection-tint',str(source),left,top,right,bottom)
        if key not in app.cache:
            sw,sh=source.width(),source.height()
            data=source.tk.call(str(source),'data','-format','ppm').split(b'\n',3)[3]
            pixels=bytearray()
            for yy in range(top,bottom):
                for xx in range(left,right):
                    pos=(max(0,min(sh-1,yy))*sw+max(0,min(sw-1,xx)))*3
                    for channel,pink in zip(data[pos:pos+3],(255,170,210)):
                        pixels.append(round(channel*.76+pink*.24))
            w,h=right-left,bottom-top
            app.cache[key]=tk.PhotoImage(data=f'P6\n{w} {h}\n255\n'.encode()+pixels,format='PPM')
        tint=app.cache[key];app.images.append(tint)
        image=canvas.create_image(x,y,image=tint,anchor='nw')
        canvas.tag_lower(image,item);parts.append(image)
    if selected and not outline_only:
        parts.append(canvas.create_line(x+3,y+2,r-3,y+2,fill='#fff1f8',width=1))
        parts.append(canvas.create_line(x+3,b-2,r-3,b-2,fill='#dfa9ce',width=1))
    app.selection_styles.append(dict(item=item,parts=parts,selected=bool(selected),group=group,overlay=overlay,normal_fill=normal_fill,outline_only=outline_only))


def connect(app):
    """Attach feedback to existing hit regions, including their icon/text area."""
    canvas=app.canvas
    canvas.selection_targets={}
    for style in app.selection_styles:
        box=canvas.coords(style['item'])
        if style['selected']:
            for child in canvas.find_enclosed(box[0]-2,box[1]-2,box[2]+2,box[3]+2):
                if canvas.type(child)=='text':canvas.itemconfigure(child,fill='#3f3a8a')
        for tag in canvas.region_callbacks:
            items=canvas.find_withtag(tag)
            for hit in items:
                if canvas.type(hit)=='rectangle':
                    target=canvas.coords(hit)
                    if len(target)==4 and max(abs(a-b) for a,b in zip(box,target))<=2:
                        canvas.selection_targets[tag]=style
                        canvas.tag_bind(tag,'<Enter>',lambda e,t=tag:canvas.feedback(t,True))
                        canvas.tag_bind(tag,'<Leave>',lambda e,t=tag:canvas.feedback(t,False))
                        break


def tinted_thumbnail(app, source, key):
    """Composite a 24% blush tint into the same icon, retaining transparency.

    Tk rectangles cannot alpha-blend reliably on macOS. A cached composite
    keeps exactly one visible image item instead of stacking opaque widgets.
    """
    cache_key=('soft-selection-icon',key,source.width(),source.height())
    if cache_key not in app.cache:
        result=source.copy()
        for y in range(source.height()):
            for x in range(source.width()):
                if source.transparency_get(x,y):continue
                rgb=source.get(x,y)
                color='#'+''.join(f'{round(v*.76+p*.24):02x}' for v,p in zip(rgb,(255,170,210)))
                result.put(color,(x,y))
        app.cache[cache_key]=result
    return app.cache[cache_key]


def tint_fill(color):
    rgb=[int(color[i:i+2],16) for i in (1,3,5)]
    return '#'+''.join(f'{round(v*.76+p*.24):02x}' for v,p in zip(rgb,(255,170,210)))
