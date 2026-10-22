from page_frame import shared_scale, page_origin, APP_WIDTH, APP_HEIGHT
"""Pixel-accurate Intro Screen reconstruction from the supplied reference."""
from pathlib import Path
import tkinter as tk
from page_frame import draw_panel

SOURCE_BOX = (27, 36, 398, 381)
BASE_SIZE = (371, 345)

def draw(app):
    if not getattr(app, 'intro_trace', False) or app.screen != 'intro':
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
        panel = app.resized(raw, out_w, out_h, ('intro-trace', out_w, out_h))
        app.images.append(panel)
        app.canvas.configure(width=width, height=height, bg='#5754b6')
        ox, oy = page_origin(app)
        draw_panel(app, panel, ox, oy, fit, BASE_SIZE)
        app.controls = {}
        # Reference-relative hit regions: Start, Moon Diary, Settings.
        actions = [
            ((84, 214, 303, 244), 'Start', app.new_reading),
            ((84, 250, 303, 278), 'Moon Diary', lambda: app.go('diary')),
            ((84, 283, 303, 312), 'Settings', lambda: app.go('settings')),
        ]
        for (x, y, r, b), label, fn in actions:
            xx, yy, rr, bb = [round(v*fit) for v in (x, y, r, b)]
            tag = f'intro-{label}'
            rect = app.canvas.create_rectangle(ox+xx, oy+yy, ox+rr, oy+bb,
                                                outline='', width=2, tags=tag)
            app.canvas.tag_bind(tag, '<Enter>', lambda e, rect=rect: app.canvas.itemconfigure(rect, outline='#ffd0ef'))
            app.canvas.tag_bind(tag, '<Leave>', lambda e, rect=rect: app.canvas.itemconfigure(rect, outline=''))
            app.canvas.tag_bind(tag, '<Button-1>', lambda e, fn=fn: app.run_action(fn))
        app.rendered_size = (width, height)
        return True
    finally:
        app._drawing_compact = False
