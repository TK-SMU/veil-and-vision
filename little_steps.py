"""Local, fixed suggestions and matching 16-pixel inventory illustrations."""
import random
import tkinter as tk

LITTLE_STEPS = (
    'Listen to a favourite song', 'Take a short pause', 'Get some fresh air',
    'Make a warm drink', 'Stretch for a minute', 'Write one kind thought',
    'Tidy one small space', 'Message someone you care about',
    'Read a few pages of something you enjoy',
    'Sit somewhere peaceful for five minutes',
    'Take three slow breaths', 'Take a short walk',
    'Give yourself permission to rest',
)

def suggestions(reading):
    if reading is None:return list(LITTLE_STEPS[:3])
    if 'little_step_options' not in reading:
        reading['little_step_options']=random.sample(list(LITTLE_STEPS),3)
    return reading['little_step_options']

# Every icon uses the same resolution, outline, pastel fills and tiny highlight.
PALETTE={'o':'#65518e','p':'#f1afd4','b':'#b9c9f6','c':'#fff7df','g':'#bbd7b5','s':'#ecd399'}
PATTERNS=(
 ('.....oooooo.....','...oo......oo...','..o..bbbbbb..o..','..o.bb....bb.o..','..obb......bbo..','..obb......bbo..','..opp......ppo..','..opp......ppo..','..opp......ppo..','...oo......oo...'),
 ('.......ss.......','......ss........','.....ss.........','.....ss..s......','......ssss......','...oooo.........','..obbbboooo.....','.obbbbbbbbbo....','..ooooooooo.....'),
 ('.......pp.......','......popo......','.......ss.......','.......oo.......','...gg..oo..gg...','..ogggoooggggo..','...ogggoogggo...','....oggooggo....','.......oo.......'),
 ('.....c..c.......','....c..c........','.....c..c.......','...oooooooo.....','...oppppppooo...','...opcppppo.o...','...oppppppooo...','....oppppo......','...oooooooo.....','..ssssssssss....'),
 ('.......oooo.....','......obbbbo....','.......oooo.....','...oooooooooo...','..oppppppppppo..','.......oo.......','......obbo......','.....ob..bo.....','....oo....oo....'),
 ('...oooooooooo...','...obbbbbbbbo...','...obcccccobo...','...obpppppbbo...','...obpopopbbo...','...obpppppbbo...','...obbpppbbbo...','...obbbpbbbbo...','...oooooooooo...'),
 ('.....oooooo.....','....o......o....','....o......o....','..oooooooooooo..','...oppppppppo...','...opcppppppo...','....oppppppo....','....oooooooo....','............s...','...........sss..'),
 ('..oooooooooooo..','..occcccccccco..','..oocccccccooo..','..ocoocccoooco..','..occoooooccoo..','..occcpppcccco..','..occcpppcccco..','..occccpccccco..','..oooooooooooo..'),
 ('..ooooo.ooooo...','..occcoooccco...','..occbooobcco...','..occcoooccco...','..occbooobcco...','..occcoooccco...','..occcoooccco...','..ooooo.ooooo...'),
 ('.....oooo.......','....osso....s...','...osso....sss..','...osso.....s...','...osso.........','....osso..o.....','.....osssso.....','......oooo......','..s.............','..sss...........'),
 # Breathing cloud with three gentle air trails.
 ('..........bbb...','.........b......','..........bbb...',
  '....oooo........','..ooccccoo..bbb.','.occcccccco.....',
  '.ococccocco.bbb.','.occcccccco.....','..oooooooo......'),
 # Pastel walking shoe and a tiny flower.
 ('............p...','...........psp..','............g...',
  '..oooo......g...','..obbo..........','..obbooo........',
  '..obbbbpoo......','..obbbpbcco.....','.obbbbbbbbbo....',
  '.occccccccco....','..ooooooooo.....'),
 # Sleepy crescent resting on a pink pillow.
 ('....oooo....sss.','...osso......s..','..ossco.........',
  '..osso..........','..osso..o.......','...osssoo.......',
  '....oooo........','..oooooooooooo..','.oppppppppppppo.',
  '.opcppppppppppo.','..oooooooooooo..'),
)

def icon(app,label):
    index=LITTLE_STEPS.index(label) if label in LITTLE_STEPS else 5
    key=('little-step-pixel-icon',index)
    if key not in app.cache:
        image=tk.PhotoImage(width=16,height=16)
        rows=PATTERNS[index];dy=(16-len(rows))//2
        for y,row in enumerate(rows):
            for x,char in enumerate(row[:16]):
                if char in PALETTE:image.put(PALETTE[char],(x,y+dy))
        app.cache[key]=image
    return app.cache[key]
