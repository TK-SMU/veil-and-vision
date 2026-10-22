"""Small artwork-backed reading viewport with a custom pastel scroll control."""
import tkinter as tk

class MeaningScroll(tk.Canvas):
    def __init__(self,app,content,box,fit,*,font_size=12,color='#10149a',name='meaning'):
        x,y,r,b=box;w,h=r-x,b-y
        super().__init__(app.canvas,width=w,height=h,bd=0,highlightthickness=0,takefocus=1)
        self.app=app;self.offset=0;self.h=h;self.w=w;self.unit=max(12,round(12*fit))
        # Use the same panel pixels; no opaque white text widget over the art.
        self.backing=tk.PhotoImage(width=w,height=h)
        px,py=app.panel_origin
        self.backing.tk.call(str(self.backing),'copy',str(app.panel_photo),'-from',x-px,y-py,r-px,b-py,'-to',0,0)
        self.create_image(0,0,image=self.backing,anchor='nw')
        factor=1+(app.settings.get('text_size',50)-50)/500
        self.label=self.create_text(0,0,anchor='nw',text=content,width=w-round(12*fit),justify='left',fill=color,font=(app.font_family,-round(font_size*fit*factor)))
        self.total=self.bbox(self.label)[3]+2
        self.limit=max(0,self.total-h)
        self.track_x=w-round(5*fit);self.track_top=round(4*fit);self.track_bottom=h-round(4*fit)
        self.thumb_height=max(round(12*fit),(self.track_bottom-self.track_top)*min(1,h/max(1,self.total)))
        if self.limit:
            self.create_line(self.track_x,self.track_top,self.track_x,self.track_bottom,fill='#e3d8f5',width=max(3,round(3*fit)),capstyle='round')
            self.thumb=self.create_line(0,0,0,1,fill='#e9a9cd',width=max(5,round(5*fit)),capstyle='round',tags='scroll-thumb')
            self.create_text(self.track_x,h-1,text='⌄',anchor='s',fill='#8c75bd',font=(app.font_family,-round(8*fit)))
        else:self.thumb=None
        self.bind('<MouseWheel>',self.wheel)
        self.bind('<Button-4>',lambda e:self.scroll(-self.unit))
        self.bind('<Button-5>',lambda e:self.scroll(self.unit))
        self.bind('<Down>',lambda e:self.scroll(self.unit));self.bind('<Up>',lambda e:self.scroll(-self.unit))
        self.bind('<Next>',lambda e:self.scroll(h*.8));self.bind('<Prior>',lambda e:self.scroll(-h*.8))
        self.bind('<Home>',lambda e:self.set_offset(0));self.bind('<End>',lambda e:self.set_offset(self.limit))
        self.bind('<Button-1>',self.press);self.bind('<B1-Motion>',self.drag)
        self.bind('<ButtonRelease-1>',lambda e:setattr(self,'dragging',False))
        self.tag_bind('scroll-thumb','<Enter>',lambda e:self.itemconfigure(self.thumb,fill='#f2bbdb'))
        self.tag_bind('scroll-thumb','<Leave>',lambda e:self.itemconfigure(self.thumb,fill='#e9a9cd'))
        self.dragging=False;self.set_offset(0)
        app.canvas.create_window(x,y,window=self,anchor='nw',width=w,height=h,tags=name+'-scroll-area')
        app.widgets.append(self);setattr(app,name+'_scroll',self)

    def set_offset(self,value):
        self.offset=max(0,min(self.limit,value));self.coords(self.label,0,-self.offset)
        if self.thumb:
            span=self.track_bottom-self.track_top-self.thumb_height
            top=self.track_top+span*self.offset/self.limit
            self.coords(self.thumb,self.track_x,top,self.track_x,top+self.thumb_height)
        return 'break'

    def scroll(self,amount):return self.set_offset(self.offset+amount)

    def wheel(self,event):
        delta=event.delta
        amount=delta/120 if abs(delta)>=120 else delta
        return self.scroll(-amount*self.unit)

    def press(self,event):
        self.focus_set();self.dragging=bool(self.limit and event.x>=self.w-self.unit)
        if self.dragging:self.drag(event)
        return 'break'

    def drag(self,event):
        if self.dragging:
            span=max(1,self.track_bottom-self.track_top-self.thumb_height)
            self.set_offset((event.y-self.track_top-self.thumb_height/2)/span*self.limit)
        return 'break'
