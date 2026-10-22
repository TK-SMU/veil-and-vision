"""Keep a result inside its assigned text box without moving or shrinking it."""
def fit(canvas,item,bottom):
    original=canvas.itemcget(item,'text')
    visible=original
    while visible and canvas.bbox(item)[3]>bottom:
        visible=visible[:-1].rstrip()
        canvas.itemconfigure(item,text=visible.rstrip(' .')+'…')
    return item
