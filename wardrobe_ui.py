"""Reference-sized wardrobe interface with real, keyboard-accessible controls."""
import tkinter as tk
import tkinter.font as tkfont
from pathlib import Path
from wardrobe import OPTIONS, LABELS
from design_system import COLORS,GLASS_STATES,font as ui_font

class ReferenceButton(tk.Canvas):
    """Keyboard-operable button with consistent pastel colours on macOS."""
    def __init__(self,parent,width,height,label,command,color,font,icon=None,selected=False,pink=False,skin=None,backdrop=None):
        super().__init__(parent,width=width,height=height,bg='#fff1f8',bd=0,
                         highlightthickness=0,takefocus=True,cursor='hand2')
        self.command=command
        self.disabled=False
        if backdrop is not None and pink:
            self._glass(width,height,label,font,backdrop,selected)
            return
        self.base_color = '#efb3d3' if pink else ('#f6c3df' if selected else '#fff7fc')
        self.hover_color = '#f28bc8' if pink else ('#cbb2ff' if selected else '#f4e7ff')
        self.outline = '#D65AA0' if (selected or pink) else '#9a78df'
        radius=min(4,height/8)
        self.shape=self.create_polygon(1+radius,1,width-radius-1,1,width-1,1+radius,
            width-1,height-radius-1,width-radius-1,height-1,1+radius,height-1,
            1,height-radius-1,1,1+radius, smooth=False,
            fill=self.base_color,outline=self.outline,width=2)
        # The reference uses a pale top highlight and a darker lower bevel.
        top_color = '#ffd8e9' if pink else ('#ffe2ef' if selected else '#fffaff')
        bottom_color = '#efb3d3' if pink else ('#f4b0d4' if selected else '#e9e2ff')
        start=tuple(int(top_color[i:i+2],16) for i in (1,3,5))
        end=tuple(int(bottom_color[i:i+2],16) for i in (1,3,5))
        for row in range(4,max(4,height-3)):
            mix=(row-4)/max(1,height-8)
            shade='#'+''.join(f'{round(c+(d-c)*mix):02x}' for c,d in zip(start,end))
            self.create_line(3,row,width-4,row,fill=shade)
        # Fine inner highlight gives the buttons the soft beveled look in the
        # supplied mockup without relying on a baked screenshot crop.
        if height >= 24:
            self.create_line(7+radius/2,3,width-8-radius/2,3,
                             fill='#ffffff',width=1)
        if icon:
            self.create_image(width/2,5,anchor='n',image=icon)
            self.create_text(width/2,height-12,text=label,font=font,fill='#0809a4',anchor='center')
            if selected:
                r=max(7,round(width*.075)); x=width-r-6; y=r+6
                self.create_oval(x-r,y-r,x+r,y+r,fill='#aa7afa',outline='#8855dd')
                self.create_line(x-r*.55,y,x-r*.1,y+r*.4,x+r*.6,y-r*.45,
                                 fill='white',width=2)
        else:
            self.create_text(width/2,height/2,text=label,font=font,fill=COLORS['ink'],width=width-16,justify='center')
        if skin is not None:
            self.skin=skin
            self.create_image(0,0,anchor='nw',image=skin)
        def hover(event=None):
            if self.disabled:return
            self.itemconfigure(self.shape,fill=self.hover_color)
            self.delete('hover-border')
            self.create_rectangle(2,2,width-2,height-2,outline='#f19bd0',width=2,tags='hover-border')
        self.bind('<Enter>',hover)
        def clear_press(event=None):
            self.delete('pink-press')
            self.delete('hover-border')
            self.itemconfigure(self.shape,fill=self.base_color)
        def show_press(event=None):
            if self.disabled:return
            self.delete('pink-press')
            self.create_rectangle(2,2,width-2,height-2,fill='#ff7ba9',
                stipple='gray25',outline='#ff7ba9',width=2,tags='pink-press')
        self.bind('<Leave>',clear_press)
        self.bind('<ButtonPress-1>',show_press)
        def release(event):
            clear_press()
            if 0 <= event.x < width and 0 <= event.y < height:
                self.invoke()
        self.bind('<ButtonRelease-1>',release)
        self.bind('<Return>',lambda event:(self.invoke(),'break')[1])
        self.bind('<space>',lambda event:(self.invoke(),'break')[1])
        self.bind('<FocusIn>',lambda event:self.configure(highlightthickness=2,highlightbackground='#6843d5'))
        self.bind('<FocusOut>',lambda event:self.configure(highlightthickness=0))
        def set_disabled(value):
            self.disabled=bool(value)
            self.delete('disabled-overlay')
            self.configure(takefocus=not self.disabled,cursor='arrow' if self.disabled else 'hand2')
            if self.disabled:
                self.create_rectangle(1,1,width-1,height-1,fill='#e5ddec',stipple='gray50',
                                      outline='#c6b7d2',tags='disabled-overlay')
        self.set_disabled=set_disabled

    def invoke(self):
        if getattr(self,'disabled',False):return
        return self.command()

    def _glass(self,width,height,label,font,backdrop,selected):
        """Alpha-composite pink over the actual artwork beneath this button."""
        self.disabled=False
        self.glass_images={}
        # Compute raster colours in Python once, then upload rows in one Tk call.
        pixels=[[backdrop.get(x,y) for x in range(width)] for y in range(height)]
        def paint(state):
            if self.disabled:state='disabled'
            if state not in self.glass_images:
                rgb,alpha=GLASS_STATES[state]
                image=tk.PhotoImage(width=width,height=height)
                rows=[]
                for y,row in enumerate(pixels):
                    colors=[]
                    for x,bg in enumerate(row):
                        inset=5 if y<3 or y>=height-3 else 3 if y<5 or y>=height-5 else 1
                        inside=inset<=x<width-inset and 1<=y<height-1
                        blend=tuple(round(c*(1-alpha)+t*alpha) for c,t in zip(bg,rgb)) if inside else bg
                        colors.append('#%02x%02x%02x'%blend)
                    rows.append('{'+ ' '.join(colors)+'}')
                image.put(' '.join(rows));self.glass_images[state]=image
            self.delete('all')
            self.create_image(0,0,anchor='nw',image=self.glass_images[state])
            offset=-1 if state=='hover' else 1 if state=='pressed' else 0
            edge='#b56aa5' if state=='disabled' else '#D65AA0'
            self.create_polygon(6,2+offset,width-6,2+offset,width-2,6+offset,
                width-2,height-6+offset,width-6,height-2+offset,6,height-2+offset,
                2,height-6+offset,2,6+offset,fill='',outline=edge,width=1)
            self.create_line(8,4+offset,width-8,4+offset,fill='#ffeaf6')
            self.create_text(width/2,height/2+offset,text=label,font=font,
                             fill='#9890af' if state=='disabled' else '#3F3A8A',width=width-24,justify='center')
            if selected:self.create_text(width-13,11,text='✓',fill='#873d91',font=font)
        idle='selected' if selected else 'normal'
        paint(idle)
        self.bind('<Enter>',lambda e:paint('hover'))
        self.bind('<Leave>',lambda e:paint(idle))
        self.bind('<ButtonPress-1>',lambda e:paint('pressed'))
        def release(e):
            paint(idle)
            if 0<=e.x<width and 0<=e.y<height:self.invoke()
        self.bind('<ButtonRelease-1>',release)
        self.bind('<KeyPress-space>',lambda e:paint('pressed'))
        self.bind('<KeyRelease-space>',lambda e:(paint(idle),self.invoke(),'break')[-1])
        self.bind('<Return>',lambda e:(self.invoke(),'break')[-1])
        self.bind('<FocusIn>',lambda e:paint('hover'))
        self.bind('<FocusOut>',lambda e:paint(idle))
        def set_disabled(value):
            self.disabled=bool(value)
            self.configure(takefocus=not self.disabled,cursor='arrow' if self.disabled else 'hand2')
            paint(idle)
        self.set_disabled=set_disabled


