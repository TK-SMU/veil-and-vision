"""Shared visual specification in logical pixels, independent of window scale."""
FONT_FAMILY='Pixelify Sans'
WINDOW=(463,778)
SPACING=(4,8,12,16,24,32)
PAGE_MARGIN=24
PANEL_PADDING=16
SECTION_GAP=12
TYPE={'logo':36,'heading':23,'section':17,'button':15,'tab':14,
      'body':14,'label':12,'caption':11,'card_title':12,'titlebar':18}
LINE_SPACING=3
COLORS={'paper':'#FFFBF2','lilac':'#F0EFF9','ink':'#3F3A8A','border':'#d5c5ed',
        'pink':'#FFAAD2','pink_border':'#D65AA0','gold':'#ffe6aa','night':'#2c2f7a',
        'disabled':'#9890af'}
GLASS_STATES={'normal':((255,170,210),.65),'hover':((255,150,205),.80),
              'pressed':((255,110,185),.88),'selected':((255,110,185),.88),
              'disabled':((235,209,230),.32)}
THEMES={'Day':{'paper':'#fffbf2','surround':'#dce8ff'},
        'Sunset':{'paper':'#fff0e9','surround':'#efccdf'},
        'Night':{'paper':'#eeeafa','surround':'#53517f'}}

def font(size='body',scale=1,bold=False):
    pixels=TYPE[size] if isinstance(size,str) else size
    return (FONT_FAMILY,-max(10,round(pixels*scale)),'bold' if bold else 'normal')
