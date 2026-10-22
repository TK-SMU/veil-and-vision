"""Small, reusable Canvas effects. One after() timer; no threads or sleeps.

Artwork, controls and hitboxes are never moved by this module. The 15-item
particle pool is reused and is removed when its page is redrawn or closed.
"""
import math
import time
from page_frame import shared_scale

class MagicEffects:
    def __init__(self,app,entering=False):
        self.app=app;self.canvas=app.canvas;self.alive=True;self.job=None;self.initializing=True
        self.start=time.monotonic();self.burst_start=None;self.burst_box=None
        self.tag='magic-atmosphere';self.scale=shared_scale(app)
        self.ox,self.oy=app.panel_origin
        self.stars=[]
        for _ in range(7):
            self.stars.append(tuple(self.canvas.create_rectangle(0,0,0,0,fill='#fff0bf',outline='',state='hidden',tags=self.tag) for _ in range(2)))
        self.glow=self.canvas.create_rectangle(0,0,0,0,fill='',outline='#e4badf',width=1,state='hidden',tags=self.tag)
        # Reference coordinates lie in decorative margins, never over labels.
        self.points={
            'intro':[(74,64),(145,43),(269,64),(339,187)],
            'oracle':[(43,84),(290,89),(54,148),(291,146)],
            'draw':[(14,58),(333,77),(22,244),(332,251)],
            'revealed':[(13,190),(357,204)],
            'meaning':[(15,185),(322,207)],
            'reading':[(12,77),(341,242)],
            'reflect':[(12,243),(341,280)],
            'save':[(95,38),(162,33),(104,78),(159,78)],
            'diary':[(10,96),(342,208)],
            'followup':[], 'settings':[], 'intention':[],
        }.get(app.screen,[])
        self.fade=[]
        if entering and app.screen in ('meaning','reading'):
            for item in self.canvas.find_all():
                if self.canvas.type(item)!='text':continue
                x,y=self.canvas.coords(item)
                if self.oy+60*self.scale<y<self.oy+258*self.scale:
                    self.fade.append((item,self.canvas.itemcget(item,'fill')))
        if entering and app.screen=='save':self.burst(self.box((98,25,160,82)),.25)
        if entering and app.screen=='oracle':self.burst(self.box((43,80,290,88)),.25)
        if entering and app.screen=='draw':self.burst(self.box((30,61,325,70)),.25)
        if entering and app.screen=='revealed' and app.card_effects:self.burst(app.card_effects[1].box)
        self.initializing=False
        self.tick()

    def box(self,values):
        x,y,r,b=values;s=self.scale
        return self.ox+x*s,self.oy+y*s,self.ox+r*s,self.oy+b*s

    def star(self,items,x,y,size,color):
        # State disabled lets all mouse events reach the existing control below.
        for item,box in zip(items,((x-size,y-1,x+size,y+1),(x-1,y-size,x+1,y+size))):
            self.canvas.coords(item,*box)
            self.canvas.itemconfigure(item,fill=color,state='disabled')

    def burst(self,box,duration=.65):
        if not self.alive:return
        self.burst_box=tuple(box);self.burst_start=time.monotonic();self.burst_duration=duration
        if self.job is None and not self.initializing:self.tick()

    def tick(self):
        self.job=None
        if not self.alive:return
        now=time.monotonic();elapsed=now-self.start
        for i in range(4):
            if i>=len(self.points):continue
            x,y=self.points[i];phase=elapsed*.65+i*1.7
            light=(math.sin(phase)+1)/2
            # Quiet twinkles with a period of darkness; maximum drift is 2px.
            if light<.56:
                for item in self.stars[i]:self.canvas.itemconfigure(item,state='hidden')
            else:
                self.star(self.stars[i],self.ox+x*self.scale,self.oy+y*self.scale+math.sin(phase*.6)*2,2 if light<.85 else 3,'#e5d0ed' if light<.85 else '#fff0bf')
        if self.burst_start is not None:
            age=(now-self.burst_start)/self.burst_duration
            if age>=1:
                self.burst_start=None
                for pair in self.stars[4:]:
                    for item in pair:self.canvas.itemconfigure(item,state='hidden')
                self.canvas.itemconfigure(self.glow,state='hidden')
            else:
                x,y,r,b=self.burst_box
                self.canvas.coords(self.glow,x+2,y+2,r-2,b-2)
                self.canvas.itemconfigure(self.glow,state='hidden' if self.app.screen in ('oracle','draw') else 'disabled',outline='#e7badb' if age<.45 else '#efddec')
                for i,fraction in enumerate((.12,.5,.88)):
                    self.star(self.stars[i+4],x+(r-x)*fraction,y+6+math.sin(age*math.pi)*2,2 if age<.6 else 1,'#fff0bf' if age<.45 else '#dfc8eb')
        if self.fade:
            fraction=min(1,elapsed/.45)
            for item,color in self.fade:
                rgb=[int(color[i:i+2],16) for i in (1,3,5)]
                amount=.35+.65*fraction
                mixed='#'+''.join(f'{round(base*(1-amount)+v*amount):02x}' for base,v in zip((255,248,242),rgb))
                self.canvas.itemconfigure(item,fill=mixed)
            if fraction>=1:self.fade=[]
        if self.points or self.burst_start is not None or self.fade:
            self.job=self.app.root.after(80,self.tick)

    def dispose(self):
        self.alive=False
        if self.job is not None:
            self.app.root.after_cancel(self.job);self.job=None
        self.canvas.delete(self.tag)


def mount(app):
    previous=getattr(app,'_magic_page',None)
    app.magic=MagicEffects(app,entering=previous!=app.screen)
    app._magic_page=app.screen


def after_action(app,before):
    magic=getattr(app,'magic',None)
    if magic is None:return
    from sound_events import snapshot
    after=snapshot(app)
    changed=any(before[k]!=after[k] for k in ('settings','step','drafts','diary'))
    if not changed:return
    if app.screen=='settings' and (before['music']!=after['music'] or before['sound']!=after['sound']):
        x=120 if before['music']!=after['music'] else 281
        magic.burst(magic.box((x,128,x+36,147)))
    elif app.screen=='oracle':
        magic.burst(magic.box((36,76,299,156)))
    else:
        chosen=[s for s in app.selection_styles if s['selected']]
        if chosen:
            # The last selected group belongs to the current visible choices.
            magic.burst(app.canvas.coords(chosen[-1]['item']))
        elif app.screen=='settings':magic.burst(magic.box((39,215,317,232)))
        elif app.screen=='diary':
            entries=app.store.data.get('readings',[])
            index=next((i for i,r in enumerate(entries) if r['id']==(app.reading or {}).get('id')),None)
            if index is not None and index//4==getattr(app,'page',0):
                y=54+(index%4)*41
                magic.burst(magic.box((18,y,336,y+37)))
