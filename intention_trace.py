from page_frame import shared_scale, page_origin, APP_WIDTH, APP_HEIGHT
"""Pixel-accurate trace of Screen 3: Choose Intention."""
from pathlib import Path
import tkinter as tk
from page_frame import draw_panel
from selection_style import apply as selection_style
from selection_state import selected
from inline_fields import edit, show_value

SOURCE_BOX = (780, 36, 1135, 381)
BASE_SIZE = (355, 345)
INTENTIONS = ['Love', 'Career', 'Money', 'Family', 'Growth', 'Friendship', 'A Big Decision', 'General']

def draw(app):
    if not getattr(app, 'intention_trace', False) or app.screen != 'intention':
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
        panel = app.resized(raw, out_w, out_h, ('intention-trace', out_w, out_h))
        app.images.append(panel)
        app.canvas.configure(width=width, height=height, bg='#5754b6')
        ox, oy = page_origin(app)
        draw_panel(app, panel, ox, oy, fit, BASE_SIZE)
        app.controls = {}

        # Reference-relative 2 × 4 intention grid.
        card_w, card_h = 77, 68
        for i, label in enumerate(INTENTIONS):
            col, row = i % 4, i // 4
            x, y = 16 + col * 81, 69 + row * 75
            xx, yy, rr, bb = [round(v*fit) for v in (x, y, x+card_w, y+card_h)]
            tag = f'intention-{i}'
            rect = app.canvas.create_rectangle(ox+xx, oy+yy, ox+rr, oy+bb,
                                                fill='#ffc6e3' if app.intention == label else '', stipple='gray50',
                                                outline='#d65aa0' if app.intention == label else '',
                                                width=max(2, round(2*fit)), tags=tag)
            selection_style(app,rect,selected(app,'intentions',label),'intentions',overlay=True)
            if selected(app,'intentions',label):
                from check_badge import draw as draw_check
                draw_check(app.canvas,(ox+rr-round(15*fit),oy+yy+round(3*fit),ox+rr-round(3*fit),oy+yy+round(15*fit)),tag='intention-check')
            app.canvas.tag_bind(tag, '<Enter>', lambda e, rect=rect: app.canvas.itemconfigure(rect, outline='#ef9ac7'))
            app.canvas.tag_bind(tag, '<Leave>', lambda e, rect=rect, label=label: app.canvas.itemconfigure(rect, outline='#d65aa0' if app.intention == label else ''))
            app.canvas.tag_bind(tag, '<Button-1>', lambda e, label=label: app.run_action(lambda: app.select_intention(label)))

        # Optional question field opens a native text prompt without covering
        # the reference artwork with a generic widget.
        qbox = (16, 224, 337, 258)
        qtag = 'intention-question'
        qrect = app.canvas.create_rectangle(ox+round(qbox[0]*fit), oy+round(qbox[1]*fit),
                                            ox+round(qbox[2]*fit), oy+round(qbox[3]*fit),
                                            outline='', tags=qtag)
        app.canvas.tag_bind(qtag, '<Button-1>', lambda e: app.run_action(lambda: _edit_question(app)))

        show_value(app,(57,229,303,246),app.question.get(),fit,ox,oy)

        # Pink Next button at the fixed reference position.
        nbox = (75, 286, 280, 315)
        ntag = 'intention-next'
        nrect = app.canvas.create_rectangle(ox+round(nbox[0]*fit), oy+round(nbox[1]*fit),
                                            ox+round(nbox[2]*fit), oy+round(nbox[3]*fit),
                                            outline='', tags=ntag)
        app.canvas.tag_bind(ntag, '<Button-1>', lambda e: app.run_action(app.begin))
        app.rendered_size = (width, height)
        return True
    finally:
        app._drawing_compact = False

def _edit_question(app):
    edit(app,'question_entry',(57,229,303,246),BASE_SIZE,
         app.question.get(),app.question.set,500)
