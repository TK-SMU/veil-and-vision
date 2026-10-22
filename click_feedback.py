"""Pink press feedback that preserves the underlying reference artwork."""
import tkinter as tk

def bind_feedback(widget):
    cache={}
    original={}
    def restore(event=None):
        if not original or not widget.winfo_exists():return
        widget.configure(**original)
        original.clear()
    def press(event=None):
        if original:return
        name=str(widget.cget('image'))
        original.update(image=name,background=widget.cget('background'),
                        activebackground=widget.cget('activebackground'))
        if name:
            if name not in cache:
                source=tk.PhotoImage(master=widget)
                source.tk.call(str(source),'copy',name)
                tinted=tk.PhotoImage(master=widget,width=source.width(),height=source.height())
                rows=[]
                for y in range(source.height()):
                    row=[]
                    for x in range(source.width()):
                        rgb=source.get(x,y)
                        if isinstance(rgb,str):rgb=tuple(map(int,rgb.split()))
                        mix=tuple(round(c*.72+p*.28) for c,p in zip(rgb,(255,123,169)))
                        row.append('#%02x%02x%02x'%mix)
                    rows.append('{'+ ' '.join(row)+'}')
                tinted.put(' '.join(rows));cache[name]=tinted
            widget.configure(image=cache[name])
        widget.configure(background='#f6bbdc',activebackground='#f6bbdc')
    widget.bind('<ButtonPress-1>',press,add='+')
    widget.bind('<ButtonRelease-1>',restore,add='+')
    widget.bind('<Leave>',restore,add='+')
    widget.bind('<KeyPress-space>',press,add='+')
    widget.bind('<KeyRelease-space>',restore,add='+')

