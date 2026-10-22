"""Bounded pixel-rounded row skin; hit coordinates remain unchanged."""
def draw(canvas, box, fill, outline, width=1):
    x,y,r,b=box
    inset=min(6,(b-y)/4)
    return canvas.create_polygon(
        x+inset,y,r-inset,y,r,y+inset,r,b-inset,r-inset,b,
        x+inset,b,x,b-inset,x,y+inset,
        fill=fill,outline=outline,width=width,joinstyle='round')
