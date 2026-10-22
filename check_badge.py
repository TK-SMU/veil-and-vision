"""One font-independent pixel seal for selected and completed states."""
def draw(canvas, box, tag="selection-check"):
    x, y, right, bottom = box
    sx, sy = (right-x)/20, (bottom-y)/20
    tags = ("veil-check-badge", tag)
    def block(a,b,c,d,color):
        return canvas.create_rectangle(x+a*sx,y+b*sy,x+c*sx,y+d*sy,
                                       fill=color,outline="",tags=tags)
    # Stepped silhouette, shared by compact selectors and the saved seal.
    rows = [(0,2,6,14),(2,4,3,17),(4,6,1,19),(6,14,0,20),
            (14,16,1,19),(16,18,3,17),(18,20,6,14)]
    for top,base,left,end in rows: block(left,top,end,base,"#65518e")
    for top,base,left,end in rows:
        block(max(left+1,1),max(top,1),min(end-1,19),min(base,19),"#efa6ce")
    block(4,15,16,17,"#d780b5")
    block(6,17,14,19,"#d780b5")
    block(5,2,14,3,"#ffe7f2")
    block(3,4,5,7,"#ffd9eb")
    # Cream tick, built from pixels rather than a platform font glyph.
    for a,b,c,d in [(4,10,6,12),(6,12,8,14),(8,11,10,13),
                    (10,9,12,11),(12,7,14,9),(14,5,16,7)]:
        block(a,b,c,d,"#fffbe6")
    block(15,2,16,5,"#fffbe6")
    block(14,3,17,4,"#fffbe6")
    return canvas.find_withtag(tag)
