"""Register the bundled font privately; never install or change system fonts."""
import ctypes as ct
import sys
from pathlib import Path
from tkinter import font as tkfont

from design_system import FONT_FAMILY as FAMILY
from design_system import TYPE
_registered=False

def setup(root):
    global _registered
    path=Path(__file__).parent/'assets/fonts/PixelifySans.ttf'
    if not _registered:
        if sys.platform=='darwin':
            cf=ct.CDLL('/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation')
            core=ct.CDLL('/System/Library/Frameworks/CoreText.framework/CoreText')
            cf.CFURLCreateFromFileSystemRepresentation.argtypes=[ct.c_void_p,ct.c_char_p,ct.c_long,ct.c_bool]
            cf.CFURLCreateFromFileSystemRepresentation.restype=ct.c_void_p
            cf.CFRelease.argtypes=[ct.c_void_p]
            core.CTFontManagerRegisterFontsForURL.argtypes=[ct.c_void_p,ct.c_int,ct.c_void_p]
            core.CTFontManagerRegisterFontsForURL.restype=ct.c_bool
            raw=str(path).encode();url=cf.CFURLCreateFromFileSystemRepresentation(None,raw,len(raw),False)
            try:core.CTFontManagerRegisterFontsForURL(url,1,None)
            finally:cf.CFRelease(url)
        elif sys.platform=='win32':
            ct.windll.gdi32.AddFontResourceExW(str(path),0x10,0)
        else:
            fc=ct.CDLL('libfontconfig.so.1')
            fc.FcConfigGetCurrent.restype=ct.c_void_p
            fc.FcConfigAppFontAddFile.argtypes=[ct.c_void_p,ct.c_char_p]
            fc.FcConfigAppFontAddFile(fc.FcConfigGetCurrent(),str(path).encode())
        _registered=True
    # Cocoa's family list can lag the CoreText registration notification.
    # Resolve the actual face directly before checking the enumerated families.
    probe=tkfont.Font(root=root,family=FAMILY,size=14)
    root.update_idletasks()
    if probe.actual('family') != FAMILY and FAMILY not in tkfont.families(root):
        raise RuntimeError('The bundled Pixelify Sans font could not be loaded.')
    for name in ('TkDefaultFont','TkTextFont','TkMenuFont','TkHeadingFont','TkCaptionFont',
                 'TkSmallCaptionFont','TkIconFont','TkTooltipFont','TkFixedFont'):
        # nametofont resolves fonts in Tk's current interpreter; unlike
        # Font/families it does not accept a root keyword argument.
        tkfont.nametofont(name).configure(family=FAMILY,size=-TYPE['body'])
    root.option_add('*Font',(FAMILY,-TYPE['body']))
    return FAMILY
