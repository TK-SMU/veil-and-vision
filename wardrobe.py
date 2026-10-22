"""Lumi's wardrobe. Tk-only layered sprites and independent saved selections."""
from pathlib import Path
import tkinter as tk

OPTIONS = {
    'Hats': ('hat', ['Star', 'Flowers', 'Sleepy', 'Frog', 'Sun', 'None', 'Beret', 'Pumpkin', 'Crown']),
    'Buddies': ('buddy', ['Bunny', 'Frog', 'Chick', 'Butterfly', 'Cloud', 'None', 'Fox', 'Owl', 'Turtle']),
    'Accessories': ('accessory', ['Bow', 'Crystal', 'Scarf', 'Pin', 'Clip', 'None', 'Pendant', 'MintBow', 'Wings']),
    'Backgrounds': ('selected_background', ['Day', 'Sunset', 'Night']),
}
LABELS = {'Star':'Star Witch', 'Flowers':'Flower Crown', 'Sleepy':'Sleepy Cap',
          'Sun':'Sun Hat', 'Bow':'Pink Bow', 'Crystal':'Heart Charm',
          'Scarf':'Moon Scarf', 'Pin':'Star Pin', 'Clip':'Flower Clip',
          'Beret':'Moon Beret', 'Pumpkin':'Pumpkin Hat', 'Crown':'Heart Crown',
          'Pendant':'Moon Charm', 'MintBow':'Mint Bow', 'Wings':'Angel Wings'}
EXTRA_CELLS = {'Beret':(0,0), 'Pumpkin':(1,0), 'Crown':(2,0),
               'Fox':(0,1), 'Owl':(1,1), 'Turtle':(2,1),
               'Pendant':(0,2), 'MintBow':(1,2), 'Wings':(2,2)}
# Sprite bounds in the supplied wardrobe design, excluding labels and borders.
SPRITES = {
 'Hats': [(95,533,187,600),(235,533,330,599),(383,528,467,602),
          (96,650,184,725),(224,650,342,724),None],
 'Buddies': [(590,530,663,602),(730,535,808,602),(869,535,945,602),
             (593,650,664,725),(727,651,806,725),None],
 'Accessories': [(1077,535,1157,602),(1217,536,1295,602),(1356,531,1448,610),
                 (1077,648,1158,719),(1225,655,1290,723),None],
}

