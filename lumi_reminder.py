"""A small local-art reminder; the reading page stays unchanged underneath."""
from pathlib import Path
import tkinter as tk
from row_shape import draw

def show(app):
    previous=getattr(app,'intention_reminder',None)
    if previous is not None and previous.winfo_exists():
        previous.lift();return
    popup=tk.Toplevel(app.root);app.intention_reminder=popup
    popup.title('A little reminder');popup.transient(app.root);popup.resizable(False,False)
    app.root.update_idletasks()
    popup.geometry(f'360x250+{app.root.winfo_rootx()+max(0,(app.root.winfo_width()-360)//2)}+{app.root.winfo_rooty()+max(0,(app.root.winfo_height()-250)//2)}')
    cv=tk.Canvas(popup,width=360,height=250,bg='#fff8f2',bd=0,highlightthickness=0);cv.pack()
    cv.create_rectangle(4,4,355,245,outline='#bca8e5',width=2)
    source=tk.PhotoImage(file=str(Path(__file__).parent/'assets/oracle/lumi_reconstructed.png'))
    source=app.trim_sprite(source.subsample(max(1,max(source.width(),source.height())//160)))
    ratio=min(104/source.width(),100/source.height())
    popup.lumi=app.resized(source,round(source.width()*ratio),round(source.height()*ratio),'reminder-lumi')
    cv.create_image(180,65,image=popup.lumi)
    cv.create_text(180,145,text='Choose what’s on\nyour heart first ♡',justify='center',fill='#3f3a8a',font=(app.font_family,-16))
    button=draw(cv,(80,191,280,229),'#f7c9e3','#cb88bb',2)
    cv.addtag_withtag('dismiss',button)
    cv.create_text(180,210,text='Choose an intention',fill='#3f3a8a',font=(app.font_family,-13),tags='dismiss')
    def close(event=None):
        popup.grab_release();popup.destroy();app.canvas.focus_set()
    cv.tag_bind('dismiss','<Button-1>',close)
    cv.tag_bind('dismiss','<Enter>',lambda e:cv.configure(cursor='hand2'))
    cv.tag_bind('dismiss','<Leave>',lambda e:cv.configure(cursor=''))
    popup.bind('<Return>',close);popup.bind('<Escape>',close)
    popup.protocol('WM_DELETE_WINDOW',close);popup.grab_set();popup.focus_set()
