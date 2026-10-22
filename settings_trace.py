from page_frame import shared_scale, page_origin, APP_WIDTH, APP_HEIGHT
"""Pixel-accurate trace of Screen 12: Settings."""
from pathlib import Path
import tkinter as tk
from page_frame import draw_panel
from selection_style import apply as selection_style
from selection_state import selected
from check_badge import draw as draw_check
import settings_actions
from artwork_text import clear as clear_art_text

SOURCE_BOX=(1154,754,1510,1014); BASE_SIZE=(356,260)
def draw(app):
    if not getattr(app,'settings_trace',False) or app.screen!='settings': return False
    app._drawing_compact=True
    try:
        if not hasattr(app,'board_source'): app.board_source=tk.PhotoImage(file=str(Path(__file__).with_name('reference_current.png')))
        width,height=(APP_WIDTH,APP_HEIGHT); fit=shared_scale(app); ow,oh=round(356*fit),round(260*fit)
        raw=tk.PhotoImage(width=356,height=260); raw.tk.call(str(raw),'copy',str(app.board_source),'-from',*SOURCE_BOX,'-to',0,0)
        # The reference has a sample Night selection ring. Neutralize only
        # that ring; background selection is drawn above from explicit user state.
        for yy in range(64,122):
            for xx in range(228,321):
                if xx<233 or xx>315 or yy<69 or yy>117:
                    red,green,blue=raw.get(xx,yy)
                    if blue>red+45 and blue>green+35:
                        raw.put('#c8b5ea',(xx,yy))
        # Clear only baked switch/slider pixels using adjacent panel shading.
        for box,sample in [((119,127,159,148),117),((280,127,319,148),278),((143,153,290,172),142)]:
            clear_art_text(raw,box,sample)
        panel=app.resized(raw,ow,oh,('settings-trace',ow,oh)); app.images.append(panel); app.canvas.configure(width=width,height=height,bg='#d5d2ff'); ox,oy=page_origin(app); draw_panel(app, panel, ox, oy, fit, BASE_SIZE); app.controls={}
        themes=['Day','Sunset','Night']
        for i,theme in enumerate(themes):
            x=44+i*83; tag='theme-'+theme; rect=app.canvas.create_rectangle(ox+round(x*fit),oy+round(59*fit),ox+round((x+70)*fit),oy+round(104*fit),outline='#d65aa0' if selected(app,'selected_background',theme) else '',width=max(1,round(2*fit)),tags=tag); hit_x1,hit_x2=[(36,125),(129,219),(228,319)][i]
            hit=app.canvas.create_rectangle(ox+round(hit_x1*fit),oy+round(64*fit),ox+round(hit_x2*fit),oy+round(121*fit),outline='')
            app.canvas.delete(rect)
            selection_style(app,hit,selected(app,'selected_background',theme),'background-shortcuts',overlay=True)
            app.canvas.tag_bind(hit,'<Button-1>',lambda e,theme=theme:app.run_action(lambda:app.open_background(theme)))
            if selected(app,'selected_background',theme):
                badge_tag='background-check-'+theme
                draw_check(app.canvas,(ox+round((hit_x2-16)*fit),oy+round(106*fit),ox+round((hit_x2-3)*fit),oy+round(119*fit)),tag=badge_tag)
        for key,x in [('music',120),('sound',281)]:
            on=app.settings.get(key,False)
            rect=app.canvas.create_rectangle(ox+round(x*fit),oy+round(128*fit),ox+round((x+36)*fit),oy+round(147*fit),fill='',outline='',tags='toggle-'+key)
            left,top,right,bottom=app.canvas.coords(rect)
            radius=(bottom-top)/2
            for color,stroke in [('#7264bb',bottom-top),('#85aaff' if on else '#d4c9ec',bottom-top-2)]:
                app.canvas.create_line(left+radius,top+radius,right-radius,top+radius,fill=color,width=stroke,capstyle='round')
            app.canvas.create_oval(ox+round((x+(18 if on else 2))*fit),oy+round(130*fit),ox+round((x+(33 if on else 17))*fit),oy+round(145*fit),fill='#fff9ff',outline='')
            app.canvas.tag_bind(rect,'<Button-1>',lambda e,key=key:app.run_action(lambda:app.toggle(key)))
        rect=app.canvas.create_rectangle(ox+round(143*fit),oy+round(153*fit),ox+round(286*fit),oy+round(172*fit),outline='',tags='text-size')
        app.canvas.tag_bind(rect,'<Button-1>',lambda event:settings_actions.size_menu(app,event))
        # Remove the reference's sample knob before drawing the actual value.
        app.canvas.create_line(ox+round(147*fit),oy+round(163*fit),ox+round(283*fit),oy+round(163*fit),fill='#bcb1f2',width=max(2,round(5*fit)),capstyle='round')
        value=app.settings.get('text_size',50)
        size=min(settings_actions.SIZES,key=lambda name:abs(settings_actions.SIZES[name]-value))
        x=148+133*list(settings_actions.SIZES).index(size)/2
        app.canvas.create_oval(ox+round((x-5)*fit),oy+round(157*fit),ox+round((x+5)*fit),oy+round(169*fit),fill='#b497ef',outline='#4038ae')
        for tag,box,fn in [('about',(36,174,319,192),lambda:settings_actions.about(app)),('clear',(36,193,319,211),app.clear_diary),('reset',(36,212,319,230),lambda:settings_actions.reset(app)),('back',(103,233,258,253),lambda:app.go('intro'))]:
            x,y,r,b=box; rect=app.canvas.create_rectangle(ox+round(x*fit),oy+round(y*fit),ox+round(r*fit),oy+round(b*fit),outline='',tags='settings-'+tag); app.canvas.tag_bind(rect,'<Button-1>',lambda e,fn=fn:app.run_action(fn))
        app.rendered_size=(width,height); return True
    finally: app._drawing_compact=False
