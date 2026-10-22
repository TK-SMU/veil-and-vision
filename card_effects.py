"""Gentle effects on one live Canvas image per tarot card."""
import tkinter as tk
import math
from sound_events import play


def separate_cards(app, panel, boxes, fit):
    """Lift painted cards out of the panel without leaving duplicate cards.

    The original pixels become the card items. Only pixels behind those items
    are filled from the adjacent scenery for the brief lift/flip exposure.
    """
    key=('card-cutouts',str(panel),tuple(boxes),fit)
    if key in app.cache:
        return app.cache[key]
    background=panel.copy()
    pictures=[]
    for x,y,r,b in boxes:
        x,y,r,b=[round(v*fit) for v in (x,y,r,b)]
        photo=tk.PhotoImage(width=r-x,height=b-y)
        photo.tk.call(str(photo),'copy',str(panel),'-from',x,y,r,b,'-to',0,0)
        pictures.append(photo)
        # One adjacent scenery column fills the hidden footprint. At rest the
        # original card covers it exactly; the rest of the panel is untouched.
        # Sample scenery beyond the printed border, not its dark edge. The
        # shared 2:3 deck leaves narrow transparent margins in older card boxes.
        pad=max(2,round(7*fit))
        left,right=max(0,x-pad),min(panel.width(),r+pad)
        top,bottom=max(0,y-round(fit)),min(panel.height(),b+round(fit))
        sample=max(0,x-round(9*fit))
        if app.screen=='revealed':
            color='#fff8f2'
            background.put(color,to=(left,top,right,bottom))
        else:
            background.tk.call(str(background),'copy',str(panel),'-from',
                               sample,top,sample+1,bottom,'-to',left,top,
                               '-zoom',right-left,1)
    app.cache[key]=(background,pictures)
    return background,pictures


class CardEffect:
    def __init__(self,app,index,box,image,front=None,revealed=False):
        self.app=app;self.canvas=app.canvas;self.index=index
        self.box=box;self.image=image;self.front=front
        self.revealed=revealed;self.busy=False;self.alive=True
        self.jobs=set();self.frames=[];self.dy=0
        self.hovered=False;self.float_job=None;self.float_phase=index*1.8
        self.tag=f'card-effect-{index}'
        x,y,r,b=box
        self.glow=self.canvas.create_rectangle(x-2,y-2,r+2,b+2,outline='',width=3)
        self.item=self.canvas.create_image(x,y,anchor='nw',image=image,tags=(self.tag,))
        self.hit=self.canvas.create_rectangle(x,y,r,b,fill='',outline='',width=0,tags=('invisible-card-hit',))
        self.canvas.tag_bind(self.hit,'<Enter>',lambda e:self.hover(True))
        self.canvas.tag_bind(self.hit,'<Leave>',lambda e:self.hover(False))
        self.canvas.tag_bind(self.hit,'<Button-1>',lambda e:self.press())
        if app.screen=='draw' and not revealed:self.float_job=app.root.after(40,self.float_tick)

    def later(self,delay,fn):
        def run():
            self.jobs.discard(job)
            if self.alive: fn()
        job=self.app.root.after(delay,run);self.jobs.add(job)

    def stop_float(self):
        if self.float_job is not None:
            self.app.root.after_cancel(self.float_job)
            self.float_job=None

    def float_tick(self):
        """A slow sine wave, eased back after hover; all coordinates move together."""
        self.float_job=None
        if not self.alive or self.busy or self.revealed or self.app.screen!='draw':return
        if self.hovered:
            # Five 40ms ticks approach the 7px lift gently.
            target=-7
        else:
            period=(2400,2100,1900)[self.index]
            self.float_phase += 2*math.pi*40/period
            target=(4 if self.index==1 else 3.5)*math.sin(self.float_phase)
        self.offset(self.dy+(target-self.dy)*.5)
        self.float_job=self.app.root.after(40,self.float_tick)

    def dispose(self):
        self.alive=False
        self.stop_float()
        for job in self.jobs:
            self.app.root.after_cancel(job)
        self.jobs.clear()

    def offset(self,dy):
        self.canvas.move(self.tag,0,dy-self.dy)
        self.dy=dy
        x,y,r,b=self.box
        self.canvas.coords(self.hit,x,y+dy,r,b+dy)
        self.canvas.coords(self.glow,x-2,y+dy-2,r+2,b+dy+2)

    def hover(self,on):
        if self.busy or not self.alive:return
        if self.app.screen=='draw' and self.revealed:return
        self.hovered=on
        if self.app.screen!='draw':self.offset(-2 if on else 0)
        # On leave the next floating ticks gently return to the wave.
        self.canvas.itemconfigure(self.glow,outline='#dcc7f5' if on else '')

    def press(self):
        if self.busy or not self.alive or getattr(self.app,'card_animating',False):return
        if self.app.screen=='draw' and self.revealed:return
        self.stop_float()
        self.busy=True;self.app.card_animating=True
        play(self.app,'select_crystal' if self.app.screen=='draw' else 'ui_click')
        self.canvas.itemconfigure(self.glow,outline='#e6acd1')
        if self.app.screen=='revealed':
            self.later(90,lambda:self.app.open_card(self.index))
        else:
            self.lift_to_flip()

    def tween(self,target,duration,done):
        start=self.dy
        steps=6
        def step(n):
            fraction=n/steps
            eased=fraction*fraction*(3-2*fraction)
            self.offset(start+(target-start)*eased)
            if n<steps:self.later(duration//steps,lambda:step(n+1))
            else:done()
        self.later(duration//steps,lambda:step(1))

    def lift_to_flip(self):
        self.tween(-5,120,self.flip)

    def settle(self):
        play(self.app,'card_reveal')
        self.tween(0,150,lambda:self.app.pick(self.index))

    @staticmethod
    def narrowed(photo,width):
        # Resample only the animated image in memory; no blocking sleeps or
        # repeated per-pixel Tk calls, and no permanent size change.
        raw=photo.tk.call(str(photo),'data','-format','ppm').split(b'\n',3)[3]
        sw,sh=photo.width(),photo.height()
        offsets=[min(sw-1,x*sw//width)*3 for x in range(width)]
        rows=[]
        for y in range(sh):
            row=raw[y*sw*3:(y+1)*sw*3]
            rows.append(b''.join(row[x:x+3] for x in offsets))
        return tk.PhotoImage(data=f'P6\n{width} {sh}\n255\n'.encode()+b''.join(rows),format='PPM')

    def flip(self):
        play(self.app,'card_flip')
        self.offset(-5)
        x,y,r,b=self.box;w=r-x
        fractions=[.94,.80,.60,.37,.15,.035,.15,.37,.60,.80,.94,1.0]
        self.frames=[self.narrowed(self.image if i<6 else self.front,max(1,round(w*f)))
                     for i,f in enumerate(fractions)]
        def frame(n):
            photo=self.frames[n]
            self.canvas.itemconfigure(self.item,image=photo)
            self.canvas.coords(self.item,x+(w-photo.width())/2,y+self.dy)
            if n+1<len(self.frames):self.later(30,lambda:frame(n+1))
            else:self.later(30,self.settle)
        frame(0)
