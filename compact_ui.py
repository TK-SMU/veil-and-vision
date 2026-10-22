"""Compact reference panels with image-backed, keyboard-operable controls.

Coordinates refer to the supplied landscape design. Every panel fits the same
artwork-sized window; control crops come from the scaled panel itself.
"""
import tkinter as tk
from tkinter.simpledialog import askstring
from pathlib import Path
from wardrobe import OPTIONS, LABELS

BOXES = {'intro':(49,6,386,367),'oracle':(406,6,758,367),
'intention':(778,6,1134,367),'draw':(1154,6,1488,367),
'revealed':(37,395,387,727),'meaning':(406,395,758,727),
'reading':(778,395,1134,727),'reflect':(1154,395,1500,727),
'save':(37,750,387,1007),'diary':(406,750,758,1007),
'followup':(778,750,1134,1007),'settings':(1154,750,1500,1007)}

# Portrait proportions of the user's original ten-panel reference.
WINDOW_WIDTH, WINDOW_HEIGHT = 463, 778


def draw(a):
    if getattr(a, 'intro_trace', False) and a.screen == 'intro':
        from intro_ui import draw as draw_intro
        return draw_intro(a)
    if getattr(a, 'oracle_trace', False) and a.screen == 'oracle':
        from oracle_trace import draw as draw_oracle
        return draw_oracle(a)
    if getattr(a, 'intention_trace', False) and a.screen == 'intention':
        from intention_trace import draw as draw_intention
        return draw_intention(a)
    if getattr(a, 'draw_trace', False) and a.screen == 'draw':
        from draw_trace import draw as draw_cards
        return draw_cards(a)
    if getattr(a, 'revealed_trace', False) and a.screen == 'revealed':
        from revealed_trace import draw as draw_revealed
        return draw_revealed(a)
    if getattr(a, 'meaning_trace', False) and a.screen == 'meaning':
        from meaning_trace import draw as draw_meaning
        return draw_meaning(a)
    if getattr(a, 'reading_trace', False) and a.screen == 'reading':
        from reading_trace import draw as draw_reading
        return draw_reading(a)
    if getattr(a, 'reflect_trace', False) and a.screen == 'reflect':
        from reflect_trace import draw as draw_reflect
        return draw_reflect(a)
    if getattr(a, 'save_trace', False) and a.screen == 'save':
        from save_trace import draw as draw_save
        return draw_save(a)
    if getattr(a, 'diary_trace', False) and a.screen == 'diary':
        from diary_trace import draw as draw_diary
        return draw_diary(a)
    if getattr(a, 'followup_trace', False) and a.screen == 'followup':
        from followup_trace import draw as draw_followup
        return draw_followup(a)
    if getattr(a, 'settings_trace', False) and a.screen == 'settings':
        from settings_trace import draw as draw_settings
        return draw_settings(a)
    if getattr(a, 'board_mode', False):
        from board_ui import draw as draw_board
        return draw_board(a)
    if a.screen not in BOXES:
        return False
    a._drawing_compact=True
    if not hasattr(a,'compact_source'):
        a.compact_source=tk.PhotoImage(file=str(Path(__file__).with_name('target_12_screen_reference.png')))
    if a.screen=='oracle':
        # Page 2 has its own supplied wardrobe artwork and 3-column layout.
        from wardrobe_ui import draw as draw_wardrobe
        a.costume_preview()
        try:
            draw_wardrobe(a)
        finally:
            a._drawing_compact=False
        return True
    from portrait_ui import draw as draw_portrait
    try:
        return draw_portrait(a)
    finally:
        a._drawing_compact=False
    left,top,right,bottom=BOXES[a.screen]
    s=min(a.scale,(a.root.winfo_screenheight()-130)/WINDOW_HEIGHT,
          (a.root.winfo_screenwidth()-80)/WINDOW_WIDTH)
    width,height=round(WINDOW_WIDTH*s),round(WINDOW_HEIGHT*s)
    viewport=getattr(a,'desktop_viewport',None)
    if viewport:
        width,height=viewport
    # Use one scale for art, controls and type. Fit the window to the art.
    fit=min(width/(right-left),height/(bottom-top))
    sx=sy=fit
    content_width=round((right-left)*fit)
    content_height=round((bottom-top)*fit)
    ox=(width-content_width)//2
    oy=(height-content_height)//2
    def bounds(box):
        x,y,r,b=box
        return round((x-left)*sx),round((y-top)*sy),round((r-left)*sx),round((b-top)*sy)
    def crop(box,w,h,key):
        raw=tk.PhotoImage(width=box[2]-box[0],height=box[3]-box[1])
        raw.tk.call(str(raw),'copy',str(a.compact_source),'-from',*box,'-to',0,0)
        return a.resized(raw,w,h,('compact',key,w,h))
    panel=crop(BOXES[a.screen],content_width,content_height,a.screen)
    a.images.append(panel)
    a.canvas.configure(width=width,height=height,bg='#d4d3ff')
    x=max(0,min(a.root.winfo_x(),a.root.winfo_screenwidth()-width-20))
    y=max(30,min(a.root.winfo_y(),a.root.winfo_screenheight()-height-90))
    a.rendered_size=(width,height)
    if not viewport:
        a.root.geometry(f'{width}x{height}+{x}+{y}')
    a.canvas.create_image(ox,oy,anchor='nw',image=panel)
    a.controls={}
    def text(box,value,size=11):
        x,y,r,b=bounds(box)
        a.canvas.create_rectangle(x+ox,y+oy,r+ox,b+oy,fill='#fff7f4',outline='')
        a.canvas.create_text(x+ox+3,y+oy+2,anchor='nw',text=value,width=r-x-6,
            fill='#10149a',font=(a.font_family,-max(8,round(size*fit))))
    def button(box,label,fn,selected=False,caption=None):
        x,y,r,b=bounds(box)
        skin=tk.PhotoImage(width=r-x,height=b-y)
        skin.tk.call(str(skin),'copy',str(panel),'-from',x,y,r,b,'-to',0,0)
        a.images.append(skin)
        widget=tk.Button(a.canvas,image=skin,text=label,command=lambda:a.run_action(fn),
            bd=0,highlightthickness=0,relief='flat',padx=0,pady=0,takefocus=True,cursor='hand2')
        if caption is not None:
            widget.configure(image='',text=caption,bg='#eee4ff',fg='#10149a',
                activebackground='#ddcaff',font=(a.font_family,-max(8,round(11*fit))),wraplength=r-x-8)
        a.canvas.create_window(x+ox,y+oy,anchor='nw',window=widget,width=r-x,height=b-y)
        a.widgets.append(widget);a.controls[label]=widget
        widget.bind('<Return>',lambda e:(widget.invoke(),'break')[1])
        widget.bind('<FocusIn>',lambda e:widget.configure(relief='solid',bd=1))
        widget.bind('<FocusOut>',lambda e:widget.configure(relief='flat',bd=0))
        if selected:
            widget.configure(relief='solid',bd=2,highlightbackground='#a062ed')
        from click_feedback import bind_feedback
        bind_feedback(widget)
        return widget
    def go(screen):a.go(screen)
    def choose(key,value):a.reading[key]=value;a.render()
    def edit(key,title):
        value=askstring(title,'Optional — a few words are enough.',initialvalue=a.reading.get(key,''),parent=a.root)
        if value is not None:choose(key,value[:1000])
    def save():
        a.store.save(a.reading,a.reading.get('note',a.note));a.page=0;go('save')
    def card(c,box):
        idx=0 if c['name'] in ('The Lovers','The Empress') else 2 if c['name'] in ('The Star','The Sun','The World') else 1
        source=[(66,450,157,578),(170,450,259,578),(271,450,363,578)][idx]
        x,y,r,b=bounds(box)
        from card_art import image as tarot_image
        img=tarot_image(a,c,r-x,b-y);a.images.append(img)
        a.canvas.create_image(x+ox,y+oy,anchor='nw',image=img)
        text((box[0]+3,box[3]-15,box[2]-3,box[3]-2),c['name'],8)
    # Match the three illustrated titlebar controls on each source panel.
    for offset,label,fn in [(69,'Minimize',a.minimize),(48,'Zoom',lambda:a.zoom(-.5 if a.scale>=2 else .5)),(27,'Close',a.close)]:
        button((right-offset,top+5,right-offset+19,top+25),label,fn)
    screen=a.screen
    if screen=='intro':
        for box,label,target in [((96,238,340,269),'Start','oracle'),((96,271,340,302),'Moon Diary','diary'),((96,303,340,334),'Settings','settings')]:
            button(box,label,lambda target=target:go(target))
    elif screen=='oracle':
        a.costume_preview()
        x,y,r,b=bounds((442,78,721,177))
        scene=a.resized(a.oracle_scene,r-x,b-y,('compact-costume',tuple(a.settings.get(k) for k in ('hat','buddy','accessory','selected_background'))))
        a.images.append(scene);a.canvas.create_image(x+ox,y+oy,anchor='nw',image=scene)
        for i,category in enumerate(OPTIONS):
            button((424+i*81,182,502+i*81,206),category,lambda c=category:a.set_category(c),category==a.category)
        key,choices=OPTIONS[a.category];page=getattr(a,'wardrobe_pages',{}).get(a.category,0)
        for i,choice in enumerate(choices[page*6:page*6+6]):
            x=423+i%3*109;y=212+i//3*61;box=(x,y,x+105,y+58)
            widget=button(box,choice,lambda v=choice:a.change(**{key:v}),a.settings.get(key)==choice,caption=LABELS.get(choice,choice))
            if choice!='None':
                px,py,pr,pb=bounds(box)
                icon=(a.wardrobe_background(choice,round(55*fit),round(27*fit)) if a.category=='Backgrounds' else a.wardrobe_sprite(a.category,choice,round(55*fit),round(27*fit)))
                a.images.append(icon);widget.configure(image=icon,compound='top')
        button((431,114,455,153),'Previous style',lambda:a.cycle_style(-1))
        button((708,114,733,153),'Next style',lambda:a.cycle_style(1))
        button((488,336,678,360),'Next',lambda:go('intention'))
    elif screen=='intention':
        from VeilAndVision import INTENTIONS
        for i,v in enumerate(INTENTIONS):
            x=794+i%4*82;y=79+i//4*75
            button((x,y,x+79,y+70),v,lambda v=v:a.select_intention(v),v==a.intention)
        def question():
            v=askstring('Your question','What is on your heart?',initialvalue=a.question.get(),parent=a.root)
            if v is not None:a.question.set(v)
        button((795,243,1120,283),'Add a question',question)
        button((853,298,1062,335),'Next',a.begin)
    elif screen=='draw':
        for i in range(3):
            box=(1177+i*96,104,1265+i*96,233)
            widget=button(box,'Choose '+str(i+1),lambda i=i:a.pick(i),i in a.chosen)
            if i in a.chosen:
                from card_art import image as tarot_image
                x,y,r,b=bounds(box)
                art=tarot_image(a,a.reading['cards'][i],r-x,b-y)
                a.images.append(art);widget.configure(image=art)
    elif screen=='revealed':
        for i,c in enumerate(a.reading['cards']):
            box=(65+i*103,449,157+i*103,579)
            button(box,'Read '+c['name'],lambda i=i:a.open_card(i))
            # Put live card artwork inside its own clickable image control.
            idx=0 if c['name']=='The Lovers' else 2 if c['name']=='The Star' else 1
            widget=a.controls['Read '+c['name']];x,y,r,b=bounds(box)
            from card_art import image as tarot_image
            img=tarot_image(a,c,r-x,b-y)
            a.images.append(img);widget.configure(image=img)
            text((65+i*103,597,158+i*103,617),c['orientation'],10)
        button((166,692,373,721),'View Reading',lambda:go('reading'))
    elif screen=='meaning':
        c=a.reading['cards'][a.card_index];card(c,(442,431,546,570))
        tabs=['Meaning','In This Position','For Your Question','Keywords']
        for i,t in enumerate(tabs):
            button((558+i%2*94,449+i//2*27,648+i%2*94,474+i//2*27),t,lambda t=t:a.set_tab(t),t==a.meaning_tab)
        content={'Meaning':c['meaning'],'In This Position':c['context'],'For Your Question':c['guidance'],'Keywords':', '.join(c['keywords'])}[a.meaning_tab]
        text((558,507,744,579),content,10)
        text((553,426,744,448),c['name'],12)
        button((491,693,677,717),'Back to Cards',lambda:go('revealed'))
    elif screen=='reading':
        for i,c in enumerate(a.reading['cards']):
            text((849,466+i*52,1116,512+i*52),c['position']+' — '+c['name']+'\n'+c['meaning'],10)
        button((808,669,1127,695),'Choose a Little Step',lambda:go('reflect'))
        button((808,697,1127,720),'Save Reading Only',save)
    elif screen=='reflect':
        steps=['Listen to a favourite song','Take a short pause','Get some fresh air']
        for i,v in enumerate(steps):button((1171,465+i*47,1479,511+i*47),v,lambda v=v:choose('step',v),a.reading.get('step')==v)
        button((1171,609,1479,636),'Add a note',lambda:edit('note','Add a note'))
        button((1186,644,1465,678),'Save to Moon Diary',save)
        button((1280,681,1375,702),'Maybe later',save)
    elif screen=='save':
        for i,c in enumerate(a.reading['cards']):card(c,(53+i*50,848,98+i*50,909))
        text((235,862,370,912),a.reading.get('step') or 'Reading saved',11)
        button((181,960,373,982),'Done for Now',lambda:go('intro'))
        button((181,984,373,1001),'View Diary',lambda:go('diary'))
    elif screen=='diary':
        readings=a.store.data['readings'];pages=max(1,(len(readings)+3)//4);a.page=min(a.page,pages-1)
        text((420,810,746,979),'')
        def load(r):a.reading=dict(r);a.note=r.get('note','');go('followup')
        for i,r in enumerate(readings[a.page*4:a.page*4+4]):
            y=811+i*41
            button((423,y,745,y+39),'Entry '+r['id'],lambda r=r:load(r),caption=r['date'][:10]+' · '+r['intention']+'   Follow up →')
        if not readings:text((440,837,720,925),'Your story starts here.\nSave a reading to begin. ♡',13)
        button((428,982,609,1001),'New Reading',lambda:go('intention'))
        button((620,982,735,1001),'Clear Diary',a.clear_diary)
        if pages>1:
            button((425,963,497,979),'Previous',lambda:a.diary_page(-1) if a.page else None,caption='‹ Previous')
            button((665,963,740,979),'More',lambda:a.diary_page(1) if a.page+1<pages else None,caption='More ›')
    elif screen=='followup':
        text((873,801,1114,831),a.reading.get('step') or 'Your reading',10)
        for i,v in enumerate(['Tried','Still working on it','Changed my mind']):
            button((813,850+i*25,1114,874+i*25),v,lambda v=v:choose('followup_status',v),a.reading.get('followup_status')==v)
        button((814,927,1112,967),'Reflection',lambda:edit('reflection','Add a reflection'))
        def followup():a.store.save(a.reading,a.reading.get('note',''));go('diary')
        button((811,972,1120,988),'Save Follow-up',followup)
        button((893,989,1066,1003),'Back to Diary',lambda:go('diary'))
    elif screen=='settings':
        for i,v in enumerate(['Day','Sunset','Night']):button((1185+i*98,828,1277+i*98,882),v,lambda v=v:a.open_background(v),a.settings.get('selected_background')==v)
        for box,key in [((1270,893,1309,914),'music'),((1434,893,1473,914),'sound')]:
            widget=button(box,key,lambda key=key:a.toggle(key))
            x,y,r,b=bounds(box);img=a.resized(a.switch_image(bool(a.settings.get(key))),r-x,b-y,('compact-toggle',key,a.settings.get(key)))
            a.images.append(img);widget.configure(image=img)
        button((1267,919,1324,939),'Smaller',lambda:a.zoom(-.5))
        button((1388,919,1469,939),'Larger',lambda:a.zoom(.5))
        button((1175,942,1474,961),'About',a.about)
        button((1175,962,1474,981),'Clear Diary',a.clear_diary)
        button((1175,982,1320,1000),'Reset',a.reset)
        button((1323,982,1474,1000),'Back',lambda:go('intro'))
    a._drawing_compact=False
    return True
