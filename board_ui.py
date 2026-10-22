"""Full landscape reference board launcher.

The supplied board is the visual source of truth.  It is shown as one fitted
image so the proportions, typography and artwork stay exactly as authored.
Each panel is an invisible hit region that opens the corresponding live
screen, keeping the board useful as a presentation and navigation overview.
"""
from pathlib import Path
import tkinter as tk

BOARD_SIZE = (1536, 1024)
PANELS = {
    'intro': (27, 36, 398, 381), 'oracle': (420, 36, 758, 381),
    'intention': (780, 36, 1135, 381), 'draw': (1154, 36, 1509, 381),
    'revealed': (27, 416, 398, 728), 'meaning': (420, 416, 758, 728),
    'reading': (780, 416, 1135, 728), 'reflect': (1154, 416, 1509, 728),
    'save': (27, 754, 389, 1014), 'diary': (406, 754, 759, 1014),
    'followup': (779, 754, 1134, 1014), 'settings': (1154, 754, 1510, 1014),
}

def draw(app):
    if not getattr(app, 'board_mode', False):
        return False
    app._drawing_compact = True
    try:
        if not hasattr(app, 'board_source'):
            app.board_source = tk.PhotoImage(file=str(Path(__file__).with_name('reference_current.png')))
        width, height = getattr(app, 'desktop_viewport', BOARD_SIZE)
        fit = min(width / BOARD_SIZE[0], height / BOARD_SIZE[1])
        out_w, out_h = max(1, round(BOARD_SIZE[0] * fit)), max(1, round(BOARD_SIZE[1] * fit))
        board = app.resized(app.board_source, out_w, out_h, ('full-board', out_w, out_h))
        app.images.append(board)
        app.canvas.configure(width=width, height=height, bg='#5754b6')
        ox, oy = (width - out_w) // 2, (height - out_h) // 2
        app.canvas.create_image(ox, oy, anchor='nw', image=board)
        app.controls = {}
        for screen, (x, y, r, b) in PANELS.items():
            xx, yy, rr, bb = [round(v * fit) for v in (x, y, r, b)]
            # Canvas hit regions preserve the artwork and provide a gentle
            # lavender hover outline so it is clear that each panel is live.
            tag = f'board-{screen}'
            rect = app.canvas.create_rectangle(ox+xx, oy+yy, ox+rr, oy+bb,
                                                outline='', width=2, tags=tag)
            app.canvas.tag_bind(tag, '<Enter>', lambda e, rect=rect: app.canvas.itemconfigure(rect, outline='#ffd0ef'))
            app.canvas.tag_bind(tag, '<Leave>', lambda e, rect=rect: app.canvas.itemconfigure(rect, outline=''))
            app.canvas.tag_bind(tag, '<Button-1>', lambda e, screen=screen: app.open_live_screen(screen))
        app.rendered_size = (width, height)
        return True
    finally:
        app._drawing_compact = False
