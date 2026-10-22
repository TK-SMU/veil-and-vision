from page_frame import shared_scale, page_origin, APP_WIDTH, APP_HEIGHT
"""Pixel-accurate trace of Screen 11: Revisit Your Step."""
from pathlib import Path
import tkinter as tk
from page_frame import draw_panel
from selection_style import apply as selection_style
from check_badge import draw as draw_check
from tkinter import messagebox
from bounded_text import fit as fit_text
from row_shape import draw as row_shape
from selection_style import tint_fill

SOURCE_BOX=(779,754,1134,1014); BASE_SIZE=(355,260); STATUSES=['Tried','Still working on it','Changed my mind']
def draw(app):
    if not getattr(app,'followup_trace',False) or app.screen!='followup': return False
    app._drawing_compact=True
    try:
        if not hasattr(app,'board_source'): app.board_source=tk.PhotoImage(file=str(Path(__file__).with_name('reference_current.png')))
        width,height=(APP_WIDTH,APP_HEIGHT); fit=shared_scale(app); ow,oh=round(355*fit),round(260*fit)
        raw=tk.PhotoImage(width=355,height=260); raw.tk.call(str(raw),'copy',str(app.board_source),'-from',*SOURCE_BOX,'-to',0,0)
        from artwork_text import clear as clear_art_text
        # Remove the reference's fixed music note from the existing icon slot.
        clear_art_text(raw,(59,38,107,76),108)
        panel=app.resized(raw,ow,oh,('followup-trace',ow,oh)); app.images.append(panel); app.canvas.configure(width=width,height=height,bg='#d5d2ff'); ox,oy=page_origin(app); draw_panel(app, panel, ox, oy, fit, BASE_SIZE); app.controls={}
        reading=app.reading or {}
        draft=_draft(app)
        from little_steps import icon as step_icon
        step=reading.get('step') or ''
        if step:
            bounds=(ox+round(60*fit),oy+round(39*fit),ox+round(106*fit),oy+round(75*fit))
            row_shape(app.canvas,bounds,'#f8d7ec','#e6c5ed',max(1,round(fit)))
            source=step_icon(app,step)
            # Trim transparent padding so the illustration fills the badge.
            pixels=[(x,y) for y in range(source.height()) for x in range(source.width())
                    if not source.transparency_get(x,y)]
            left=min(x for x,y in pixels);top=min(y for x,y in pixels)
            right=max(x for x,y in pixels)+1;bottom=max(y for x,y in pixels)+1
            cropped=tk.PhotoImage(width=right-left,height=bottom-top)
            cropped.tk.call(str(cropped),'copy',str(source),'-from',left,top,right,bottom,'-to',0,0)
            scale=min(38*fit/cropped.width(),30*fit/cropped.height())
            picture=app.resized(cropped,round(cropped.width()*scale),round(cropped.height()*scale),
                                ('followup-step-icon-large',step))
            app.images.append(picture)
            app.canvas.create_image(ox+round(83*fit),oy+round(57*fit),image=picture,
                                    tags=('followup-step-icon','step:'+step))

        def clear(box):
            x,y,r,b=box
            app.canvas.create_rectangle(ox+round(x*fit),oy+round(y*fit),ox+round(r*fit),oy+round(b*fit),fill='#fff8f2',outline='')
        clear((94,23,310,35))
        app.canvas.create_text(ox+round(202*fit),oy+round(29*fit),text=reading.get('date','')[:10]+' · '+reading.get('intention','General'),fill='#10149a',font=(app.font_family,-max(9,round(10*fit))))
        clear((109,41,306,73))
        app.canvas.create_text(ox+round(112*fit),oy+round(43*fit),anchor='nw',text='My little step',fill='#10149a',font=(app.font_family,-max(9,round(10*fit))))
        step_item=app.canvas.create_text(ox+round(112*fit),oy+round(56*fit),anchor='nw',width=round(191*fit),text=reading.get('step') or 'No Little Step chosen',fill='#3f3a8a',font=(app.font_family,-max(9,round(10*fit))))
        fit_text(app.canvas,step_item,oy+round(76*fit))
        for i,status in enumerate(STATUSES):
            x,y,r,b=36,97+i*24,319,117+i*24; selected=draft.get('followup_status')==status
            rect=app.canvas.create_rectangle(ox+round(x*fit),oy+round(y*fit),ox+round(r*fit),oy+round(b*fit),fill='#ffc6e3' if selected else '#fffbf2',outline='#d65aa0' if selected else '#ccc2f5',width=max(1,round(fit)),tags='status-'+str(i))
            selection_style(app,rect,selected,'followup-status',normal_fill='#ffe4f1' if i==0 else '#fffbf2')
            style=app.selection_styles[-1]
            # Paint only the original rounded row; retain a transparent hit area.
            for extra in style['parts'][1:]:app.canvas.delete(extra)
            visual=row_shape(app.canvas,app.canvas.coords(rect),
                tint_fill(style['normal_fill']) if selected else style['normal_fill'],
                '#d65aa0' if selected else '#ccc2f5',max(1,round(fit)))
            app.canvas.itemconfigure(rect,fill='',outline='')
            style.update(visual_item=visual,parts=[rect,visual])
            app.canvas.create_text(ox+round(177*fit),oy+round((y+10)*fit),text=status,tags=('followup-status-label','followup-status-label-'+str(i)),fill='#3f3a8a',font=(app.font_family,-max(9,round(10*fit))))
            bounds=(ox+round(297*fit),oy+round((y+3)*fit),ox+round(311*fit),oy+round((y+17)*fit))
            if selected:draw_check(app.canvas,bounds,tag='followup-check')
            else:app.canvas.create_oval(*bounds,outline='#a79bea',fill='#fffbf2')
            app.canvas.tag_bind(rect,'<Button-1>',lambda e,status=status:app.run_action(lambda:_choose(app,status)))
        # Real editable reflection field.
        from inline_fields import panel_color
        field=tk.Text(app.canvas,wrap='word',relief='flat',bd=0,highlightthickness=0,bg=panel_color(app,40,191,fit),fg='#3f3a8a',insertbackground='#3f3a8a',selectbackground='#efbfdc',selectforeground='#3f3a8a',font=(app.font_family,-max(9,round(9*fit))),height=2)
        field.insert('1.0',draft.get('reflection','')); app.canvas.create_window(ox+round(177*fit),oy+round(191*fit),window=field,width=round(270*fit),height=round(31*fit)); app.widgets.append(field); app.followup_field=field
        if not draft.get('reflection'):
            field.insert('1.0','Anything you want to remember?');field.placeholder=True
            field.configure(fg='#8a7daa')
        def focus_in(event):
            if getattr(field,'placeholder',False):
                field.delete('1.0','end');field.placeholder=False;field.configure(fg='#3f3a8a')
        field.bind('<FocusIn>',focus_in)
        for tag,box,fn in [('save',(35,214,319,235),lambda:_save(app)),('back',(96,236,259,256),lambda:_back(app))]:
            x,y,r,b=box; rect=app.canvas.create_rectangle(ox+round(x*fit),oy+round(y*fit),ox+round(r*fit),oy+round(b*fit),outline='',tags='followup-'+tag); app.canvas.tag_bind(rect,'<Button-1>',lambda e,fn=fn:app.run_action(fn))
        app.rendered_size=(width,height); return True
    finally: app._drawing_compact=False
def _draft(app):
    if not hasattr(app,'followup_drafts'):app.followup_drafts={}
    reading=app.reading or {}
    status=reading.get('followup_status') or reading.get('follow_up_status','')
    if status not in STATUSES:status=''
    return app.followup_drafts.setdefault(reading.get('id'),dict(followup_status=status,reflection=reading.get('reflection','')))

def _capture(app):
    field=getattr(app,'followup_field',None)
    if field is not None and field.winfo_exists():
        _draft(app)['reflection']='' if getattr(field,'placeholder',False) else field.get('1.0','end-1c')[:2000]

def _choose(app,status):
    if status not in STATUSES:return
    _capture(app)
    _draft(app)['followup_status']=status
    app.render()

def _save(app):
    _capture(app)
    reading=app.reading or {}
    entry=next((r for r in app.store.data['readings'] if r['id']==reading.get('id')),None)
    if entry is None:
        messagebox.showinfo('Moon Diary','This reading is no longer in Moon Diary.',parent=app.root)
        return
    entry.update(_draft(app))
    # Keep one canonical saved field; accept the alternate spelling on load.
    entry.pop('follow_up_status',None)
    app.store.write()
    app.reading=entry
    app.go('diary')

def _back(app):
    _capture(app)
    app.go('diary')
