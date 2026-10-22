from page_frame import shared_scale, page_origin, APP_WIDTH, APP_HEIGHT
"""Pixel-accurate trace of Screen 10: Moon Diary."""
from pathlib import Path
import tkinter as tk
from page_frame import draw_panel
from datetime import datetime
from row_shape import draw as row_shape

SOURCE_BOX=(406,754,759,1014); BASE_SIZE=(353,260)
def draw(app):
    if not getattr(app,'diary_trace',False) or app.screen!='diary': return False
    app._drawing_compact=True
    try:
        if not hasattr(app,'board_source'): app.board_source=tk.PhotoImage(file=str(Path(__file__).with_name('reference_current.png')))
        width,height=(APP_WIDTH,APP_HEIGHT); fit=shared_scale(app); ow,oh=round(353*fit),round(260*fit)
        raw=tk.PhotoImage(width=353,height=260); raw.tk.call(str(raw),'copy',str(app.board_source),'-from',*SOURCE_BOX,'-to',0,0)
        panel=app.resized(raw,ow,oh,('diary-trace',ow,oh)); app.images.append(panel); app.canvas.configure(width=width,height=height,bg='#d5d2ff'); ox,oy=page_origin(app); draw_panel(app, panel, ox, oy, fit, BASE_SIZE); app.controls={}
        entries=sorted(app.store.data.get('readings',[]), key=lambda entry:entry.get('date',''), reverse=True)
        app.canvas.create_rectangle(ox+round(17*fit),oy+round(53*fit),ox+round(338*fit),oy+round(225*fit),fill='#fff8f2',outline='')
        if not entries:
            from little_steps import icon
            book=icon(app,'Read a few pages of something you enjoy')
            book=app.resized(book,round(24*fit),round(24*fit),('empty-diary-book',fit))
            app.images.append(book)
            app.canvas.create_image(ox+round(176*fit),oy+round(93*fit),image=book,tags='empty-diary-icon')
            app.canvas.create_text(ox+round(176*fit),oy+round(130*fit),text='Your Moon Diary is waiting\nfor its first little journey ✦',fill='#3f3a8a',font=(app.font_family,-max(10,round(11*fit))))
        app.page=max(0,min(getattr(app,'page',0),max(0,(len(entries)-1)//4)))
        for i,reading in enumerate(entries[app.page*4:app.page*4+4]):
            y=54+i*41; tag='diary-entry-'+str(i)
            rect=app.canvas.create_rectangle(ox+round(18*fit),oy+round(y*fit),ox+round(336*fit),oy+round((y+37)*fit),fill='#fff8f2',outline='#d4c7ee',tags=tag)
            visual=row_shape(app.canvas,app.canvas.coords(rect),'#fff8f2','#d4c7ee')
            app.selection_styles.append(dict(item=rect,visual_item=visual,parts=[rect,visual],selected=False,group='diary-rows',normal_fill='#fff8f2'))
            app.canvas.itemconfigure(rect,fill='',outline='')
            from card_art import image as tarot_image
            thumbnail=tarot_image(app,reading['cards'][0],round(28*fit),round(34*fit))
            app.images.append(thumbnail)
            app.canvas.create_image(ox+round(22*fit),oy+round((y+2)*fit),image=thumbnail,anchor='nw')
            # Three compact lines, as in the original diary: date, summary,
            # then category / optional step. Reserve the right action column.
            date=reading.get('date','')[:10]
            try:
                parsed=datetime.fromisoformat(reading.get('date',''))
                date=f"{parsed.day} {parsed.strftime('%b %Y')}"
            except (ValueError,TypeError):pass
            cards=reading.get('cards') or []
            summary=reading.get('summary') or reading.get('title') or (cards[0].get('meaning') if cards else None) or 'A little guidance saved.'
            right=230 if reading.get('step') else 310
            def line(text,dy,color,size=10):
                item=app.canvas.create_text(ox+round(69*fit),oy+round((y+dy)*fit),text=str(text),anchor='nw',fill=color,font=(app.font_family,-max(9,round(size*fit))),tags='diary-row-text')
                visible=str(text)
                while visible and app.canvas.bbox(item)[2]>ox+round(right*fit):
                    visible=visible[:-1].rstrip()
                    app.canvas.itemconfigure(item,text=visible+'…')
                return item
            line(date,1,'#10149a')
            line(summary,12,'#10149a')
            category=reading.get('intention','General')
            step=reading.get('step') or ''
            category_item=line(category,25,'#65518e',9)
            if step:
                chip_left=app.canvas.bbox(category_item)[2]+round(5*fit)
                chip_right=ox+round(right*fit)
                chip=row_shape(app.canvas,(chip_left,oy+round((y+24)*fit),chip_right,oy+round((y+36)*fit)),'#ede3fb','')
                label=app.canvas.create_text(chip_left+round(3*fit),oy+round((y+25)*fit),text='♪ '+step,anchor='nw',fill='#65518e',font=(app.font_family,-max(9,round(8*fit))),tags='diary-step-chip')
                visible='♪ '+step
                while visible and app.canvas.bbox(label)[2]>chip_right-round(3*fit):
                    visible=visible[:-1].rstrip();app.canvas.itemconfigure(label,text=visible+'…')
            app.canvas.tag_bind(tag,'<Button-1>',lambda e,reading=reading:app.run_action(lambda:_open_entry(app,reading,True)))
            if reading.get('step'):
                button=app.canvas.create_rectangle(ox+round(237*fit),oy+round((y+7)*fit),ox+round(330*fit),oy+round((y+30)*fit),fill='#ffe1f0',outline='#d65aa0')
                completed=(reading.get('followup_status') or reading.get('follow_up_status')) in ('Tried','Still working on it','Changed my mind')
                visual=row_shape(app.canvas,app.canvas.coords(button),'' if completed else '#ffe1f0','' if completed else '#d65aa0')
                app.selection_styles.append(dict(item=button,visual_item=visual,parts=[button,visual],selected=False,group='diary-actions',normal_fill='' if completed else '#ffe1f0',outline_only=completed))
                app.canvas.itemconfigure(button,fill='',outline='')
                app.canvas.create_text(ox+round(283*fit),oy+round((y+18)*fit),text={'Tried':'✓ Tried','Still working on it':'Still working','Changed my mind':'Changed mind'}.get(reading.get('followup_status') or reading.get('follow_up_status'),'Follow-up →'),tags='diary-followup-label',fill='#65518e' if completed else '#10149a',font=(app.font_family,-max(9,round((9 if completed else 10)*fit))))
                app.canvas.tag_bind(button,'<Button-1>',lambda e,reading=reading:app.run_action(lambda:_open_entry(app,reading,True)))
            else:
                app.canvas.create_text(ox+round(323*fit),oy+round((y+18)*fit),text='›',fill='#8070cf',font=(app.font_family,-round(20*fit)),tags='diary-arrow')
        for tag,box,fn in [('new',(18,229,186,253),app.new_reading),('clear',(193,229,334,253),app.clear_diary)]:
            x,y,r,b=box; rect=app.canvas.create_rectangle(ox+round(x*fit),oy+round(y*fit),ox+round(r*fit),oy+round(b*fit),outline='',tags='diary-'+tag); app.canvas.tag_bind(rect,'<Button-1>',lambda e,fn=fn:app.run_action(fn))
        app.rendered_size=(width,height); return True
    finally: app._drawing_compact=False

def _open_entry(app,reading,followup=False):
    from copy import deepcopy
    app.reading=deepcopy(reading)
    app.note=reading.get('note','')
    from selection_state import choose
    choose(app,"intentions",reading.get("selected_intention"))
    app.intention=reading.get('intention','General')
    app.question.set(reading.get('question',''))
    if followup: app.go('followup' if reading.get('step') else 'reflect')
    else: app.go('reading')

def turn_page(app,delta):
    if app.screen!='diary':return
    count=len(app.store.data.get('readings',[]))
    page=max(0,min(getattr(app,'page',0)+delta,max(0,(count-1)//4)))
    if page!=getattr(app,'page',0):app.page=page;app.render()
    return 'break'
