from page_frame import shared_scale, page_origin, APP_WIDTH, APP_HEIGHT
"""Pixel-accurate trace of Screen 8: One Little Step."""
from pathlib import Path
import tkinter as tk
from page_frame import draw_panel
from complete_panel import restore_edges
from selection_style import apply as selection_style
from inline_fields import edit, show_value
from check_badge import draw as draw_check
from little_steps import suggestions, icon as step_icon

SOURCE_BOX=(1154,416,1509,728); BASE_SIZE=(355,312)
STEPS=['Listen to a favourite song','Take a short pause','Get some fresh air']
def draw(app):
    if not getattr(app,'reflect_trace',False) or app.screen!='reflect': return False
    app._drawing_compact=True
    try:
        if not hasattr(app,'board_source'): app.board_source=tk.PhotoImage(file=str(Path(__file__).with_name('reference_current.png')))
        width,height=(APP_WIDTH,APP_HEIGHT); fit=shared_scale(app); ow,oh=round(355*fit),round(312*fit)
        raw=tk.PhotoImage(width=355,height=312); raw.tk.call(str(raw),'copy',str(app.board_source),'-from',*SOURCE_BOX,'-to',0,0)
        panel=app.resized(raw,ow,oh,('reflect-trace',ow,oh)); app.images.append(panel); app.canvas.configure(width=width,height=height,bg='#d5d2ff'); ox,oy=page_origin(app); draw_panel(app, panel, ox, oy, fit, BASE_SIZE); app.controls={}
        restore_edges(app,SOURCE_BOX,ox,oy,fit)
        selected=(app.reading or {}).get('step','')
        options=suggestions(app.reading)
        for i,label in enumerate(options):
            x,y,r,b=25,71+i*40,331,105+i*40
            active=selected==label
            # Replace only the sample selection pixels with the real state.
            row_style=app.canvas.create_rectangle(ox+round(x*fit),oy+round(y*fit),ox+round(r*fit),oy+round(b*fit),fill='#ffc6e3' if active else '#fffbf2',outline='#d65aa0' if active else '#c8b5ea',width=max(1,round(fit)),tags='step-fill-'+str(i))
            selection_style(app,row_style,active,'little-step',normal_fill='#ffe4f1' if i==0 else '#fffbf2')
            source=step_icon(app,label)
            # Enlarge the artwork itself, excluding transparent sprite padding.
            pixels=[(px,py) for py in range(source.height()) for px in range(source.width())
                    if not source.transparency_get(px,py)]
            left=min(px for px,py in pixels);top=min(py for px,py in pixels)
            right=max(px for px,py in pixels)+1;bottom=max(py for px,py in pixels)+1
            cropped=tk.PhotoImage(width=right-left,height=bottom-top)
            cropped.tk.call(str(cropped),'copy',str(source),'-from',left,top,right,bottom,'-to',0,0)
            scale=min(38*fit/cropped.width(),28*fit/cropped.height())
            icon=app.resized(cropped,round(cropped.width()*scale),round(cropped.height()*scale),
                             ('step-icon-large',label))
            app.images.append(icon)
            app.canvas.create_image(ox+round(67*fit),oy+round((y+17)*fit),image=icon,tags='little-step-icon')
            app.canvas.create_text(ox+round(109*fit),oy+round((y+17)*fit),text=label,anchor='w',width=round(174*fit),fill='#10149a',font=(app.font_family,-max(10,round(11*fit))),tags='little-step-label')
            app.canvas.create_oval(ox+round(294*fit),oy+round((y+7)*fit),ox+round(314*fit),oy+round((y+27)*fit),fill='#ed8abd' if active else '#fffbf2',outline='#d65aa0' if active else '#a79bea',tags='step-check-'+str(i))
            if active:draw_check(app.canvas,(ox+round(294*fit),oy+round((y+7)*fit),ox+round(314*fit),oy+round((y+27)*fit)),tag='step-tick')
            tag='reflect-step-'+str(i); rect=app.canvas.create_rectangle(ox+round(x*fit),oy+round(y*fit),ox+round(r*fit),oy+round(b*fit),outline='',tags=tag)
            app.canvas.tag_bind(tag,'<Button-1>',lambda e,label=label:app.run_action(lambda:_choose(app,label)))
        show_value(app,(51,197,308,213),selected if selected not in options else '',fit,ox,oy)
        # Optional custom step field and actions.
        tag='reflect-custom'; rect=app.canvas.create_rectangle(ox+round(18*fit),oy+round(192*fit),ox+round(337*fit),oy+round(218*fit),outline='',tags=tag); app.canvas.tag_bind(tag,'<Button-1>',lambda e:app.run_action(lambda:_custom(app)))
        for tag,box,fn in [('save',(63,229,311,260),app.save_and_show_confirmation),('later',(145,269,218,284),lambda:_later(app))]:
            x,y,r,b=box; rect=app.canvas.create_rectangle(ox+round(x*fit),oy+round(y*fit),ox+round(r*fit),oy+round(b*fit),outline='',tags='reflect-'+tag); app.canvas.tag_bind(rect,'<Button-1>',lambda e,fn=fn:app.run_action(fn))
        app.rendered_size=(width,height); return True
    finally: app._drawing_compact=False

def _choose(app,value):
    if app.reading is not None: app.reading['step']=value
    app.render()
def _custom(app):
    def changed(value):
        if app.reading is None:return
        app.reading['step']=value
        for i in range(3):
            app.canvas.itemconfigure('step-fill-'+str(i),fill='#ffe4f1' if i==0 else '#fffbf2',outline='#c8b5ea')
            app.canvas.itemconfigure('step-check-'+str(i),fill='#fffbf2',outline='#a79bea')
        app.canvas.delete('step-tick')
        for style in app.selection_styles:
            if style['group']=='little-step':
                style['selected']=False
                style.pop('rest',None)
                for part in style['parts'][1:]:app.canvas.delete(part)
                style['parts']=style['parts'][:1]
    previous=(app.reading or {}).get('step','')
    edit(app,'step_entry',(51,197,308,213),BASE_SIZE,
         previous if previous not in suggestions(app.reading) else '',changed,200)

def _later(app):
    if app.reading is not None: app.reading["step"]=""
    app.save_and_show_confirmation()
