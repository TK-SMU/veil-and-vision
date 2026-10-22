from page_frame import shared_scale, page_origin, APP_WIDTH, APP_HEIGHT
"""Pixel-accurate trace of Screen 2: Create Your Oracle."""
from pathlib import Path
import tkinter as tk
from page_frame import draw_panel
from selection_style import apply as selection_style, tinted_thumbnail, tint_fill
from selection_state import selected
from check_badge import draw as draw_check

SOURCE_BOX = (420, 36, 758, 381)
BASE_SIZE = (338, 345)

def draw(app):
    if not getattr(app, 'oracle_trace', False) or app.screen != 'oracle':
        return False
    app._drawing_compact = True
    try:
        if not hasattr(app, 'board_source'):
            app.board_source = tk.PhotoImage(file=str(Path(__file__).with_name('reference_current.png')))
        width, height = (APP_WIDTH,APP_HEIGHT)
        fit = shared_scale(app)
        out_w, out_h = round(BASE_SIZE[0] * fit), round(BASE_SIZE[1] * fit)
        raw = tk.PhotoImage(width=BASE_SIZE[0], height=BASE_SIZE[1])
        raw.tk.call(str(raw), 'copy', str(app.board_source), '-from', *SOURCE_BOX, '-to', 0, 0)
        panel = app.resized(raw, out_w, out_h, ('oracle-trace', out_w, out_h))
        app.images.append(panel)
        app.canvas.configure(width=width, height=height, bg='#5754b6')
        ox, oy = page_origin(app)
        draw_panel(app, panel, ox, oy, fit, BASE_SIZE)
        app.controls = {}

        def region(name, box, fn):
            x, y, r, b = [round(v*fit) for v in box]
            tag = f'oracle-{name}'
            rect = app.canvas.create_rectangle(ox+x, oy+y, ox+r, oy+b,
                                                outline='', width=2, tags=tag)
            app.canvas.tag_bind(tag, '<Enter>', lambda e, rect=rect: app.canvas.itemconfigure(rect, outline='#ffd0ef'))
            app.canvas.tag_bind(tag, '<Leave>', lambda e, rect=rect: app.canvas.itemconfigure(rect, outline=''))
            app.canvas.tag_bind(tag, '<Button-1>', lambda e, fn=fn: app.run_action(fn))

        categories = ['Hats', 'Buddies', 'Accessories', 'Backgrounds']
        for i, category in enumerate(categories):
            tab_box=[(14,166,78,188),(80,166,149,188),(151,166,235,188),(238,166,322,188)][i]
            x,y,r,b=tab_box
            tab_style=app.canvas.create_rectangle(ox+round(x*fit),oy+round(y*fit),ox+round(r*fit),oy+round(b*fit))
            selection_style(app,tab_style,selected(app,'oracle-tabs',category),'oracle-tabs',overlay=True)
            region('tab-'+category, [(14,166,78,188),(80,166,149,188),(151,166,235,188),(238,166,322,188)][i], lambda c=category: app.set_category(c))

        from oracle_preview import update_oracle_preview
        update_oracle_preview(app)
        region('left',(16,102,44,137),lambda:app.cycle_style(-1))
        region('right',(291,102,319,137),lambda:app.cycle_style(1))

        # Six visible selection slots in the reference layout.
        from wardrobe import OPTIONS, LABELS
        key, choices = OPTIONS.get(getattr(app, 'category', 'Hats'), ('hat', ['Star','Flower','Sleepy','Frog','Sun','None']))
        if app.category=='Backgrounds':
            app.canvas.create_rectangle(ox+round(16*fit),oy+round(193*fit),ox+round(318*fit),oy+round(309*fit),fill='#fffbf2',outline='')
        for i, choice in enumerate(choices[:6]):
            x = 16 + (i % 3) * 103
            y = 193 + (i // 3) * 60
            chosen=selected(app,key,choice)
            slot=app.canvas.create_rectangle(ox+round(x*fit),oy+round(y*fit),ox+round((x+96)*fit),oy+round((y+56)*fit),
                fill='#ffe1f0' if chosen else '#fffbf2',outline='#d65aa0' if chosen else '#d4c7ee',width=max(1,round(fit)),tags='oracle-item-'+str(i))
            selection_style(app,slot,chosen,'oracle-items',normal_fill='#ffe4f1' if key=='hat' and choice=='Star' else '#fffbf2',outline_only=True)
            if chosen:app.canvas.itemconfigure(slot,fill=tint_fill(app.selection_styles[-1]['normal_fill']))
            from slot_art import thumbnail
            sprite=thumbnail(app,app.category,choice,64,34)
            if sprite:
                if chosen:sprite=tinted_thumbnail(app,sprite,(app.category,choice))
                sprite=app.resized(sprite,round(sprite.width()*fit),round(sprite.height()*fit),('slot',app.category,choice,chosen))
                app.images.append(sprite)
                icon=app.canvas.create_image(ox+round((x+48)*fit),oy+round((y+20)*fit),image=sprite,tags='inventory-icon')
                # Only the little icon lifts; the slot and its hitbox stay fixed.
                app.selection_styles[-1]['hover_items']=[icon]
            label=LABELS.get(choice,choice)
            if choice=='Frog' and app.category=='Hats': label='Frog Hat'
            label_item=app.canvas.create_text(ox+round((x+48)*fit),oy+round((y+46)*fit),text=label,fill='#10149a',font=(app.font_family,-round(10*fit)))
            # This existing slot is also the click target. No separate button,
            # overlay rectangle or duplicate border is drawn over the artwork.
            tag='oracle-item-'+str(i)
            app.canvas.tag_bind(tag,'<Button-1>',lambda e,key=key,choice=choice:app.run_action(lambda:app.change(**{key:choice})))
            if chosen:
                draw_check(app.canvas,(ox+round((x+82)*fit),oy+round((y+3)*fit),ox+round((x+93)*fit),oy+round((y+14)*fit)),tag='oracle-background-check' if app.category=='Backgrounds' else 'oracle-item-check')
            app.canvas.tag_raise(label_item)
        region('next', (80, 315, 258, 340), lambda: app.go('intention'))
        app.rendered_size = (width, height)
        return True
    finally:
        app._drawing_compact = False
