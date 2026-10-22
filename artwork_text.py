"""Clear baked sample lettering inside an existing painted panel only."""
def clear(image, box, sample_x):
    x,y,r,b=box
    # Copy a clean vertical background strip from the SAME painted panel.
    # This retains its row shading rather than adding an opaque Canvas panel.
    image.tk.call(str(image),'copy',str(image),'-from',sample_x,y,sample_x+1,b,
                  '-to',x,y,'-zoom',r-x,1)
