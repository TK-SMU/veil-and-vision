"""Place the original, untouched page inside the shared outer container."""


# One design grid and one fixed application container for all twelve pages.
APP_WIDTH = 761
APP_HEIGHT = 740
DESIGN_WIDTH = 371
DESIGN_HEIGHT = 345


# Page 4's approved scale stays fixed; only its unused outer side margins go.
CONTENT_SCALE = 740 / 345
PAGE_BASES = {
    'intro': (371,345), 'oracle': (338,345), 'intention': (355,345),
    'draw': (355,345), 'revealed': (371,312), 'meaning': (338,312),
    'reading': (355,312), 'reflect': (355,312), 'save': (362,260),
    'diary': (353,260), 'followup': (355,260), 'settings': (356,260),
}


def scale_for(page):
    if page=='draw':return CONTENT_SCALE
    w,h=PAGE_BASES[page]
    return min(APP_WIDTH/w, APP_HEIGHT/h)


def shared_scale(app):
    return scale_for(app.screen)


def page_origin(app):
    w,h=PAGE_BASES[app.screen];scale=shared_scale(app)
    return ((APP_WIDTH-round(w*scale))//2,
            (APP_HEIGHT-round(h*scale))//2)


def draw_panel(app, panel, ox, oy, scale, base_size):
    import tkinter as tk
    width,height=APP_WIDTH,APP_HEIGHT
    # Cover the whole client area with page material, never a default widget
    # strip. This is behind the untouched art and never changes its coordinates.
    paper='#302d79' if app.screen=='draw' else '#5754b6' if app.screen=='intro' else '#fff8f2'
    app.canvas.create_rectangle(0,0,width,height,fill=paper,outline='',tags='page-background')
    from page_extension import draw as extend_edges
    extend_edges(app,scale)
    # Preserve all interior pixels at their current scale. Only the old page
    # chrome is replaced by the single outer app frame, shared on every page.
    trim=max(1,round(2*scale));bar=round(21*scale)
    key=('page-interior',str(panel),trim,bar)
    if key not in app.cache:
        interior=tk.PhotoImage(width=panel.width()-2*trim,height=panel.height()-bar-trim)
        interior.tk.call(str(interior),'copy',str(panel),'-from',trim,bar,panel.width()-trim,panel.height()-trim,'-to',0,0)
        app.cache[key]=interior
    interior=app.cache[key];app.images.append(interior)
    app.canvas.create_image(ox+trim,oy+bar,anchor='nw',image=interior,tags='page-content')
    header_height=round(21*CONTENT_SCALE)
    key=('shared-title-bar',width,header_height)
    if key not in app.cache:
        raw=tk.PhotoImage(width=371,height=21)
        raw.tk.call(str(raw),'copy',str(app.board_source),'-from',27,36,398,57,'-to',0,0)
        app.cache[key]=app.resized(raw,width,header_height,key)
    header=app.cache[key];app.images.append(header)
    app.canvas.create_rectangle(0,0,width,header_height,fill='#c8c5ff',outline='')
    app.canvas.create_image(0,0,anchor='nw',image=header,tags='shared-title-bar')
    app.canvas.create_rectangle(1,1,width-1,height-1,outline='#3535ad',width=2,tags='page-frame')
    app.panel_photo=panel
    app.panel_origin=(ox,oy)
    app.page_frame_bounds=(0,0,width,height)
    app.content_art_bounds=(ox,oy,ox+panel.width(),oy+panel.height())
