"""Page 2 only: local, alpha-composited wardrobe on reconstructed Lumi."""
from pathlib import Path
import tkinter as tk
from page_frame import shared_scale,page_origin
from wardrobe import OPTIONS

# Inside the original preview frame, in Panel 2 artwork coordinates.
VIEW=(34,72,304,160)
HATS={
 'Star':(76,40,143,40), 'Flowers':(66,23,143,30),
 'Sleepy':(72,39,144,39), 'Frog':(67,36,143,36),
 'Sun':(85,39,143,39),
}
ACCESSORIES={
 'Bow':(23,18,141,62),'Crystal':(20,20,141,61),
 'Scarf':(31,22,141,59),'Pin':(14,14,153,66),
 'Clip':(15,16,165,31),
}

def update_oracle_preview(app):
    """Read the same saved selections as slots; replace one preview image."""
    if app.screen!='oracle':return
    key='reconstructed-lumi-base'
    if key not in app.cache:
        source=tk.PhotoImage(file=str(Path(__file__).parent/'assets/oracle/lumi_reconstructed.png'))
        # Trim alpha padding after downsampling, avoiding a million Tcl calls.
        small=source.subsample(max(1,max(source.width(),source.height())//160))
        app.cache[key]=app.trim_sprite(small)
    source=app.cache[key]
    ratio=min(76/source.width(),74/source.height())
    cat=app.resized(source,round(source.width()*ratio),round(source.height()*ratio),key)
    x,y,r,b=VIEW;w,h=r-x,b-y
    background=app.settings.get('selected_background') or 'Day'
    scene=app.wardrobe_background(background,w,h)
    app.paste_layer(scene,cat,139-cat.width()//2,h-cat.height())
    accessory=app.settings.get('accessory','None')
    if accessory in ACCESSORIES:
        sw,sh,cx,top=ACCESSORIES[accessory]
        sprite=app.wardrobe_sprite('Accessories',accessory,sw,sh)
        app.paste_layer(scene,sprite,cx-sprite.width()//2,top)
    buddy=app.settings.get('buddy','None')
    if buddy in OPTIONS['Buddies'][1][:6] and buddy!='None':
        sprite=app.wardrobe_sprite('Buddies',buddy,29,31)
        app.paste_layer(scene,sprite,87-sprite.width(),h-sprite.height())
    hat=app.settings.get('hat','None')
    if hat in HATS:
        sw,sh,cx,baseline=HATS[hat]
        sprite=app.wardrobe_sprite('Hats',hat,sw,sh)
        app.paste_layer(scene,sprite,cx-sprite.width()//2,baseline-sprite.height())
    # The original arrows overlap the viewport: retain their exact pixels.
    for box in [(34,102,44,137),(291,102,304,137)]:
        left,top,right,bottom=box
        scene.tk.call(str(scene),'copy',str(app.board_source),'-from',420+left,36+top,420+right,36+bottom,'-to',left-x,top-y)
    fit=shared_scale(app);ox,oy=page_origin(app)
    state=(hat,buddy,accessory,background)
    photo=app.resized(scene,round(w*fit),round(h*fit),('oracle-preview-v1',state))
    app.preview_images={'composite':photo,'lumi':cat}
    app.oracle_scene=scene
    items=app.canvas.find_withtag('oracle-preview')
    if items:app.canvas.itemconfigure(items[0],image=photo)
    else:app.canvas.create_image(ox+round(x*fit),oy+round(y*fit),image=photo,anchor='nw',tags='oracle-preview')
