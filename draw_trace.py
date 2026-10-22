from page_frame import shared_scale, page_origin, APP_WIDTH, APP_HEIGHT
"""Pixel-accurate trace of Screen 4: Drawing Cards."""
from pathlib import Path
import tkinter as tk
from page_frame import draw_panel
from card_effects import CardEffect, separate_cards

SOURCE_BOX = (1154, 36, 1509, 381)
BASE_SIZE = (355, 345)
CARD_BOXES = [(41, 81, 124, 202), (139, 81, 222, 202), (236, 81, 319, 202)]
# Actual painted card-back bounds in reference_current.png, relative to this page.
BACK_HIT_BOXES = [(41, 81, 124, 202), (139, 81, 222, 202), (236, 81, 319, 202)]

def draw(app):
    if not getattr(app, 'draw_trace', False) or app.screen != 'draw':
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
        panel = app.resized(raw, out_w, out_h, ('draw-trace', out_w, out_h))
        app.images.append(panel)
        app.canvas.configure(width=width, height=height, bg='#302d79')
        ox, oy = page_origin(app)
        background, backs = separate_cards(app, panel, CARD_BOXES, fit)
        # Protected screen: always use the original Panel 4 night artwork.
        # Wardrobe/Settings backgrounds must never affect this canvas.
        app.images.append(background)
        draw_panel(app, background, ox, oy, fit, BASE_SIZE)
        app.controls = {}

        from card_art import image as tarot_image
        if app.reading:
            for i,card in enumerate(app.reading['cards']):
                x,y,r,b=[round(v*fit) for v in CARD_BOXES[i]]
                face=tarot_image(app,card,r-x,b-y)
                opened=i in app.chosen
                effect=CardEffect(app,i,(ox+x,oy+y,ox+r,oy+b),
                                  face if opened else backs[i],front=face,revealed=opened)
                app.card_effects.append(effect)
        if len(app.chosen)==3:
            # Appears only after all reveals, in the existing space below labels.
            from row_shape import draw as row_shape
            box=(ox+round(113*fit),oy+round(229*fit),ox+round(243*fit),oy+round(247*fit))
            row_shape(app.canvas,box,'#ffe1f0','#d65aa0')
            app.canvas.create_text((box[0]+box[2])/2,(box[1]+box[3])/2,
                text='Continue →',fill='#3f3a8a',font=(app.font_family,-round(10*fit)))
            hit=app.canvas.create_rectangle(*box,fill='',outline='',tags='draw-continue')
            app.canvas.tag_bind(hit,'<Button-1>',lambda e:app.run_action(lambda:app.go('revealed')))
        app.rendered_size = (width, height)
        return True
    finally:
        app._drawing_compact = False