def draw(app):
    # Reference panel is 463 x 778; fit it to the app's current preview height.
    viewport=getattr(app,'desktop_viewport',None)
    if viewport:
        width,height=viewport
        scale=min(width/463,height/778)
        content_width,content_height=round(463*scale),round(778*scale)
        offset_x,offset_y=(width-content_width)//2,(height-content_height)//2
    else:
        available=min(app.root.winfo_screenheight()-140,app.root.maxsize()[1]-60)
        scale=min(466*app.scale/778,available/778)
        width,height=round(463*scale),round(778*scale)
        content_width,content_height=width,height
        offset_x=offset_y=0
    app.canvas.delete('all')
    app.canvas.configure(width=width,height=height)
    app.rendered_size=(width,height)
    if not viewport:
        app.root.geometry(f'{width}x{height}')
    app.hits=[]
    app.controls={}
    if not hasattr(app,'wardrobe_source'):
        app.wardrobe_source=tk.PhotoImage(file=str(Path(__file__).with_name('wardrobe_reference.png')))
    if 'wardrobe-frame' not in app.cache:
        frame=tk.PhotoImage(width=463,height=778)
        frame.tk.call(str(frame),'copy',str(app.wardrobe_source),'-from',50,122,513,900,'-to',0,0)
        app.cache['wardrobe-frame']=frame
    frame=app.resized(app.cache['wardrobe-frame'],content_width,content_height,('wardrobe-ui-frame',scale))
    app.images.append(frame)
    app.canvas.create_image(offset_x,offset_y,anchor='nw',image=frame)
    families=tkfont.families(app.root)
    # Use the same rounded family chosen by the main application so generated
    # labels and controls stay visually consistent with the rest of the flow.
    family=app.font_family

    def rectangle(box,color):
        x1,y1,x2,y2=box
        app.canvas.create_rectangle(offset_x+x1*scale,offset_y+y1*scale,
            offset_x+x2*scale,offset_y+y2*scale,fill=color,outline='')

    def text(x,y,value,size=14,bold=False):
        app.canvas.create_text(offset_x+x*scale,offset_y+y*scale,text=value,fill='#10149a',
            font=ui_font(size,scale,bold),anchor='center')

    rectangle((61,7,338,39),'#b5b2f6')
    app.canvas.create_text(offset_x+63*scale,offset_y+23*scale,text='Veil & Vision',anchor='w',
        fill=COLORS['ink'],font=ui_font('titlebar',scale))
    rectangle((73,50,398,117),'#fff3f4')
    text(231,72,'Create Your Oracle',23,True)
    text(231,102,'Customise your little guide!',15)

    def button(box,label,action,caption=None,icon=None,selected=False,pink=False,source_box=None):
        left,top,right,bottom=box
        skin=None
        if source_box:
            cache_key=('reference-control',source_box,round((right-left)*scale),round((bottom-top)*scale))
            if cache_key not in app.cache:
                raw=tk.PhotoImage(width=source_box[2]-source_box[0],height=source_box[3]-source_box[1])
                raw.tk.call(str(raw),'copy',str(app.wardrobe_source),'-from',*source_box,'-to',0,0)
                app.cache[cache_key]=app.resized(raw,cache_key[2],cache_key[3],cache_key+('scaled',))
            skin=app.cache[cache_key]
        backdrop=None
        if pink:
            backdrop=tk.PhotoImage(width=round((right-left)*scale),height=round((bottom-top)*scale))
            backdrop.tk.call(str(backdrop),'copy',str(frame),'-from',round(left*scale),round(top*scale),
                round(left*scale)+backdrop.width(),round(top*scale)+backdrop.height(),'-to',0,0)
            # The reference's Next crop contains baked lettering: use the clean
            # floral panel for the button region before alpha compositing.
            source=tk.PhotoImage(file=str(Path(__file__).with_name('floral_panel.png')))
            clean=app.resized(source,content_width,content_height,('glass-wardrobe-bg',scale))
            backdrop.tk.call(str(backdrop),'copy',str(clean),'-from',round(left*scale),round(top*scale),
                round(left*scale)+backdrop.width(),round(top*scale)+backdrop.height(),'-to',0,0)
        color='#d8caff' if selected else '#ef83c5' if pink else '#fff6fa'
        b=ReferenceButton(app.canvas,round((right-left)*scale),round((bottom-top)*scale),
            caption if caption is not None else label,lambda:app.run_action(action),color,
            ui_font('button' if pink else 'tab',scale,pink),icon,selected,pink,skin,backdrop)
        app.canvas.create_window(offset_x+left*scale,offset_y+top*scale,anchor='nw',window=b,
            width=(right-left)*scale,height=(bottom-top)*scale)
        app.widgets.append(b); app.controls[label]=b
        # Each widget owns its mouse and keyboard events. Old reference-space
        # hit areas would be displaced when the portrait panel is centred.
        return b

    # Clear the original baked-in model and replace it with the user's own cat.
    preview=app.wardrobe_background(app.settings.get('selected_background','Day'),round(376*scale),round(202*scale))
    foreground=app.resized(app.oracle_foreground,round(222*202/129*scale),round(202*scale),
        ('wardrobe-model-ui',tuple(app.settings.get(k) for k in ('hat','accessory','buddy')),scale))
    app.paste_layer(preview,foreground,(preview.width()-foreground.width())//2,0)
    app.images.append(preview)
    app.canvas.create_image(offset_x+45*scale,offset_y+120*scale,anchor='nw',image=preview)
    button((28,210,49,259),'Previous style',lambda:app.cycle_style(-1),'◀',source_box=(78,332,99,381))
    button((414,210,435,259),'Next style',lambda:app.cycle_style(1),'▶',source_box=(464,332,485,381))
    for category,left,right in [('Hats',24,119),('Buddies',125,220),('Accessories',226,323),('Backgrounds',330,439)]:
        # Use the reference lettering and bevel artwork, with the active tab
        # taken from the corresponding panel in the supplied design.
        active=app.category==category
        crops={
            'Hats': (74,459,170,501) if active else (561,459,657,501),
            'Buddies': (661,459,759,501) if active else (175,459,271,501),
            'Accessories': (1245,459,1354,501) if active else (276,459,379,501),
            'Backgrounds': (384,459,494,501),
        }
        b=button((left,337,right,379),category,lambda c=category:app.set_category(c),
               selected=active)
        if active and category=='Backgrounds':
            b.create_rectangle(2,2,round((right-left)*scale)-2,round(42*scale)-2,
                               outline='#9164df',width=2)
    # Larger 3 x 2 tiles follow the reference, with a separate browsing strip.
    rectangle((23,391,441,648),'#fff1f8')
    key,choices=OPTIONS[app.category]
    page=getattr(app,'wardrobe_pages',{}).get(app.category,0)
    for i,choice in enumerate(choices[page*6:page*6+6]):
        left=26+(i%3)*141; top=396+(i//3)*117
        selected=app.settings.get(key)==choice
        if app.category=='Backgrounds':
            icon=app.wardrobe_background(choice,round(89*scale),round(62*scale))
        elif choice=='None':
            # Cat ears / empty companion / empty collar icon from the reference.
            box={'Hats':(380,650,469,725),'Buddies':(883,651,938,718),
                 'Accessories':(1358,655,1441,716)}[app.category]
            raw=tk.PhotoImage(width=box[2]-box[0],height=box[3]-box[1])
            raw.tk.call(str(raw),'copy',str(app.wardrobe_source),'-from',*box,'-to',0,0)
            icon=app.resized(raw,round(62*scale),round(51*scale),('none-ui',app.category,scale))
        else:
            icon=app.wardrobe_sprite(app.category,choice,round(89*scale),round(70*scale))
        app.images.append(icon)
        label=LABELS.get(choice,choice)
        if choice=='None': label={'Hats':'No Hat','Buddies':'No Buddy','Accessories':'No Accessory'}[app.category]
        if choice=='Frog' and app.category=='Hats': label='Frog Hat'
        button((left,top,left+129,top+107),choice,lambda k=key,v=choice:app.change(**{k:v}),
               caption=label,icon=icon,selected=selected)
    count=(len(choices)+5)//6
    if count>1:
        button((28,627,124,650),'‹ Previous',lambda:app.wardrobe_page(-1))
        text(232,639,f'{page+1} / {count}',13)
        button((340,627,436,650),'More ›',lambda:app.wardrobe_page(1))
    # Recreate name text at reference sizes without baking the current name in.
    rectangle((36,655,432,701),'#fff2f8')
    text(231,667,'This is '+app.settings.get('name','Lumi')+'! ♡',20,True)
    text(231,690,'Your companion on this journey. ♡',14)
    button((85,713,377,763),'Choose intention',lambda:app.go('intention'),'Next →',pink=True,
           source_box=(135,835,427,885))
    button((349,9,376,37),'Minimize',app.minimize,'−',source_box=(399,131,426,159))
    button((382,9,409,37),'Change zoom',lambda:app.zoom(-.5 if app.scale>=2 else .5),'□',
           source_box=(432,131,459,159))
    button((416,9,443,37),'Close app',app.close,'×',pink=True,source_box=(466,131,493,159))
    app.hit((329,22,346,45),'Navigation menu',app.popup_menu)
    rectangle((243,7,343,39),'#b5b2f6')
    button((247,10,291,38),'Back',app.back,'‹')
    button((297,10,340,38),'Home',lambda:app.go('intro'),'⌂')
