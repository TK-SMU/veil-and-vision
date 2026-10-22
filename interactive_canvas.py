"""Route painted controls over their whole rectangle, including empty fills."""
import tkinter as tk


class InteractiveCanvas(tk.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.region_callbacks = {}
        self.region_hover = {}
        self.hovered_region = None
        self.feedback_original = {}
        self.selection_targets = {}
        self.selection_press = False
        self.generation = 0
        self.bind('<Motion>', self._region_motion, add='+')
        self.bind('<Leave>', self._region_leave, add='+')

    def create_rectangle(self, *args, **kwargs):
        # Tk interprets a string as a Tcl list: 'intro-Moon Diary' would
        # otherwise become two tags and could never be found by that name.
        if isinstance(kwargs.get('tags'),str):
            kwargs['tags']=(kwargs['tags'],)
        return super().create_rectangle(*args,**kwargs)

    def tag_bind(self, tag, sequence=None, func=None, add=None):
        if sequence in ('<Enter>', '<Leave>') and callable(func):
            self.region_hover.setdefault(tag, {})[sequence] = func
            return None
        if sequence == '<Button-1>' and callable(func):
            self.region_callbacks[tag] = func
            self.region_hover.setdefault(tag,{})
            self.region_hover[tag].setdefault('<Enter>',lambda e,t=tag:self.feedback(t,True))
            self.region_hover[tag].setdefault('<Leave>',lambda e,t=tag:self.feedback(t,False))
            return None
        return super().tag_bind(tag, sequence, func, add)

    def delete(self, *args):
        if 'all' in args:
            self.generation += 1
            self.selection_targets.clear()
            self.selection_press = False
            self.feedback_original.clear()
            self.region_callbacks.clear()
            self.region_hover.clear()
            self.hovered_region = None
        return super().delete(*args)

    def feedback(self,tag,on):
        if any("invisible-card-hit" in self.gettags(i) for i in self.find_withtag(tag)):return
        style=self.selection_targets.get(tag)
        if style:
            if on and not style.get('icon_lifted'):
                for icon in style.get('hover_items',[]):self.move(icon,0,-2)
                style['icon_lifted']=True
            elif not on and style.pop('icon_lifted',False):
                for icon in style.get('hover_items',[]):self.move(icon,0,2)
            item=style.get('visual_item',style['item'])
            if on:
                if 'rest' not in style:
                    style['rest']=(self.itemcget(item,'fill'),self.itemcget(item,'outline'))
                self.itemconfigure(item,fill='' if style.get('overlay') else (style['normal_fill'] if style.get('outline_only') else ('#ffbbdc' if style['selected'] else '#ffe5f1')),outline='#d65aa0' if style['selected'] else '#dfafce')
            elif 'rest' in style:
                fill,outline=style.pop('rest')
                self.itemconfigure(item,fill=fill,outline=outline)
            return
        for item in self.find_withtag(tag):
            if self.type(item)!='rectangle':continue
            if on:
                self.feedback_original.setdefault(item,self.itemcget(item,'outline'))
                self.itemconfigure(item,outline='#e9b2d2')
            elif item in self.feedback_original:
                self.itemconfigure(item,outline=self.feedback_original.pop(item))

    def _region_leave(self, event):
        old = self.hovered_region
        self.hovered_region = None
        callback = self.region_hover.get(old, {}).get('<Leave>')
        if callback:
            callback(event)

    def _region_motion(self, event):
        # Outline changes must not trigger an endless item Enter/Leave loop.
        # Hit-test the complete area independently of the painted outline.
        x, y = self.canvasx(event.x), self.canvasy(event.y)
        hit = None
        for tag in reversed(tuple(self.region_hover)):
            for item in self.find_withtag(tag):
                box = self.coords(item)
                if self.type(item) == 'rectangle' and len(box) == 4:
                    if box[0] <= x <= box[2] and box[1] <= y <= box[3]:
                        hit = tag
                        break
            if hit is not None:
                break
        if hit == self.hovered_region:
            return
        self._region_leave(event)
        self.hovered_region = hit
        callback = self.region_hover.get(hit, {}).get('<Enter>')
        if callback:
            callback(event)

    def region_at(self, event):
        x, y = self.canvasx(event.x), self.canvasy(event.y)
        for tag in reversed(tuple(self.region_callbacks)):
            for item in self.find_withtag(tag):
                box = self.coords(item)
                if self.type(item) == 'rectangle' and len(box) == 4:
                    if box[0] <= x <= box[2] and box[1] <= y <= box[3]:
                        return tag
        return None

    def press_selection(self,tag,callback,event):
        if self.selection_press:return
        style=self.selection_targets[tag]
        self.selection_press=True
        self.feedback(tag,False)
        x,y,r,b=self.coords(style['item'])
        group='selection-press'
        for item in self.find_enclosed(x-3,y-3,r+3,b+3):
            self.addtag_withtag(group,item)
        self.itemconfigure(style.get('visual_item',style['item']),fill='' if style.get('overlay') else (style['normal_fill'] if style.get('outline_only') else '#ffafd4'),outline='#d65aa0')
        movement=0 if style.get("outline_only") else 1
        self.move(group,0,movement)
        generation=self.generation
        def release():
            if generation!=self.generation:return
            self.move(group,0,-movement);self.dtag(group,group)
            self.selection_press=False
            # The callback redraws from saved state, so hover cannot overwrite
            # the newly selected appearance on the next screen generation.
            callback(event)
        self.after(80,release)

    def dispatch_region(self, event):
        if self.selection_press:return True
        x, y = self.canvasx(event.x), self.canvasy(event.y)
        for tag, callback in reversed(tuple(self.region_callbacks.items())):
            for item in self.find_withtag(tag):
                box = self.coords(item)
                if self.type(item) == 'rectangle' and len(box) == 4:
                    if box[0] <= x <= box[2] and box[1] <= y <= box[3]:
                        if tag in self.selection_targets:
                            self.press_selection(tag,callback,event)
                            return True
                        if 'invisible-card-hit' not in self.gettags(item):
                            self.feedback(tag,True)
                            self.itemconfigure(item,outline='#d65aa0')
                            self.after(100,lambda t=tag:self.feedback(t,False))
                        callback(event)
                        return True
        return False

    def focus_next_region(self):
        regions=list(self.region_callbacks)
        if not regions: return
        self.region_focus=(getattr(self,'region_focus',-1)+1)%len(regions)
        self.delete('keyboard-focus')
        box=self.bbox(regions[self.region_focus])
        invisible=any('invisible-card-hit' in self.gettags(i) for i in self.find_withtag(regions[self.region_focus]))
        if box and not invisible:self.create_rectangle(*box,outline='#d65aa0',width=2,tags='keyboard-focus')

    def activate_region(self):
        from types import SimpleNamespace
        regions=list(self.region_callbacks)
        index=getattr(self,'region_focus',-1)
        if not 0<=index<len(regions): return False
        box=self.bbox(regions[index])
        if not box: return False
        self.region_callbacks[regions[index]](SimpleNamespace(widget=self,x=(box[0]+box[2])/2,y=(box[1]+box[3])/2))
        return True
