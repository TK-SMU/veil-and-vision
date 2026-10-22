"""Use the Intro's footprint for one fixed window across all twelve pages."""
from importlib import import_module

PAGES = ('intro','oracle','intention','draw','revealed','meaning',
         'reading','reflect','save','diary','followup','settings')


def fit_window(app):
    from VeilAndVision import draw_reading
    from page_frame import APP_WIDTH, APP_HEIGHT
    # All renderers and hitboxes use page_frame.shared_scale. Smaller source
    # panels are centered without independently enlarging their contents.
    from page_frame import scale_for
    dimensions=[]
    for page in PAGES:
        module=import_module('intro_ui' if page=='intro' else page+'_trace')
        bw,bh=module.BASE_SIZE
        scale=scale_for(page)
        dimensions.append((round(bw*scale),round(bh*scale)))
    size=(APP_WIDTH,APP_HEIGHT)
    assert all(w<=APP_WIDTH and h<=APP_HEIGHT for w,h in dimensions)
    app.original_page_sizes=dict(zip(PAGES,dimensions))
    app.desktop_viewport=app.reference_viewport=size
    original_reading,original_chosen=app.reading,app.chosen
    app.reading=draw_reading(app.intention,app.question.get())
    app.chosen={0,1,2}
    requirements={}
    app.page_content_bounds={}
    try:
        for page in PAGES:
            app.desktop_viewport=size
            app.go(page)
            app.canvas.configure(width=size[0],height=size[1])
            app.root.update_idletasks()
            requirements[page]=(app.canvas.winfo_reqwidth(),app.canvas.winfo_reqheight())
            app.page_content_bounds[page]=app.canvas.bbox('all')
    finally:
        app.reading,app.chosen=original_reading,original_chosen
    app.page_requirements=requirements
    app.desktop_viewport=app.reference_viewport=app.rendered_size=size
    app.content_frame.configure(width=size[0],height=size[1])
    app.content_frame.pack_propagate(False)
    app.content_frame.grid_propagate(False)
    app.canvas.configure(width=size[0],height=size[1])
    app.go('intro')
    app.content_frame.place(x=0,y=0,width=APP_WIDTH,height=APP_HEIGHT)
    app.root.update_idletasks()
    app.root.geometry(f'{APP_WIDTH}x{APP_HEIGHT}')
    app.root.minsize(APP_WIDTH,APP_HEIGHT)
    app.root.maxsize(APP_WIDTH,APP_HEIGHT)
    app.root.resizable(False,False)
