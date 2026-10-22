from page_frame import shared_scale, page_origin, APP_WIDTH, APP_HEIGHT
"""Card Meaning: live content in Panel 6's measured reference regions."""
from pathlib import Path
import tkinter as tk
from page_frame import draw_panel
from selection_style import apply as selection_style
from selection_state import selected
from bounded_text import fit as fit_text
from artwork_text import clear as clear_art_text
SOURCE_BOX=(420,416,758,728)
BASE_SIZE=(338,312)
CARD_BOXES=[(35,35,139,176)]
TABS=['Meaning','Position','My Question','Keywords']
KEYWORD_BOXES=[(54,222,131,242),(138,222,215,242),(222,222,298,242),(54,249,125,269),(139,249,244,269)]

def draw(app):
    if not getattr(app,'meaning_trace',False) or app.screen!='meaning':return False
    width,height=APP_WIDTH,APP_HEIGHT;fit=shared_scale(app)
    ow,oh=round(338*fit),round(312*fit);ox,oy=page_origin(app)
    if not hasattr(app,'board_source'):app.board_source=tk.PhotoImage(file=str(Path(__file__).with_name('reference_current.png')))
    raw=tk.PhotoImage(width=338,height=312);raw.tk.call(str(raw),'copy',str(app.board_source),'-from',*SOURCE_BOX,'-to',0,0)
    for box,sample in [((148,26,245,51),145),((148,105,324,155),145),((83,183,297,212),296)]:
        clear_art_text(raw,box,sample)
    for x,y,r,b in KEYWORD_BOXES:
        clear_art_text(raw,(x+8,y+3,r-8,b-3),x+7)
    panel=app.resized(raw,ow,oh,('meaning-trace',ow,oh));app.images.append(panel)
    app.canvas.configure(width=width,height=height,bg='#d5d2ff');draw_panel(app,panel,ox,oy,fit,BASE_SIZE)
    card=app.reading['cards'][app.card_index]
    def rect(box,fill='#fff8f2',outline=''):
        x,y,r,b=box
        return app.canvas.create_rectangle(ox+round(x*fit),oy+round(y*fit),ox+round(r*fit),oy+round(b*fit),fill=fill,outline=outline)
    def text(x,y,value,size=12,w=174,anchor='nw'):
        return app.canvas.create_text(ox+round(x*fit),oy+round(y*fit),text=value,width=round(w*fit),anchor=anchor,justify='left',fill='#10149a',font=(app.font_family,-round(size*fit)))
    from card_art import image
    photo=image(app,card,round(104*fit),round(141*fit));app.images.append(photo)
    app.canvas.create_image(ox+round(35*fit),oy+round(35*fit),image=photo,anchor='nw',tags='card-result')
    fit_text(app.canvas,text(152,28,card['name'],18),oy+round(51*fit))
    for i,label in enumerate(TABS):
        x=152+(i%2)*91;y=53+(i//2)*26
        item=rect((x,y,x+84,y+22),'#f0eff9','#c8b5ea')
        selection_style(app,item,selected(app,'meaning-tabs',label),'meaning-tabs')
        text(x+42,y+11,label,11,80,'center')
        app.canvas.tag_bind(item,'<Button-1>',lambda e,label=label:app.run_action(lambda:app._set_meaning_tab(label)))
    content={'Meaning':card['meaning'],'Position':card.get('context',{}).get(card['position'],card['meaning']) if isinstance(card.get('context'),dict) else card.get('context',card['meaning']),
             'My Question':card.get('guidance',card['meaning']),
             'Keywords':' · '.join(card.get('keywords',[]))}[app.meaning_tab]
    from meaning_scroll import MeaningScroll
    MeaningScroll(app,content,(ox+round(152*fit),oy+round(109*fit),
                               ox+round(326*fit),oy+round(171*fit)),fit)
    text(83,184,card['position']+' · '+card['orientation']+(' ↓' if card['orientation']=='Reversed' else ' ↑'),11,207)
    text(83,199,'One gentle step is enough. ♡',11,207)
    keywords=card.get('keywords',[])[:5]
    for word,(x,y,r,b) in zip(keywords,KEYWORD_BOXES):
        fit_text(app.canvas,text((x+r)/2,(y+b)/2,word,10,r-x-8,'center'),oy+round((b-1)*fit))
    item=rect((90,277,268,303),'')
    app.canvas.tag_bind(item,'<Button-1>',lambda e:app.run_action(lambda:app.go('revealed')))
    app.rendered_size=(width,height)
    return True