class WardrobeMixin:
    def wardrobe_sprite(self, category, choice, width, height):
        if choice in EXTRA_CELLS:
            return self.extra_sprite(choice,width,height)
        index=OPTIONS[category][1].index(choice)
        box=SPRITES[category][index]
        if box is None:
            return None
        key=('wardrobe-sprite',category,choice)
        if key not in self.cache:
            if not hasattr(self,'wardrobe_source'):
                self.wardrobe_source=tk.PhotoImage(file=str(Path(__file__).with_name('wardrobe_reference.png')))
            x1,y1,x2,y2=box
            sprite=tk.PhotoImage(width=x2-x1,height=y2-y1)
            sprite.tk.call(str(sprite),'copy',str(self.wardrobe_source),'-from',*box,'-to',0,0)
            w,h=sprite.width(),sprite.height()
            pending=[(x,y) for x in range(w) for y in (0,h-1)]
            pending += [(x,y) for y in range(h) for x in (0,w-1)]
            visited=set()
            while pending:
                x,y=pending.pop()
                if (x,y) in visited or not (0<=x<w and 0<=y<h): continue
                visited.add((x,y))
                r,g,b=sprite.get(x,y)
                if r>175 and g>150 and b>170:
                    sprite.transparency_set(x,y,True)
                    pending.extend(((x-1,y),(x+1,y),(x,y-1),(x,y+1)))
            if category=='Buddies' and choice=='Cloud':
                # Pale gaps in the cloud outline let edge flood-fill erase its
                # white body. Restore the ORIGINAL pixels between each row's
                # outer outline points; leave the outside fully transparent.
                for yy in range(h):
                    edges=[xx for xx in range(w) if not sprite.transparency_get(xx,yy)]
                    if len(edges)<2:continue
                    for xx in range(min(edges),max(edges)+1):
                        sprite.transparency_set(xx,yy,False)
            self.cache[key]=self.trim_sprite(sprite)
        source=self.cache[key]
        ratio=min(width/source.width(),height/source.height())
        return self.resized(source,max(1,int(source.width()*ratio)),max(1,int(source.height()*ratio)),key)

    def trim_sprite(self,sprite):
        """Fit clothing to its visible outline rather than a padded tile."""
        pixels=[(x,y) for y in range(sprite.height()) for x in range(sprite.width())
                if not sprite.transparency_get(x,y)]
        if not pixels: return sprite
        remaining=set(pixels); components=[]
        while remaining:
            part=set(); stack=[remaining.pop()]
            while stack:
                x,y=stack.pop(); part.add((x,y))
                for point in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                    if point in remaining:
                        remaining.remove(point); stack.append(point)
            components.append(part)
        minimum=max(4,max(map(len,components))//20)
        keep=set().union(*(c for c in components if len(c)>=minimum))
        for x,y in set(pixels)-keep: sprite.transparency_set(x,y,True)
        pixels=keep
        left=min(x for x,y in pixels); right=max(x for x,y in pixels)+1
        top=min(y for x,y in pixels); bottom=max(y for x,y in pixels)+1
        trimmed=tk.PhotoImage(width=right-left,height=bottom-top)
        trimmed.tk.call(str(trimmed),'copy',str(sprite),'-from',left,top,right,bottom,'-to',0,0)
        return trimmed

    def wardrobe_background(self,theme,width=222,height=129):
        """Cover-fit a pixel-art scene with nearest-neighbour scaling."""
        theme=theme if theme in ('Day','Sunset','Night') else 'Day'
        key=('wardrobe-scenery',theme)
        if key not in self.cache:
            if not hasattr(self,'scenery_source'):
                self.scenery_source=tk.PhotoImage(file=str(Path(__file__).with_name('wardrobe_backgrounds_pixel.png')))
            source=self.scenery_source
            row=('Day','Sunset','Night').index(theme)
            top=row*source.height()//3; bottom=(row+1)*source.height()//3
            scene=tk.PhotoImage(width=source.width(),height=bottom-top)
            scene.tk.call(str(scene),'copy',str(source),'-from',0,top,source.width(),bottom,'-to',0,0)
            self.cache[key]=scene
        source=self.cache[key]
        # Center-crop to the requested viewport, then use nearest-neighbour.
        # No stretched clouds, hills, or moon in the preview or option tiles.
        crop_key=(key,'aspect',width,height)
        if crop_key not in self.cache:
            sw,sh=source.width(),source.height()
            if sw/sh>width/height:
                cw,ch=round(sh*width/height),sh
            else:
                cw,ch=sw,round(sw*height/width)
            left,top=(sw-cw)//2,(sh-ch)//2
            if theme=='Night': left=round((sw-cw)*.30)
            crop=tk.PhotoImage(width=cw,height=ch)
            crop.tk.call(str(crop),'copy',str(source),'-from',left,top,left+cw,top+ch,'-to',0,0)
            self.cache[crop_key]=crop
        return self.resized(self.cache[crop_key],width,height,crop_key).copy()

    def extra_sprite(self,choice,width,height):
        """Read a cell from the transparent expansion sheet and trim margins."""
        key=('wardrobe-extra',choice)
        if key not in self.cache:
            if not hasattr(self,'extra_source'):
                self.extra_source=tk.PhotoImage(file=str(Path(__file__).with_name('wardrobe_extra.png')))
            source=self.extra_source
            col,row=EXTRA_CELLS[choice]
            left,right=col*source.width()//3,(col+1)*source.width()//3
            top,bottom=row*source.height()//3,(row+1)*source.height()//3
            # The fox tail and left wing extend slightly beyond nominal cells.
            if choice=='Fox': right=source.width()*35//100
            if choice=='Owl': left=source.width()*36//100
            if choice=='Wings': left=source.width()*64//100
            pixels={(x,y) for y in range(top,bottom) for x in range(left,right)
                    if not source.transparency_get(x,y)}
            if not pixels: raise ValueError('Missing wardrobe sprite: '+choice)
            # Ignore isolated generator specks while retaining disconnected
            # meaningful pieces such as both wings and a hanging pendant.
            pending=set(pixels)
            components=[]
            while pending:
                component=set()
                stack=[pending.pop()]
                while stack:
                    x,y=stack.pop()
                    component.add((x,y))
                    for point in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                        if point in pending:
                            pending.remove(point)
                            stack.append(point)
                components.append(component)
            minimum=max(20,max(map(len,components))//20)
            pixels=set().union(*(c for c in components if len(c)>=minimum))
            x1=min(x for x,y in pixels); x2=max(x for x,y in pixels)+1
            y1=min(y for x,y in pixels); y2=max(y for x,y in pixels)+1
            sprite=tk.PhotoImage(width=x2-x1,height=y2-y1)
            sprite.tk.call(str(sprite),'copy',str(source),'-from',x1,y1,x2,y2,'-to',0,0)
            for y in range(y1,y2):
                for x in range(x1,x2):
                    if (x,y) not in pixels: sprite.transparency_set(x-x1,y-y1,True)
            self.cache[key]=sprite
        source=self.cache[key]
        ratio=min(width/source.width(),height/source.height())
        return self.resized(source,max(1,int(source.width()*ratio)),max(1,int(source.height()*ratio)),key)

    def wardrobe_page(self,step):
        pages=getattr(self,'wardrobe_pages',{})
        count=(len(OPTIONS[self.category][1])+5)//6
        pages[self.category]=(pages.get(self.category,0)+step)%count
        self.wardrobe_pages=pages
        self.render()

    def show_oracle(self):
        for category,left,right in [('Hats',330,386),('Buddies',386,452),('Accessories',452,528),('Backgrounds',528,603)]:
            self.hit((left,256,right,287),category,lambda c=category:self.set_category(c))
        self.rect((331,292,602,392),'#fff0f8')
        self.wardrobe_tiles=[]
        key,choices=OPTIONS[self.category]
        page=getattr(self,'wardrobe_pages',{}).get(self.category,0)
        self.wardrobe_page_count=(len(choices)+5)//6
        for i,choice in enumerate(choices[page*6:page*6+6]):
            x=335+(i%3)*88
            y=295+(i//3)*40
            self.wardrobe_tiles.append(((x,y,x+84,y+38),key,choice))
            self.hit((x,y,x+84,y+38),choice,lambda k=key,v=choice:self.change(**{k:v}))
        if self.wardrobe_page_count>1:
            self.text(467,383,f'{page+1} / {self.wardrobe_page_count}',9,65,'center')
        self.hit((353,174,382,217),'Previous style',lambda:self.cycle_style(-1))
        self.hit((551,174,581,217),'Next style',lambda:self.cycle_style(1))
        self.hit((379,438,552,474),'Choose intention',lambda:self.go('intention'))
        self.costume_preview()
        if self.settings.get('name','Lumi')!='Lumi':
            self.rect((350,400,580,414),'#fff0f8')
            self.text(465,409,'This is '+self.settings['name']+'!',11,230,'center')
        self.hit((341,394,590,436),'Rename your oracle',self.rename)

    def install_controls(self):
        if self.screen=='oracle':
            from wardrobe_ui import draw
            draw(self)
            return
        hits=self.hits
        if self.screen=='oracle':
            self.hits=[hit for hit in hits if not (293<=hit[0][1]<392)]
        try:
            self.legacy_install_controls()
        finally:
            self.hits=hits
        if self.screen!='oracle': return
        for box,key,choice in self.wardrobe_tiles:
            selected=self.settings.get(key)==choice
            if self.category=='Backgrounds':
                icon=self.wardrobe_background(choice,39,23)
            else:
                icon=self.wardrobe_sprite(self.category,choice,39,22)
            if icon:
                icon=self.resized(icon,round(icon.width()*self.scale),round(icon.height()*self.scale),('wardrobe-button',self.category,choice,self.scale))
                self.images.append(icon)
            label=LABELS.get(choice,choice)
            if choice=='Frog' and self.category=='Hats': label='Frog Hat'
            label=('✓ ' if selected else '')+label
            button=tk.Button(self.canvas,text=label,image=icon or '',compound='top',
                command=lambda k=key,v=choice:self.run_action(lambda:self.change(**{k:v})),
                bg='#d7c7ff' if selected else '#fff7fc',fg='#10149a',
                activebackground='#e4d5ff',relief='solid',bd=1,highlightthickness=0,
                font=(self.font_family,-round(9*self.scale)),cursor='hand2',takefocus=True)
            button.bind('<Return>',lambda event,b=button:(b.invoke(),'break')[1])
            x,y=self.xy(box[0],box[1])
            self.canvas.create_window(x,y,anchor='nw',window=button,width=84*self.scale,height=38*self.scale)
            self.widgets.append(button)
            self.controls[choice]=button
        if self.wardrobe_page_count>1:
            for label,left,step in [('‹ Previous',337,-1),('More ›',512,1)]:
                button=tk.Button(self.canvas,text=label,command=lambda s=step:self.wardrobe_page(s),
                    font=(self.font_family,-round(9*self.scale)),bg='#e8dcff',fg='#10149a',
                    relief='flat',bd=0,cursor='hand2')
                button.bind('<Return>',lambda event,b=button:(b.invoke(),'break')[1])
                x,y=self.xy(left,375)
                self.canvas.create_window(x,y,anchor='nw',window=button,width=82*self.scale,height=16*self.scale)
                self.widgets.append(button)
                self.controls[label]=button

    def cycle_style(self,step):
        key,choices=OPTIONS[self.category]
        choices=choices[:6]
        current=self.settings.get(key)
        index=choices.index(current) if current in choices else 0
        index=(index+step)%len(choices)
        pages=getattr(self,'wardrobe_pages',{})
        pages[self.category]=index//6
        self.wardrobe_pages=pages
        self.change(**{key:choices[index]})

    def costume_preview(self):
        # Retain the existing base cat and proven witch-hat fit. Add new
        # independent layers after composing a clean background and cat.
        settings=self.settings
        saved={k:settings.get(k) for k in ('hat','buddy','accessory')}
        hat=saved['hat']
        settings.update(hat=hat if hat in ('Star','Moon','Rose','Ice') else 'None',buddy='None',accessory='None')
        try:
            self.legacy_costume_preview()
        finally:
            settings.update(saved)
        scene=tk.PhotoImage(width=222,height=129)
        if saved['accessory']=='Wings':
            # Put wings behind the body, leaving the cat's face and paws clear.
            self.paste_layer(scene,self.extra_sprite('Wings',135,65),36,56)
        self.paste_layer(scene,self.cat_layer(),40,23)
        if hat == 'Star':
            self.paste_layer(scene,self.wardrobe_sprite('Hats','Star',92,67),60,1)
        elif hat in ('Moon','Rose','Ice'):
            self.paste_layer(scene,self.cache[('fitted-hat',hat)],60,1)
        if hat in ('Flowers','Sleepy','Frog','Sun','Beret','Pumpkin','Crown'):
            # Center visible artwork on the head, and align its lower edge
            # with the forehead. Padded source rectangles must not affect fit.
            size,baseline={'Flowers':((75,28),54), 'Sleepy':((90,57),58),
                           'Frog':((87,51),59), 'Sun':((105,57),61),
                           'Beret':((88,53),58), 'Pumpkin':((88,57),59),
                           'Crown':((54,40),53)}[hat]
            sprite=self.wardrobe_sprite('Hats',hat,*size)
            self.paste_layer(scene,sprite,106-sprite.width()//2,baseline-sprite.height())
        accessory=saved['accessory']
        accessory={'Flowers':'Clip'}.get(accessory,accessory)
        if accessory in OPTIONS['Accessories'][1] and accessory not in ('None','Wings'):
            size,center,top={'Bow':((30,22),110,96), 'Crystal':((29,23),110,95),
                            'Scarf':((35,25),110,94), 'Pin':((18,17),117,100),
                            'Clip':((16,18),138,48), 'Pendant':((29,24),110,95),
                            'MintBow':((30,22),110,96)}[accessory]
            sprite=self.wardrobe_sprite('Accessories',accessory,*size)
            self.paste_layer(scene,sprite,center-sprite.width()//2,top)
        buddy=saved['buddy']
        if buddy in OPTIONS['Buddies'][1] and buddy!='None':
            size=(32,37) if buddy=='Bunny' else (33,30)
            sprite=self.wardrobe_sprite('Buddies',buddy,*size)
            self.paste_layer(scene,sprite,12,129-sprite.height()-3)
        # Legacy 'Cat' means Lumi alone, not a second scenery crop.
        # Only the explicit Buddy choices add a transparent companion.
        self.oracle_foreground=scene
        background=self.wardrobe_background(self.settings.get('selected_background','Day'))
        self.paste_layer(background,scene,0,0)
        self.oracle_scene=background
        self.put_sticker(background,356,120)
