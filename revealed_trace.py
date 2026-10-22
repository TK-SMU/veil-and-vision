from page_frame import shared_scale, page_origin, APP_WIDTH, APP_HEIGHT
"""Pixel-accurate trace of Screen 5: Your Cards."""
from pathlib import Path
import tkinter as tk
from page_frame import draw_panel
from card_effects import CardEffect, separate_cards
from artwork_text import clear as clear_art_text

SOURCE_BOX = (27, 416, 398, 728)
BASE_SIZE = (371, 312)
CARD_BOXES = [(38, 50, 128, 174), (146, 50, 236, 174), (254, 50, 344, 174)]

def draw(app):
    if not getattr(app, 'revealed_trace', False) or app.screen != 'revealed':
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
        for x,y,r,b in CARD_BOXES:
            clear_art_text(raw,(x+8,192,r-5,207),x+(14 if x==254 else 6))
        panel = app.resized(raw, out_w, out_h, ('revealed-trace', out_w, out_h))
        app.images.append(panel)
        app.canvas.configure(width=width, height=height, bg='#d5d2ff')
        ox, oy = page_origin(app)
        background, _ = separate_cards(app, panel, CARD_BOXES, fit)
        app.images.append(background)
        draw_panel(app, background, ox, oy, fit, BASE_SIZE)
        app.controls = {}

        if getattr(app, 'reading', None):
            from card_art import image as tarot_image
            for i, card in enumerate(app.reading.get('cards', [])):
                x, y, r, b = CARD_BOXES[i]
                img = tarot_image(app, card, round((r-x)*fit), round((b-y)*fit))
                app.images.append(img)
                effect=CardEffect(app,i,(ox+round(x*fit),oy+round(y*fit),ox+round(x*fit)+img.width(),oy+round(y*fit)+img.height()),img,revealed=True)
                app.card_effects.append(effect)
                # Replace the baked sample orientation label with the actual
                # orientation from Screen 4 while keeping its exact position.
                ly = round(190*fit)
                label = card.get('orientation', 'Upright') + (' ↑' if card.get('orientation') == 'Upright' else ' ↓')
                app.canvas.create_text(ox+round((x+r)/2*fit), oy+round(201*fit),
                                       text=label, fill='#3f3a8a',
                                       font=(app.font_family, -max(10, round(12*fit))))

        # View Reading button from the reference panel.
        tag = 'revealed-reading'
        rect = app.canvas.create_rectangle(ox+round(166*fit), oy+round(276*fit),
                                            ox+round(350*fit), oy+round(303*fit), outline='', tags=tag)
        app.canvas.tag_bind(tag, '<Button-1>', lambda e: app.run_action(lambda: app.go('reading')))
        app.rendered_size = (width, height)
        return True
    finally:
        app._drawing_compact = False
