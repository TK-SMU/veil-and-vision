from page_frame import shared_scale, page_origin, APP_WIDTH, APP_HEIGHT
"""Pixel-accurate trace of Screen 7: Overall Reading."""
from pathlib import Path
import tkinter as tk
from page_frame import draw_panel
from complete_panel import restore_edges
from bounded_text import fit as fit_text
from artwork_text import clear as clear_art_text

SOURCE_BOX=(780,416,1135,728); BASE_SIZE=(355,312)
def draw(app):
    if not getattr(app,'reading_trace',False) or app.screen!='reading': return False
    app._drawing_compact=True
    try:
        if not hasattr(app,'board_source'): app.board_source=tk.PhotoImage(file=str(Path(__file__).with_name('reference_current.png')))
        width,height=(APP_WIDTH,APP_HEIGHT); fit=shared_scale(app); ow,oh=round(355*fit),round(312*fit)
        raw=tk.PhotoImage(width=355,height=312); raw.tk.call(str(raw),'copy',str(app.board_source),'-from',*SOURCE_BOX,'-to',0,0)
        for i in range(3):
            y=62+i*52
            clear_art_text(raw,(76,y-1,329,y+43),25)
            clear_art_text(raw,(29,y+2,65,y+39),25)
        clear_art_text(raw,(76,215,329,259),25)
        panel=app.resized(raw,ow,oh,('reading-trace',ow,oh)); app.images.append(panel); app.canvas.configure(width=width,height=height,bg='#d5d2ff'); ox,oy=page_origin(app); draw_panel(app, panel, ox, oy, fit, BASE_SIZE); app.controls={}
        cards=(app.reading or {}).get('cards',[])
        for i,card in enumerate(cards[:3]):
            y=62+i*52; label=f"{card.get('position','')} — {card.get('name','')} {'↑' if card.get('orientation')=='Upright' else '↓'}"; short=card.get('meaning','A gentle message is waiting.').split('. ')[0].rstrip('.')+'.'
            from card_art import image as card_image
            thumbnail=card_image(app,card,round(25*fit),round(37*fit))
            app.images.append(thumbnail)
            app.canvas.create_image(ox+round(34*fit),oy+round((y+2)*fit),image=thumbnail,anchor='nw',tags='reading-thumbnail')
            title_item=app.canvas.create_text(ox+round(78*fit),oy+round(y*fit),tags=('reading-title',f'reading-row-{i}'),text=label,width=round(255*fit),anchor='nw',fill='#10149a',font=(app.font_family,-max(10,round(11*fit))))
            fit_text(app.canvas,title_item,oy+round((y+16)*fit))
            body_item=app.canvas.create_text(ox+round(78*fit),oy+round((y+17)*fit),tags=('reading-body',f'reading-row-{i}'),text=short,width=round(245*fit),anchor='nw',fill='#3f3a8a',font=(app.font_family,-max(9,round(10*fit))))
            fit_text(app.canvas,body_item,oy+round((y+40)*fit))
        app.canvas.create_text(ox+round(78*fit),oy+round(216*fit),text='Overall Message',anchor='nw',fill='#10149a',font=(app.font_family,-max(10,round(12*fit))))
        message='Choose three cards to begin.'
        if len(cards)==3:
            # Save exactly the overall message the user saw, rather than a
            # different template when the diary entry is reopened.
            message=app.reading.setdefault('interpretation',
                'For '+app.reading.get('intention',app.intention).lower()+', past lessons can guide a gentle next step. Explore '+cards[2]['meaning'].lower())
        from meaning_scroll import MeaningScroll
        MeaningScroll(app,message,(ox+round(78*fit),oy+round(232*fit),
                                  ox+round(328*fit),oy+round(257*fit)),fit,
                      font_size=10,color='#3f3a8a',name='reading')
        for tag,box,fn in [('step',(32,261,324,285),lambda:app.go('reflect')),('save',(32,288,324,307),app.save_reading_only)]:
            x,y,r,b=box; rect=app.canvas.create_rectangle(ox+round(x*fit),oy+round(y*fit),ox+round(r*fit),oy+round(b*fit),outline='',tags='reading-'+tag); app.canvas.tag_bind(rect,'<Button-1>',lambda e,fn=fn:app.run_action(fn))
        app.rendered_size=(width,height); return True
    finally: app._drawing_compact=False
