from page_frame import shared_scale, page_origin, APP_WIDTH, APP_HEIGHT
"""Pixel-accurate trace of Screen 9: Saved to Moon Diary."""
from pathlib import Path
import tkinter as tk
from page_frame import draw_panel
from check_badge import draw as draw_check

SOURCE_BOX=(27,754,389,1014); BASE_SIZE=(362,260)
def draw(app):
    if not getattr(app,'save_trace',False) or app.screen!='save': return False
    app._drawing_compact=True
    try:
        if not hasattr(app,'board_source'): app.board_source=tk.PhotoImage(file=str(Path(__file__).with_name('reference_current.png')))
        width,height=(APP_WIDTH,APP_HEIGHT); fit=shared_scale(app); ow,oh=round(362*fit),round(260*fit)
        raw=tk.PhotoImage(width=362,height=260); raw.tk.call(str(raw),'copy',str(app.board_source),'-from',*SOURCE_BOX,'-to',0,0)
        panel=app.resized(raw,ow,oh,('save-trace',ow,oh)); app.images.append(panel); app.canvas.configure(width=width,height=height,bg='#d5d2ff'); ox,oy=page_origin(app); draw_panel(app, panel, ox, oy, fit, BASE_SIZE); app.controls={}
        draw_check(app.canvas,(ox+round(100*fit),oy+round(24*fit),ox+round(159*fit),oy+round(82*fit)),tag='saved-check')
        if getattr(app,'reading',None):
            from card_art import image as tarot_image
            for i,card in enumerate(app.reading.get('cards',[])[:3]):
                x=[29,85,138][i]; y=84; img=tarot_image(app,card,round(47*fit),round(62*fit)); app.images.append(img); app.canvas.create_image(ox+round(x*fit),oy+round(y*fit),anchor='nw',image=img)
        step=(app.reading or {}).get('step','')
        app.canvas.create_rectangle(ox+round(203*fit),oy+round(84*fit),ox+round(344*fit),oy+round(154*fit),fill='#fff3fb',outline='#d8a8da',width=max(1,round(fit)))
        app.canvas.create_text(ox+round(273*fit),oy+round(95*fit),text='My little step',fill='#3f3a8a',font=(app.font_family,-max(9,round(10*fit))))
        app.canvas.create_text(ox+round(273*fit),oy+round(123*fit),text=step or 'No Little Step chosen',width=round(125*fit),fill='#10149a',font=(app.font_family,-max(9,round(10*fit))))
        for tag,box,fn in [('done',(151,202,342,227),lambda:app.go('intro')),('diary',(151,229,342,249),lambda:app.go('diary'))]:
            x,y,r,b=box; rect=app.canvas.create_rectangle(ox+round(x*fit),oy+round(y*fit),ox+round(r*fit),oy+round(b*fit),outline='',tags='save-'+tag); app.canvas.tag_bind(rect,'<Button-1>',lambda e,fn=fn:app.run_action(fn))
        # Secondary action in the spare margin; existing two buttons stay intact.
        y=min(APP_HEIGHT-32,oy+oh+22)
        app.canvas.create_text(APP_WIDTH/2,y,text='↻ Start New Reading',
            fill='#3f3a8a',font=(app.font_family,-round(11*fit)),tags='new-reading-label')
        box=app.canvas.bbox('new-reading-label')
        hit=app.canvas.create_rectangle(*box,fill='',outline='',tags='save-new')
        app.canvas.tag_bind(hit,'<Button-1>',lambda e:app.run_action(app.new_reading))
        app.rendered_size=(width,height); return True
    finally: app._drawing_compact=False
