"""Live portrait layouts sharing the wardrobe's 463 × 778 design canvas.

Art fragments retain their aspect ratio. Text and controls are independent of
the reference images, so saved readings never overlap baked-in sample text.
"""
import tkinter as tk
import math
from pathlib import Path
from tkinter.simpledialog import askstring
from wardrobe_ui import ReferenceButton
from card_art import image as tarot_image
from design_system import COLORS,THEMES,TYPE,WINDOW,PANEL_PADDING,LINE_SPACING,font

INK = COLORS['ink']

def short_meaning(card):
    """A small teaser; the original interpretation remains available on demand."""
    if card['name']=='The Moon' and card['orientation']=='Reversed':
        return 'Clarity is returning.'
    sentence=card['meaning'].split('. ')[0].strip().rstrip('.')
    if len(sentence)>43:
        sentence=sentence[:40].rsplit(' ',1)[0]+'…'
    return sentence if sentence.endswith('…') else sentence+'.'


def draw(a):
    width, height = getattr(a, 'desktop_viewport', None) or WINDOW
    scale = min(width / 463, height / 778)
    ox, oy = (width - 463 * scale) / 2, (height - 778 * scale) / 2
    cv = a.canvas
    cv.configure(width=width, height=height, bg=THEMES['Day']['surround'])
    a.rendered_size = (width, height)
    a.controls = {}
    theme = 'Day'
    text_zoom=max(.9,min(1.1,float(a.settings.get('text_size',1))))
    paper = THEMES[theme]['paper']
    # Drawing Cards is naturally a moonlit scene; Night theme keeps that
    # atmosphere on every screen while Day and Sunset retain the same layout.
    night = theme == 'Night' or a.screen == 'draw'
    backdrop=tk.PhotoImage(width=width,height=height)
    backdrop.put('#2c2f7a' if night else paper,to=(0,0,width,height))

    def rect(x, y, w, h, fill=paper, outline='#d5c5ed'):
        points=[x+5,y,x+w-5,y,x+w,y+5,x+w,y+h-5,x+w-5,y+h,x+5,y+h,x,y+h-5,x,y+5]
        cv.create_polygon(*[ox+p*scale if i%2==0 else oy+p*scale for i,p in enumerate(points)],
                          fill=fill,outline=outline,width=max(1,scale))

    def text(x, y, value, size=TYPE['body'], w=405, anchor='n', color=INK, bold=False):
        return cv.create_text(ox+x*scale, oy+y*scale, text=value,
            font=font(size,scale*text_zoom,bold),
            fill=color, width=w*scale, anchor=anchor, justify='center' if anchor=='n' else 'left')

    def art(box, x, y, w, h):
        # Fit, never stretch, supplied artwork inside the requested region.
        bw, bh = box[2]-box[0], box[3]-box[1]
        fit = min(w/bw, h/bh)
        iw, ih = max(1,round(bw*fit*scale)), max(1,round(bh*fit*scale))
        key=('portrait-art',box,iw,ih)
        if key not in a.cache:
            raw=tk.PhotoImage(width=bw,height=bh)
            raw.tk.call(str(raw),'copy',str(a.compact_source),'-from',*box,'-to',0,0)
            a.cache[key]=a.resized(raw,iw,ih,key)
        img=a.cache[key];a.images.append(img)
        cv.create_image(ox+(x+w/2)*scale,oy+(y+h/2)*scale,image=img)
        backdrop.tk.call(str(backdrop),'copy',str(img),'-to',
                         round(ox+(x+w/2)*scale-iw/2),round(oy+(y+h/2)*scale-ih/2))

    def button(x,y,w,h,label,fn,selected=False,pink=False,display=None):
        under=None
        if pink:
            under=tk.PhotoImage(width=round(w*scale),height=round(h*scale))
            bx,by=round(ox+x*scale),round(oy+y*scale)
            under.tk.call(str(under),'copy',str(backdrop),'-from',bx,by,bx+under.width(),by+under.height(),'-to',0,0)
        widget=ReferenceButton(cv,round(w*scale),round(h*scale),display or label,
            lambda:a.run_action(fn),paper,font('button',scale,True),
            selected=selected,pink=pink,backdrop=under)
        widget.window_item=cv.create_window(ox+x*scale,oy+y*scale,anchor='nw',window=widget,
                         width=round(w*scale),height=round(h*scale))
        a.widgets.append(widget);a.controls[label]=widget
        if selected:
            widget.create_text((w-15)*scale,12*scale,text='✓',fill='#844bdd',
                               font=font('tab',scale,True))
        return widget

    def tile_art(widget,box,x,y,w,h,key):
        raw=tk.PhotoImage(width=box[2]-box[0],height=box[3]-box[1])
        raw.tk.call(str(raw),'copy',str(a.compact_source),'-from',*box,'-to',0,0)
        image=a.resized(raw,round(w*scale),round(h*scale),('reference-tile',key,scale))
        a.images.append(image)
        widget.create_image(x*scale,y*scale,anchor='nw',image=image)

    def label_in(widget,x,y,value,size=TYPE['body'],anchor='w',width=290):
        widget.create_text(x*scale,y*scale,text=value,anchor=anchor,fill=INK,
                           width=width*scale,font=font(size,scale))

    def go(page): a.go(page)
    def open_detail(index,origin):
        a.meaning_origin=origin
        a.open_card(index)
    def text_box(x,y,w,h,value,editable=False,key=None):
        field=tk.Text(cv,wrap='word',relief='flat',bd=0,padx=8,pady=8,
                      bg=paper,fg=INK,font=font('body',scale*text_zoom),spacing1=LINE_SPACING,spacing3=LINE_SPACING,
                      highlightthickness=1,highlightbackground=COLORS['border'],highlightcolor=COLORS['pink_border'])
        field.insert('1.0',value)
        if editable:
            field.edit_modified(False)
            def changed(event=None):
                if field.edit_modified():
                    a.reading[key]=field.get('1.0','end-1c')[:1000]
                    field.edit_modified(False)
            field.bind('<<Modified>>',changed)
        else:field.configure(state='disabled')
        cv.create_window(ox+x*scale,oy+y*scale,anchor='nw',window=field,width=(w-13)*scale,height=h*scale)
        scroll=tk.Scrollbar(cv,orient='vertical',command=field.yview)
        field.configure(yscrollcommand=scroll.set)
        cv.create_window(ox+(x+w-13)*scale,oy+y*scale,anchor='nw',window=scroll,width=13*scale,height=h*scale)
        a.widgets.append(scroll)
        a.widgets.append(field)
        return field
    def choose(key,value): a.reading[key]=value;a.render()
    def edit(key,title):
        value=askstring(title,'A few words, if you want to.',
                        initialvalue=a.reading.get(key,''),parent=a.root)
        if value is not None: choose(key,value[:1000])
    def save():
        if len(a.reading.get('cards',[]))!=3:return
        if a.sound and a.settings.get('sound'):a.sound.effect('save')
        a.store.save(a.reading,a.reading.get('note',a.note));a.page=0;go('save')
    def heading(title,subtitle=''):
        text(231.5,67,title,TYPE['heading'],bold=True,color='#fff8f1' if night else INK)
        if subtitle:text(231.5,101,subtitle,TYPE['body'],color='#fff8f1' if night else INK)
    def card(c,x,y,w=113,h=174,action=None,label=None,show_name=True):
        img=tarot_image(a,c,round(w*scale),round((h-28)*scale));a.images.append(img)
        if action:
            widget=button(x,y,w,h-28,label,action)
            widget.create_image(0,0,anchor='nw',image=img)
        else:cv.create_image(ox+x*scale,oy+y*scale,anchor='nw',image=img)
        if show_name:text(x+w/2,y+h-26,c['name'],TYPE['card_title'],w=w-4,bold=True,
                          color='#fff8f1' if night else INK)
        return widget if action else None
    def pick(index):
        if index in a.chosen:return
        a.flipping_card=index
        a.pick(index)
    def back_image(w,h):
        key=('portrait-back',w,h)
        if key not in a.cache:
            raw=tk.PhotoImage(width=83,height=126)
            raw.tk.call(str(raw),'copy',str(a.compact_source),'-from',1181,106,1264,232,'-to',0,0)
            a.cache[key]=a.resized(raw,w,h,key)
        return a.cache[key]
    def flip(widget,c):
        """Turn the card about its vertical axis without blocking Tk's event loop."""
        w,h=round(128*scale),round(196*scale)
        front=tarot_image(a,c,w,h);back=back_image(w,h)
        def frame(n=0):
            if not widget.winfo_exists():return
            progress=n/16
            fw=max(2,round(w*abs(math.cos(progress*math.pi))))
            source=back if progress<.5 else front
            pic=a.resized(source,fw,h,('flip',c.get('artwork_seed'),n,w,h))
            widget._flip_image=pic
            widget.delete('flip')
            if n==0:widget.delete('all')
            widget.create_image(w/2,h/2,image=pic,tags='flip')
            if n<16:a.typing_timers.append(a.root.after(24,lambda:frame(n+1)))
        frame()
    def lumi(y=490):
        a.costume_preview()
        source=a.oracle_foreground
        fit=min(170/source.width(),135/source.height())*scale
        img=a.resized(source,round(source.width()*fit),round(source.height()*fit),
                      ('portrait-lumi',tuple(a.settings.get(k) for k in ('hat','buddy','accessory')),scale))
        a.images.append(img)
        item=cv.create_image(ox+108*scale,oy+(y+66)*scale,image=img)
        rect(183,y+30,246,76)
        message={'draw':'Hmm… what will\nyour cards say? ♡',
                 'revealed':('Let’s look gently\nat this together. ♡' if any(c['orientation']=='Reversed' for c in a.reading['cards']) else 'Oh! A little surprise. ♡'),
                 'save':'Tucked into your diary.\nI’m proud of your little step! ♡',
                 'followup':'Thank you for checking in.\nSmall steps count. ♡'}.get(a.screen,'One gentle moment\nis enough. ♡')
        text(306,y+43,message,15,w=220)
        def bob(frame=0):
            if frame>22:return
            cv.coords(item,ox+108*scale,oy+(y+66-3*math.sin(frame*math.pi/11))*scale)
            a.typing_timers.append(a.root.after(35,lambda:bob(frame+1)))
        bob()

    # Shared titlebar and floral corners; no screenshot text under live controls.
    rect(2,2,459,774,'#a8a9f5','#373ab5')
    rect(7,46,449,725,'#2c2f7a' if night else paper,'#7978c9')
    if not night:
        if not hasattr(a,'floral_source'):
            a.floral_source=tk.PhotoImage(file=str(Path(__file__).with_name('floral_panel.png')))
        bg=a.resized(a.floral_source,round(449*scale),round(725*scale),('floral-panel',scale))
        a.images.append(bg);cv.create_image(ox+7*scale,oy+46*scale,anchor='nw',image=bg)
        backdrop.tk.call(str(backdrop),'copy',str(bg),'-to',round(ox+7*scale),round(oy+46*scale))
    else:
        for j in range(36):
            x=17+(j*83)%425;y=62+(j*127)%657
            text(x,y,'✦' if j%5==0 else '·',10,w=12,color='#ffe8ac')
    # Theme lighting is applied over the shared artwork without changing its
    # geometry.  The soft stipple reads like pixel-game color grading.
    if theme == 'Sunset':
        cv.create_rectangle(ox+7*scale, oy+46*scale,
                            ox+456*scale, oy+771*scale,
                            fill='#e6a4c4', outline='', stipple='gray25')
    elif theme == 'Night':
        cv.create_rectangle(ox+7*scale, oy+46*scale,
                            ox+456*scale, oy+771*scale,
                            fill='#25215f', outline='', stipple='gray50')
    # Small edge sparkles retain the airy reference decoration without reducing
    # the usable area for reading text or hit targets.
    for x,y in [(17,134),(445,263),(17,449),(444,578),(19,679)]:
        text(x,y,'✦',12,w=15,color='#ebbc77')
    # Use exactly the wardrobe titlebar across all screens, without re-lettering.
    if not hasattr(a,'wardrobe_source'):
        a.wardrobe_source=tk.PhotoImage(file=str(Path(__file__).with_name('wardrobe_reference.png')))
    header=tk.PhotoImage(width=463,height=46)
    header.tk.call(str(header),'copy',str(a.wardrobe_source),'-from',50,122,513,168,'-to',0,0)
    header=a.resized(header,round(463*scale),round(46*scale),('portrait-header',scale))
    a.images.append(header);cv.create_image(ox,oy,anchor='nw',image=header)
    rect(60,7,278,32,fill='#b5b2f6',outline='#b5b2f6')
    text(60,13,'Veil & Vision',18,w=179,anchor='nw')
    button(247,10,44,28,'Back',a.back,display='‹')
    button(297,10,43,28,'Home',lambda:go('intro'),display='⌂')
    for x,label,symbol,fn in [(347,'Minimize','−',a.minimize),
        (382,'Zoom','□',lambda:a.set_window_size(463,778)),(417,'Close','×',a.close)]:
        control=button(x,10,29,28,label,fn,pink=label=='Close',display=symbol)
        sx={'Minimize':399,'Zoom':432,'Close':466}[label]
        raw=tk.PhotoImage(width=27,height=28)
        raw.tk.call(str(raw),'copy',str(a.wardrobe_source),'-from',sx,131,sx+27,159,'-to',0,0)
        skin=a.resized(raw,round(29*scale),round(28*scale),('window-control',label,scale))
        a.images.append(skin);control.create_image(0,0,anchor='nw',image=skin)
    screen=a.screen
    if screen=='intro':
        # Rebuild the logo in the same font instead of baking a second family
        # into an illustration. The existing scenery and customized Lumi remain.
        scene=a.wardrobe_background('Day',round(417*scale),round(352*scale))
        a.images.append(scene);cv.create_image(ox+23*scale,oy+76*scale,anchor='nw',image=scene)
        backdrop.tk.call(str(backdrop),'copy',str(scene),'-to',round(ox+23*scale),round(oy+76*scale))
        rect(89,107,285,142,fill='#f0e8fb',outline='#dad0f5')
        text(233,123,'Veil & Vision',TYPE['logo'],w=275,bold=True,color='#b29bd0')
        text(231,121,'Veil & Vision',TYPE['logo'],w=275,bold=True)
        text(231,176,'A little guidance\nfor a brighter you ♡',15,w=264)
        a.costume_preview()
        cat=a.resized(a.oracle_foreground,round(270*scale),round(157*scale),
                      ('intro-pixel-lumi',tuple(a.settings.get(k) for k in ('hat','buddy','accessory')),scale))
        a.images.append(cat);cv.create_image(ox+185*scale,oy+340*scale,image=cat)
        rect(315,302,99,105,fill='#514581',outline='#e2b884')
        text(365,319,'TAROT\nFOR A\nKINDER\nTOMORROW',12,w=87,color='#fff3de')
        for y,label,target,pink in [(473,'Start','oracle',True),(536,'Moon Diary','diary',False),
                                  (599,'Settings','settings',False)]:
            button(51,y,361,51,label,lambda target=target:go(target),pink=pink,
                   display='☆  Start' if label=='Start' else label)
        text(231,707,'Good things take time ♡',16)
    elif screen=='intention':
        heading('What is on your heart today?','Choose a topic or write your own.')
        from VeilAndVision import INTENTIONS
        icons=['♡','▣','$','⌂','♧','♧','☆','☾']
        for i,v in enumerate(INTENTIONS):
            x=28+(i%4)*103;y=164+(i//4)*130
            tile=button(x,y,98,114,v,lambda v=v:a.select_intention(v),v==a.intention,display=' ')
            box=(813+(i%4)*82,89+(i//4)*75,852+(i%4)*82,126+(i//4)*75)
            raw=tk.PhotoImage(width=39,height=37)
            raw.tk.call(str(raw),'copy',str(a.compact_source),'-from',*box,'-to',0,0)
            icon=a.resized(raw,round(49*scale),round(47*scale),('topic',i,scale))
            a.images.append(icon);tile.create_image(49*scale,34*scale,image=icon)
            tile.create_text(49*scale,85*scale,text=v.replace('A Big Decision','A Big\nDecision'),
                             font=font('tab',scale),fill=INK)
        def question():
            value=askstring('Your question','What is on your heart?',initialvalue=a.question.get(),parent=a.root)
            if value is not None:a.question.set(value[:500]);a.render()
        button(29,458,405,52,'Add a question',question,display='+  Add a question (optional)')
        preview=a.question.get()
        text(45,532,preview[:90]+('…' if len(preview)>90 else ''),15,w=370,anchor='nw')
        button(78,685,307,49,'Next',a.begin,pink=True,display='Next →')
    elif screen in ('draw','revealed'):
        heading('The Cards Are Waiting…' if night else 'Your Cards',
                'Take a deep breath. Pick three cards when you feel ready.' if night else 'A little guidance from your cards')
        draw_widgets=[]
        for i in range(3):
            x=28+i*139;y=185
            if night and i not in a.chosen:
                widget=button(x,y,128,196,'Choose '+str(i+1),lambda i=i:pick(i))
                img=back_image(round(128*scale),round(196*scale))
                a.images.append(img);widget.create_image(0,0,anchor='nw',image=img)
            else:
                c=a.reading['cards'][i]
                widget=card(c,x,y,128,224,lambda i=i:pick(i) if night else open_detail(i,'revealed'),
                     'Choose '+str(i+1) if night else 'Read '+c['name'])
                if night and getattr(a,'flipping_card',None)==i:
                    a.flipping_card=None;flip(widget,c)
            draw_widgets.append((widget,x,y))
            text(x+64,423,['Past','Present','Future'][i],17,w=128,bold=True,
                 color='#fff8f1' if night else INK)
            if not night:text(x+64,454,a.reading['cards'][i]['orientation'],13,w=130)
        if night:
            if getattr(a,'shuffle_pending',False):
                a.shuffle_pending=False
                def shuffle(frame=0):
                    for i,(widget,x,y) in enumerate(draw_widgets):
                        if not widget.winfo_exists():return
                        offset=math.sin(frame*math.pi/4+i)*15*(1-frame/20)
                        cv.coords(widget.window_item,ox+(x+offset)*scale,oy+y*scale)
                    if frame<20:a.typing_timers.append(a.root.after(24,lambda:shuffle(frame+1)))
                shuffle()
            lumi(550)
            text(231,492,f'{len(a.chosen)} of 3 chosen',17,color='#fff8f1')
        else:
            lumi(513)
            button(52,685,359,49,'View Reading',lambda:go('reading'),pink=True,display='View Reading →')
    elif screen=='meaning':
        c=a.reading['cards'][a.card_index]
        heading(c['name'],'Card Meaning')
        card(c,32,145,146,235)
        for i,t in enumerate(['Meaning','In This Position','For Your Question','Keywords']):
            button(193+(i%2)*119,151+(i//2)*46,113,38,t,lambda t=t:a.set_tab(t),a.meaning_tab==t,
                   display={'In This Position':'Position','For Your Question':'My Question'}.get(t,t))
        content={'Meaning':short_meaning(c),'In This Position':c['context'],
                 'For Your Question':c['guidance'],'Keywords':', '.join(c['keywords'])}[a.meaning_tab]
        text_box(192,242,234,122,content)
        def more():
            dialog=tk.Toplevel(a.root);dialog.title(c['name']);dialog.geometry('390x330')
            dialog.configure(bg=paper);dialog.transient(a.root)
            body=tk.Text(dialog,wrap='word',bg=paper,fg=INK,relief='flat',padx=20,pady=20,
                         font=font('body'),spacing1=LINE_SPACING,spacing3=LINE_SPACING)
            body.pack(fill='both',expand=True)
            question=a.reading.get('question','')
            body.insert('1.0',c['meaning']+'\n\n'+c['context']+'\n\n'+
                        (('Your question: '+question+'\n\n') if question else '')+c['guidance'])
            body.configure(state='disabled')
            tk.Button(dialog,text='Back ♡',command=dialog.destroy).pack(pady=10)
            dialog.bind('<Escape>',lambda e:dialog.destroy())
        button(225,374,170,36,'Read more',more)
        # Decorative character takes the space previously occupied by repeated copy.
        a.costume_preview()
        img=a.resized(a.oracle_foreground,round(270*scale),round(157*scale),
                      ('meaning-lumi',tuple(a.settings.get(k) for k in ('hat','buddy','accessory')),scale))
        a.images.append(img);cv.create_image(ox+231*scale,oy+540*scale,image=img)
        origin=getattr(a,'meaning_origin','revealed')
        button(81,685,301,49,'Back to Cards',lambda:go(origin),
               display='← Back to Reading' if origin=='reading' else '← Back to Cards')
    elif screen=='reading':
        heading('Your Reading')
        for i,c in enumerate(a.reading['cards']):
            y=125+i*105
            rect(25,y,413,98)
            icon_box={'The Moon':(808,521,837,551),'The Lovers':(808,474,837,501)}.get(c['name'],(808,575,837,603))
            art(icon_box,37,y+24,50,50)
            arrow='↓' if c['orientation']=='Reversed' else '↑'
            text(103,y+10,c['position']+' — '+c['name']+' '+arrow,15,w=323,anchor='nw',bold=True)
            text(103,y+35,short_meaning(c),14,w=323,anchor='nw')
            button(293,y+61,126,28,'Read more '+str(i+1),lambda i=i:open_detail(i,'reading'),display='Read more')
        rect(25,456,413,179)
        text(231,467,'Overall Message',17,bold=True)
        from VeilAndVision import overall
        text_box(36,496,391,126,overall(a.reading))
        saved=any(r['id']==a.reading['id'] for r in a.store.data['readings'])
        if saved:
            button(30,657,403,43,'Follow Up',lambda:go('followup'),pink=True,display='Revisit Your Step →')
            button(30,712,403,35,'Back to Diary',lambda:go('diary'),display='← Back to Diary')
        else:
            button(30,657,403,43,'Choose a Little Step',lambda:go('reflect'),pink=True,display='☆ Choose a Little Step →')
            button(30,712,403,35,'Save Reading Only',save)
    elif screen=='reflect':
        heading('One Little Step')
        for i,(v,symbol) in enumerate([('Listen to a favourite song','♫'),('Take a short pause','☕'),('Get some fresh air','♧')]):
            tile=button(30,169+i*100,403,80,v,lambda v=v:choose('step',v),a.reading.get('step')==v,display=' ')
            tile_art(tile,[(1191,473,1241,508),(1191,518,1241,553),(1191,564,1241,603)][i],17,15,53,43,('step',i))
            label_in(tile,89,40,v,17,width=265)
        button(30,492,403,49,'Add a note',lambda:edit('note','Add a note'),display='+ Note (optional)')
        button(30,659,403,49,'Save to Moon Diary',save,pink=True,display='Save to Moon Diary →')
        button(132,717,199,32,'Maybe later',save)
    elif screen=='save':
        art((125,779,197,849),36,85,83,83)
        text(290,105,'Saved to your\nMoon Diary ♡',23,w=290,bold=True)
        for i,c in enumerate(a.reading['cards']):card(c,28+i*74,246,66,126,show_name=False)
        rect(253,235,178,142,fill='#fff0f8')
        text(340,253,'My little step',14,w=155)
        text(340,286,a.reading.get('step') or 'Reading saved ♡',17,w=149)
        lumi(518)
        button(35,673,393,42,'Done for Now',lambda:go('intro'),pink=True)
        button(35,723,393,32,'View Diary',lambda:go('diary'))
    elif screen=='diary':
        heading('Moon Diary')
        entries=a.store.data['readings'];pages=max(1,(len(entries)+3)//4);a.page=min(a.page,pages-1)
        def load(entry):a.reading=dict(entry);a.note=entry.get('note','');go('reading')
        for i,r in enumerate(entries[a.page*4:a.page*4+4]):
            tile=button(29,150+i*114,405,98,'Entry '+r['id'],lambda r=r:load(r),display=' ')
            if r.get('cards'):
                thumb=tarot_image(a,r['cards'][0],round(48*scale),round(73*scale))
                a.images.append(thumb);tile.create_image(12*scale,12*scale,anchor='nw',image=thumb)
            label_in(tile,75,21,r['date'][:10]+'  ·  '+r['intention'],14)
            label_in(tile,75,57,short_meaning(r['cards'][1]),14,width=310)
        if not entries:text(231,272,'Your story starts here.\nSave a reading to begin. ♡',20)
        if pages>1:
            button(30,619,150,33,'Previous',lambda:a.diary_page(-1) if a.page else None)
            button(282,619,150,33,'More',lambda:a.diary_page(1) if a.page+1<pages else None)
        button(30,673,403,43,'New Reading',lambda:go('intention'),pink=True,display='+ New Reading')
        button(30,726,403,31,'Clear Diary',a.clear_diary)
    elif screen=='followup':
        heading('Revisit Your Step')
        rect(30,124,403,92)
        art((1191,473,1241,508),45,142,57,47)
        text(121,154,a.reading.get('step') or 'Your reading',17,w=287,anchor='nw')
        for i,v in enumerate(['Tried','Still working on it','Changed my mind']):
            button(30,340+i*67,403,52,v,lambda v=v:choose('followup_status',v),a.reading.get('followup_status')==v)
        text(35,542,'Reflection (optional)',14,anchor='nw')
        text_box(30,566,403,73,a.reading.get('reflection',''),editable=True,key='reflection')
        def followup():
            a.store.save(a.reading,a.reading.get('note',''))
            if a.sound and a.settings.get('sound'):a.sound.effect('save')
            go('diary')
        button(30,677,403,43,'Save Follow-up',followup,pink=True)
        button(103,730,257,30,'Back to Diary',lambda:go('diary'),display='← Back to Diary')
    elif screen=='settings':
        heading('Settings','Your familiar journey. Your little extra kindness. ♡')
        text(35,156,'Theme',19,anchor='nw',bold=True)
        for i,v in enumerate(['Day','Sunset','Night']):
            tile=button(30+i*137,192,129,90,v,lambda v=v:a.open_background(v),a.settings.get('selected_background')==v,display=' ')
            tile_art(tile,(1188+i*98,831,1267+i*98,865),10,10,109,47,('theme',v))
            label_in(tile,64,74,v,14,anchor='center')
        for i,(key,label) in enumerate([('music','Music'),('sound','Sound Effects')]):
            y=325+i*67
            rect(30,y,403,53)
            text(46,y+17,label,17,anchor='nw',w=235)
            button(335,y+9,82,35,key,lambda key=key:a.toggle(key),
                   display='● On' if a.settings.get(key) else '○ Off')
        text(36,474,'Text Size',17,anchor='nw')
        slider=tk.Scale(cv,from_=90,to=110,orient='horizontal',showvalue=False,
                        bg=paper,highlightthickness=0)
        slider.set(round(text_zoom*100));a.widgets.append(slider)
        def resize_text(event=None):
            a.store.settings(text_size=slider.get()/100)
            a.render()
        slider.bind('<ButtonRelease-1>',resize_text)
        slider.bind('<KeyRelease>',resize_text)
        cv.create_window(ox+180*scale,oy+465*scale,anchor='nw',window=slider,width=245*scale,height=39*scale)
        for y,label,fn in [(540,'About',a.about),(591,'Clear Diary',a.clear_diary),(642,'Reset',a.reset),
                            (703,'Back',lambda:go('intro'))]:
            button(30,y,403,40,label,fn,display='About Veil & Vision' if label=='About' else label)
    return True
