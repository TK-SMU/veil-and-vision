# Veil & Vision — reference-art desktop app
# Run main.py with Python 3.10+ and Tkinter. Assets are bundled locally.

"""Shared, display-independent tarot logic and atomic JSON persistence."""
import json
import os
import random
from datetime import datetime
from pathlib import Path
from uuid import uuid4

INTENTIONS = ['Love', 'Career', 'Money', 'Family', 'Growth', 'Friendship', 'A Big Decision', 'General']
# Each card has distinct upright and reversed interpretations.
CARD_DATA = [
 ('The Fool', 'new beginnings and curiosity', 'rushing ahead without preparation'),
 ('The Magician', 'resourcefulness and confident action', 'unused skills and scattered energy'),
 ('The High Priestess', 'intuition and quiet understanding', 'ignoring your inner voice'),
 ('The Empress', 'care, creativity and growth', 'giving so much that your needs are overlooked'),
 ('The Emperor', 'stability and healthy boundaries', 'rigidity or a need to control everything'),
 ('The Hierophant', 'learning from traditions and trusted teachers', 'questioning rules that no longer fit'),
 ('The Lovers', 'meaningful connection and aligned choices', 'conflicting values or a need for honest communication'),
 ('The Chariot', 'determination and steady progress', 'competing priorities pulling you off course'),
 ('Strength', 'patient courage and compassion', 'self-doubt and depleted energy'),
 ('The Hermit', 'reflection and inner guidance', 'isolation or avoiding useful support'),
 ('Wheel of Fortune', 'change and a fresh cycle', 'resisting changes beyond your control'),
 ('Justice', 'fairness and thoughtful accountability', 'imbalance or an overlooked responsibility'),
 ('The Hanged Man', 'pausing to see another perspective', 'feeling stuck or postponing a decision'),
 ('Death', 'an ending that makes room for renewal', 'holding on to something you have outgrown'),
 ('Temperance', 'balance and gentle moderation', 'overextension and a need to restore balance'),
 ('The Devil', 'recognising habits that limit your freedom', 'loosening an unhealthy attachment'),
 ('The Tower', 'a sudden shift revealing a weak foundation', 'avoiding a change that needs attention'),
 ('The Star', 'hope, healing and renewed trust', 'discouragement and a need for self-kindness'),
 ('The Moon', 'uncertainty, dreams and intuition', 'confusion beginning to clear'),
 ('The Sun', 'joy, openness and renewed energy', 'temporary clouds over your confidence'),
 ('Judgement', 'honest reflection and a fresh calling', 'harsh self-criticism or avoiding reflection'),
 ('The World', 'completion and a sense of belonging', 'unfinished details needing patient attention'),
]
GUIDANCE = {
 'Love': 'Consider how this affects mutual care, boundaries and honest communication.',
 'Career': 'Reflect on your work, learning goals and one achievable next step.',
 'Money': 'Reflect on your spending habits, priorities and practical plans.',
 'Family': 'Consider the balance between caring for family and respecting your own needs.',
 'Growth': 'Notice what you are learning and which small habit could support you.',
 'Friendship': 'Think about reciprocity, trust and making space for connection.',
 'A Big Decision': 'Compare your options against your values and the information you still need.',
 'General': 'Notice where this theme appears in your daily life and what is within your control.',
}
POSITIONS = ['Past', 'Present', 'Future']
ARCANA_ANIMALS = {
 'The Fool':'Rabbit','The Magician':'Fox','The High Priestess':'Owl',
 'The Empress':'Deer','The Emperor':'Lion','The Hierophant':'Tortoise',
 'The Lovers':'Swans','The Chariot':'Horse','Strength':'Bear',
 'The Hermit':'Hedgehog','Wheel of Fortune':'Hamster','Justice':'Wolf',
 'The Hanged Man':'Sloth','Death':'Butterfly','Temperance':'Otter',
 'The Devil':'Goat','The Tower':'Squirrel','The Star':'Moon Rabbit',
 'The Moon':'Black Cat','The Sun':'Chick','Judgement':'Dove','The World':'Whale'}

def draw_reading(intention='General', question='', rng=None):
    if intention not in INTENTIONS:
        raise ValueError('Choose a valid intention.')
    rng = rng or random.SystemRandom()
    question=question.strip()[:500]
    cards = []
    for position, (name, upright, reversed_meaning) in zip(POSITIONS, rng.sample(CARD_DATA, 3)):
        reverse = rng.choice([False, True])
        meaning = reversed_meaning if reverse else upright
        cards.append(dict(name=name, animal=ARCANA_ANIMALS.get(name, 'Garden Spirit'), position=position, artwork_seed=str(uuid4()), orientation='Reversed' if reverse else 'Upright',
                          meaning=meaning.capitalize() + '.', keywords=meaning.replace(' and ', ', ').split(', '),
                          guidance=(f"For {intention.lower()}, {name} invites you to notice {meaning}. "
                                    +GUIDANCE[intention]+(f' With “{question}” in mind, what small choice would support you?' if question else '')),
                          context={'Past': f'In the past, {meaning} may have shaped your {intention.lower()} journey.',
                                   'Present': f'Right now, notice where {meaning} appears in your {intention.lower()} choices.',
                                   'Future': f'Looking ahead, reflect on {meaning} in {intention.lower()}; this is a possibility to explore.'}[position]))
    return dict(id=str(uuid4()), date=datetime.now().astimezone().isoformat(timespec='seconds'),
                intention=intention, question=question.strip()[:500], cards=cards, note='')

def overall(reading):
    if reading.get('interpretation'):return reading['interpretation']
    a, b, c = reading['cards']
    return (f"Your journey moves from {a['meaning'].lower().rstrip('.')} through "
            f"{b['meaning'].lower().rstrip('.')} toward {c['meaning'].lower()} "
            f"{GUIDANCE[reading['intention']]} Be gentle with yourself: the next step is yours to choose.")

class Store:
    """Both interfaces use the same data folder; a custom folder helps testing."""
    def __init__(self, directory=None):
        self.directory = Path(directory or os.environ.get('VEIL_DATA_DIR', Path(__file__).parent / 'data'))
        self.directory.mkdir(parents=True, exist_ok=True)
        self.path = self.directory / 'moon_diary.json'
        self.data = {'settings': {'selected_background': None, 'hat': 'Star', 'buddy': 'Cat', 'accessory': 'Bow', 'name': 'Lumi', 'speed': 'Normal'}, 'readings': []}
        if self.path.exists():
            try:
                loaded = json.loads(self.path.read_text(encoding='utf-8'))
                if not isinstance(loaded, dict) or not isinstance(loaded.get('settings'), dict) or not isinstance(loaded.get('readings'), list):
                    raise ValueError('Invalid diary structure')
                for r in loaded['readings']:
                    if not all(k in r for k in ('id', 'date', 'intention', 'cards', 'note')) or len(r['cards']) != 3:
                        raise ValueError('Invalid reading')
                    if any(not all(k in c for k in ('name','position','orientation','meaning','guidance','context','keywords')) for c in r['cards']):
                        raise ValueError('Invalid card')
                self.data['settings'].update(loaded['settings'])
                self.data['readings'] = loaded['readings']
                settings=self.data['settings']
                choices=dict(settings.get('selection_choices',{}))
                if 'selected_background' not in loaded['settings']:
                    old=loaded['settings'].get('background',choices.get('background'))
                    settings['selected_background']=old if old in ('Day','Sunset','Night') else None
                migrate=any(k in settings for k in ('theme','background')) or any(k in choices for k in ('themes','background','selected_background'))
                settings.pop('theme',None);settings.pop('background',None)
                for key in ('themes','background','selected_background'):choices.pop(key,None)
                settings['selection_choices']=choices
                if migrate:self.write()
            except (ValueError, TypeError, KeyError) as exc:
                raise ValueError(f'Cannot read {self.path}. Your file has been preserved; rename it to keep a backup before restarting.') from exc
    def write(self):
        temporary = self.path.with_suffix('.tmp')
        temporary.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding='utf-8')
        temporary.replace(self.path)
    def save(self, reading, note=''):
        cards=reading.get('cards',[])
        if len(cards)!=3 or len({c.get('name') for c in cards})!=3:
            raise ValueError('Choose three different cards before saving.')
        if any(c.get('orientation') not in ('Upright','Reversed') for c in cards):
            raise ValueError('Each card needs an orientation before saving.')
        reading = dict(reading, note=note[:4000],interpretation=overall(reading),
                       step=reading.get('step',''),followup_status=reading.get('followup_status',''),
                       reflection=reading.get('reflection',''))
        self.data['readings'] = [r for r in self.data['readings'] if r['id'] != reading['id']]
        self.data['readings'].insert(0, reading)
        self.data['readings'].sort(key=lambda entry:entry['date'],reverse=True)
        self.write()
    def settings(self, **changes):
        self.data['settings'].update(changes)
        self.write()

"""Reference-art desktop interface. Only Python's standard library is needed.

The embedded reference is used as a sprite sheet. Canvas hit regions make its
painted controls interactive; live readings and diary entries replace sample text.
Coordinates below are in the ORIGINAL reference image, which makes the layout
straightforward to compare with the design.
"""
import base64
import math
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox
import wave

# The build script substitutes this constant in the standalone distribution.
ART_DATA = None
LUMI_DATA = None
ART_PATH = Path(__file__).parent / 'reference.png'
ORACLE_OPTIONS = {
    'Hats': ('hat', ['Star','Flowers','Frog','Bow','Cat','Moon','Rose','Ice']),
    'Buddies': ('buddy', ['Cat','Bunny','Frog','None']),
    'Accessories': ('accessory', ['Bow','Flowers','Crystal','None']),
    'Backgrounds': ('selected_background', ['Day','Sunset','Night']),
}

SCREENS = {
    'intro': (20, 16, 301, 482),
    'oracle': (324, 16, 612, 482),
    'intention': (627, 16, 912, 482),
    'draw': (929, 16, 1217, 482),
    'revealed': (1233, 16, 1522, 482),
    'meaning': (20, 520, 313, 947),
    'reading': (325, 520, 660, 947),
    'save': (674, 520, 948, 947),
    'diary': (958, 520, 1255, 947),
    'settings': (1267, 520, 1522, 947),
    'reflect': (0,0,280,460),
    'followup': (0,0,280,460),
}
INK = '#10149a'
PAPER = '#fff7f4'
PINK = '#ffe5f3'
LILAC = '#e8dcff'
CARD_ART = [(1248, 101, 1331, 260), (1341, 101, 1425, 260), (1432, 101, 1515, 260)]


class Sound:
    """Tiny locally generated music loop and chime, with native audio players."""
    def __init__(self):
        self.temp = tempfile.TemporaryDirectory(prefix='veil-audio-')
        self.player = None
        self.effects = []
        self.enabled = False
        self.available = sys.platform == 'win32' or bool(shutil.which('afplay') or shutil.which('aplay') or shutil.which('paplay'))
        supplied_music = Path(__file__).with_name('assets') / 'music' / 'cosmic_lofi_voyage.mp3'
        self.music = supplied_music if supplied_music.exists() else Path(self.temp.name) / 'moon.wav'
        self.chime = Path(self.temp.name) / 'chime.wav'
        # A soft, slow pentatonic lullaby keeps the garden atmosphere gentle
        # while the shuffle/reveal effects remain distinct and audible.
        if self.music.suffix != '.mp3':
            self.make_wave(self.music, [220.00, 261.63, 329.63, 392.00,
                                        329.63, 293.66, 261.63, 196.00], 1.45)
        self.make_wave(self.chime, [659.25, 880], .13)
        sound_dir=Path(__file__).with_name('assets')/'sounds'
        self.event_sounds={name:sound_dir/(name+'.wav') for name in
            ('ui_click','select_crystal','card_flip','card_reveal','save_chime','page_turn','toggle')}
        self.event_sounds.update(reveal=self.event_sounds['card_reveal'],save=self.event_sounds['save_chime'],shuffle=self.event_sounds['card_flip'])

    def make_wave(self, path, notes, duration):
        rate = 16000
        frames = bytearray()
        for frequency in notes:
            for i in range(int(rate * duration)):
                t = i / rate
                envelope = min(1, t / .025) * max(0, 1 - t / duration) ** 2
                value = int(2700 * envelope * (math.sin(2 * math.pi * frequency * t) + .2 * math.sin(4 * math.pi * frequency * t)))
                frames.extend(struct.pack('<h', value))
        with wave.open(str(path), 'wb') as output:
            output.setnchannels(1)
            output.setsampwidth(2)
            output.setframerate(rate)
            output.writeframes(frames)

    def play_file(self, path):
        command = shutil.which('afplay') or shutil.which('aplay') or shutil.which('paplay')
        if command:
            try:
                return subprocess.Popen([command, str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except OSError:
                self.available = False
                self.enabled = False
        return None

    def set_music(self, enabled):
        self.enabled = enabled
        if sys.platform == 'win32':
            import winsound
            winsound.PlaySound(str(self.music) if enabled else None,
                               winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP if enabled else 0)
        elif not enabled and self.player:
            self.player.terminate()
            self.player.wait()
            self.player = None
        self.tick()

    def tick(self):
        self.effects = [p for p in self.effects if p.poll() is None]
        if self.player is not None and self.player.poll() not in (None, 0):
            self.enabled = False
        if self.enabled and sys.platform != 'win32' and self.available:
            if self.player is None or self.player.poll() is not None:
                self.player = self.play_file(self.music)

    def click(self):
        self.effect('ui_click')

    def stop_effects(self):
        for process in self.effects:
            if process.poll() is None:process.terminate()
        self.effects=[]

    def effect(self,name):
        path=self.event_sounds.get(name,self.chime)
        if not path.is_file():return
        process=self.play_file(path)
        if process:self.effects.append(process)

    def close(self):
        self.set_music(False)
        for process in self.effects:
            if process.poll() is None:
                process.terminate()
            process.wait()
        self.temp.cleanup()


from wardrobe import WardrobeMixin, OPTIONS
ORACLE_OPTIONS = OPTIONS

class ReferenceApp(WardrobeMixin):
    def __init__(self, root, store, audio=True):
        self.root, self.store = root, store
        from typography import setup
        self.font_family = setup(root)
        self.root.title('Veil & Vision')
        self.root.resizable(False, False)
        # Provisional drawing bounds only; fit_window measures all pages
        # before mapping the content frame and setting root geometry once.
        from page_frame import APP_WIDTH, APP_HEIGHT
        self.desktop_viewport = (APP_WIDTH,APP_HEIGHT)
        self.reference_viewport = self.desktop_viewport
        self.rendered_size = self.desktop_viewport
        self.resize_timer = None
        # Keep a normal managed window so macOS/Windows route real mouse
        # and keyboard events reliably to the primary controls.
        self.root.overrideredirect(False)
        self.drag_origin = None
        self.root.configure(bg='#d4d3ff')
        self.root.protocol('WM_DELETE_WINDOW', self.close)
        self.root.report_callback_exception = self.callback_error
        self.source = tk.PhotoImage(data=ART_DATA) if ART_DATA else tk.PhotoImage(file=str(ART_PATH))
        self.cache = {}
        self.images = []
        self.widgets = []
        self.hits = []
        self.focus_index = -1
        self.focus_rect = None
        self.timer = None
        self.typing_timers = []
        self.screen = 'intro'
        self.board_mode = False
        self.intro_trace = True
        self.oracle_trace = False
        self.intention_trace = False
        self.draw_trace = False
        self.revealed_trace = False
        self.meaning_trace = False
        self.reading_trace = False
        self.reflect_trace = False
        self.save_trace = False
        self.diary_trace = False
        self.followup_trace = False
        self.settings_trace = False
        self.category = 'Hats'
        self.intention = 'General'
        self.question = tk.StringVar(root)
        self.note = ''
        self.reading = None
        self.chosen = set()
        self.card_index = 0
        self.meaning_tab = 'Meaning'
        self.page = 0
        self.message = ''
        self.scale = 1.5 if root.winfo_screenheight() < 1080 else 2
        for key, value in dict(music=False, sound=False, text_speed=50, selected_background=None, accessory='Bow', buddy='Cat', hat='Star').items():
            self.store.data['settings'].setdefault(key, value)
        # Upgrade older rough costumes to the reference Lumi once. Keep diary,
        # oracle name, theme, audio and subsequent customization choices.
        if self.settings.get('avatar_version', 0) < 2:
            self.store.settings(hat='Star', buddy='Cat', accessory='Bow', avatar_version=2)
        if self.settings.get('oracle_layout_version', 0) < 1:
            # This appearance update restores the requested reference costume
            # once; saved readings and later customization remain intact.
            self.store.settings(hat='Star',buddy='Cat',accessory='Bow',oracle_layout_version=1)
        from interactive_canvas import InteractiveCanvas
        self.content_frame=tk.Frame(root,width=APP_WIDTH,height=APP_HEIGHT,borderwidth=0,highlightthickness=0,bg='#d4d3ff')
        self.content_frame.pack_propagate(False)
        self.content_frame.grid_propagate(False)
        self.canvas = InteractiveCanvas(self.content_frame,width=APP_WIDTH,height=APP_HEIGHT,highlightthickness=0,borderwidth=0,bg='#d4d3ff')
        self.canvas.place(x=0,y=0,width=APP_WIDTH,height=APP_HEIGHT)
        # The painted frame is the whole window; navigation lives in its
        # title menu rather than adding bars that are absent from the picture.
        self.status = tk.StringVar(root, 'A little guidance for a brighter you ♡')
        self.menu = tk.Menu(root, tearoff=False)
        for label, action in [('Back (Esc)', self.back), ('Home', lambda:self.go('intro')),
                              ('Moon Diary', lambda:self.go('diary')), ('Settings', lambda:self.go('settings'))]:
            self.menu.add_command(label=label,command=action)
        self.menu.add_separator()
        self.menu.add_command(label='Show full 12-screen board',command=self.show_board)
        self.menu.add_command(label='Close',command=self.close)
        self.canvas.bind('<Button-3>',self.popup_menu)
        self.canvas.bind('<B1-Motion>',self.drag_window)
        self.canvas.bind('<ButtonRelease-1>',lambda e:setattr(self,'drag_origin',None))
        self.root.bind('<Return>',self.advance_from_keyboard)
        self.canvas.bind('<Motion>', self.hover, add='+')
        from diary_trace import turn_page
        self.canvas.bind('<MouseWheel>',lambda e:turn_page(self,1 if e.delta<0 else -1))
        self.canvas.bind('<Next>',lambda e:turn_page(self,1))
        self.canvas.bind('<Prior>',lambda e:turn_page(self,-1))
        self.canvas.bind('<Button-1>', self.click)
        self.root.bind('<Escape>', lambda e: self.back())
        self.canvas.bind('<Tab>', self.next_focus)
        self.canvas.bind('<Return>', self.activate_focus)
        try:
            self.sound = Sound() if audio else None
        except (OSError, RuntimeError):
            self.sound = None
        if self.sound and self.settings['music']:
            self.sound.set_music(True)
        self.audio_timer = self.root.after(500, self.audio_tick)
        from content_layout import fit_window
        fit_window(self)

    def set_window_size(self, width, height):
        """Compatibility hook: presentation dimensions are locked at startup."""
        return self.reference_viewport

    def show_board(self):
        """Return to the fitted landscape reference board."""
        self.board_mode = True
        self.intro_trace = False
        self.oracle_trace = False
        self.intention_trace = False
        self.draw_trace = False
        self.revealed_trace = False
        self.meaning_trace = False
        self.reading_trace = False
        self.reflect_trace = False
        self.save_trace = False
        self.diary_trace = False
        self.followup_trace = False
        self.settings_trace = False
        self.desktop_viewport = self.reference_viewport
        self.render()

    def open_live_screen(self, screen):
        """Open a board panel in the existing interactive renderer."""
        self.board_mode = False
        self.intro_trace = screen == 'intro'
        self.oracle_trace = screen == 'oracle'
        self.intention_trace = screen == 'intention'
        self.draw_trace = screen == 'draw'
        self.revealed_trace = screen == 'revealed'
        self.meaning_trace = screen == 'meaning'
        self.reading_trace = screen == 'reading'
        self.reflect_trace = screen == 'reflect'
        self.save_trace = screen == 'save'
        self.diary_trace = screen == 'diary'
        self.followup_trace = screen == 'followup'
        self.settings_trace = screen == 'settings'
        self.desktop_viewport = self.reference_viewport
        self.rendered_size = self.reference_viewport
        self.screen = screen
        self.render()

    def desktop_resize(self, event):
        if getattr(self, '_drawing_compact', False):
            return
        if event.widget is not self.root or not hasattr(self, 'canvas'):
            return
        size = (event.width, event.height)
        # Never redraw into a viewport smaller than the approved reference
        # window; this prevents title bars, buttons, and artwork being clipped.
        if hasattr(self, 'reference_viewport'):
            size = (max(size[0], self.reference_viewport[0]),
                    max(size[1], self.reference_viewport[1]))
        if self.resize_timer:
            self.root.after_cancel(self.resize_timer)
            self.resize_timer=None
        if size == getattr(self, 'rendered_size', None) or min(size) < 200:
            return
        def redraw():
            self.resize_timer = None
            self.desktop_viewport = size
            self.render()
        self.resize_timer = self.root.after(180, redraw)

    @property
    def settings(self):
        return self.store.data['settings']

    def callback_error(self, kind, value, tb):
        import traceback
        try:
            with (self.store.directory / 'error.log').open('a', encoding='utf-8') as log:
                traceback.print_exception(kind, value, tb, file=log)
        except OSError:
            pass
        messagebox.showerror('Veil & Vision',
            'That action could not finish. Your saved diary is safe.\n'
            'Please try again. Details are recorded in data/error.log.', parent=self.root)

    def audio_tick(self):
        if self.sound:
            self.sound.tick()
        self.audio_timer = self.root.after(1000, self.audio_tick)

    def close(self):
        if getattr(self,'magic',None):self.magic.dispose()
        for effect in getattr(self,'card_effects',[]):
            effect.dispose()
        if self.timer:
            self.root.after_cancel(self.timer)
        self.root.after_cancel(self.audio_timer)
        for timer in self.typing_timers:
            self.root.after_cancel(timer)
        if self.sound:
            self.sound.close()
        self.root.destroy()

    def zoom(self, delta):
        self.capture_note()
        self.desktop_viewport = None
        self.scale = max(1, min(2.5, self.scale + delta))
        self.render()

    def xy(self, x, y):
        left, top, _, _ = SCREENS[self.screen]
        return (x - left) * self.scale, (y - top) * self.scale

    def crop(self, box):
        key = ('crop', tuple(box))
        if key not in self.cache:
            x1, y1, x2, y2 = box
            photo = tk.PhotoImage(width=x2-x1, height=y2-y1)
            photo.tk.call(str(photo), 'copy', str(self.source), '-from', x1, y1, x2, y2, '-to', 0, 0)
            self.cache[key] = photo
        return self.cache[key]

    def resized(self, photo, width, height, key):
        """Nearest-neighbour sprite scaling using Tk alone (no Pillow)."""
        cache_key = ('size', key, width, height)
        if cache_key not in self.cache:
            out = tk.PhotoImage(width=width, height=height)
            sw, sh = photo.width(), photo.height()
            # Copy whole columns and rows inside Tk. This preserves exact
            # nearest-neighbour sampling and alpha without per-pixel Tcl calls.
            horizontal = tk.PhotoImage(width=width, height=sh)
            for x in range(width):
                sx = min(sw - 1, x * sw // width)
                horizontal.tk.call(str(horizontal), 'copy', str(photo),
                    '-from', sx, 0, sx + 1, sh, '-to', x, 0)
            for y in range(height):
                sy = min(sh - 1, y * sh // height)
                out.tk.call(str(out), 'copy', str(horizontal),
                    '-from', 0, sy, width, sy + 1, '-to', 0, y)
            self.cache[cache_key] = out
        return self.cache[cache_key]

    def art(self, box, x=None, y=None, size=None):
        photo = self.crop(box)
        if size:
            photo = self.resized(photo, size[0], size[1], tuple(box))
        # All display zoom factors are exact half steps.
        key = ('zoom', str(photo), self.scale)
        if key not in self.cache:
            self.cache[key] = photo.zoom(int(self.scale*2)).subsample(2)
        photo = self.cache[key]
        self.images.append(photo)
        px, py = self.xy(box[0] if x is None else x, box[1] if y is None else y)
        self.canvas.create_image(px, py, image=photo, anchor='nw')

    def rect(self, box, fill=PAPER, outline=''):
        x1, y1 = self.xy(box[0], box[1])
        x2, y2 = self.xy(box[2], box[3])
        return self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=outline, width=max(1, self.scale))

    def text(self, x, y, text, size=8, width=240, anchor='nw', color=INK, bold=False):
        px, py = self.xy(x, y)
        return self.canvas.create_text(px, py, text=text, anchor=anchor, fill=color,
            font=(self.font_family, -round(size*self.scale), 'bold' if bold else 'normal'),
            width=width*self.scale, justify='left' if anchor=='nw' else 'center')

    def hit(self, box, label, action):
        self.hits.append((box, label, action))

    def popup_menu(self, event=None):
        x = event.x_root if event else self.root.winfo_rootx()+15
        y = event.y_root if event else self.root.winfo_rooty()+35
        try:
            self.menu.tk_popup(x,y)
        finally:
            self.menu.grab_release()

    def minimize(self):
        self.root.overrideredirect(False)
        self.root.iconify()

    def restore_frame(self,event):
        # Restoring the app must not replace its native window or drop focus.
        if event.widget is self.root and self.root.state()=='normal':
            self.root.after_idle(self.canvas.focus_set)

    def drag_window(self,event):
        if self.drag_origin:
            dx,dy,left,top=self.drag_origin
            self.root.geometry(f'+{max(0,left+event.x_root-dx)}+{max(0,top+event.y_root-dy)}')

    def hover(self, event):
        if getattr(self, self.screen + '_trace', False):
            self.canvas.configure(cursor='hand2' if self.canvas.region_at(event) is not None else '')
            return
        x, y = self.to_source(event)
        hit = self.find_hit(x, y)
        self.canvas.configure(cursor='hand2' if hit else '')
        self.status.set(hit[1] if hit else self.message or 'A little guidance for a brighter you ♡')

    def to_source(self, event):
        left, top, _, _ = SCREENS[self.screen]
        return event.x/self.scale + left, event.y/self.scale + top

    def find_hit(self, x, y):
        return next((h for h in reversed(self.hits) if h[0][0] <= x <= h[0][2] and h[0][1] <= y <= h[0][3]), None)

    def click(self, event):
        # Canvas item bindings run before the canvas widget binding. A
        # navigation action must not reuse this press on the newly drawn page.
        if getattr(self, '_action_pending', False):
            return 'break'
        if getattr(self.canvas, 'dispatch_region', lambda event: False)(event):
            return 'break'
        if getattr(self, self.screen + '_trace', False):
            # Registered regions are the source of truth for the painted UI.
            # Do not reuse coordinates from a different reference below.
            return 'break'
        # Traced reference screens use canvas image hit regions. Handle these
        # before the legacy artwork coordinate map so navigation is reliable.
        if getattr(self, 'intro_trace', False) and self.screen == 'intro':
            width, height = self.desktop_viewport
            fit=min(width/371, height/345)
            ox,oy=(width-round(371*fit))//2,(height-round(345*fit))//2
            x,y=(event.x-ox)/fit,(event.y-oy)/fit
            if 84 <= x <= 303:
                if 214 <= y <= 244: self.run_action(lambda:self.go('oracle')); return 'break'
                if 250 <= y <= 278: self.run_action(lambda:self.go('diary')); return 'break'
                if 283 <= y <= 312: self.run_action(lambda:self.go('settings')); return 'break'
        if getattr(self, 'oracle_trace', False) and self.screen == 'oracle':
            width, height = self.desktop_viewport
            fit=min(width/338, height/345)
            ox,oy=(width-round(338*fit))//2,(height-round(345*fit))//2
            x,y=(event.x-ox)/fit,(event.y-oy)/fit
            if 166 <= y <= 188 and 44 <= x <= 364:
                index=max(0,min(3,int((x-44)//80)))
                self.run_action(lambda:self.set_category(['Hats','Buddies','Accessories','Backgrounds'][index])); return 'break'
            if 193 <= y <= 309 and 43 <= x <= 279:
                index=(int((x-43)//80)+3*int((y-193)//60))
                from wardrobe import OPTIONS
                key, choices=OPTIONS.get(self.category, ('hat', []))
                if 0 <= index < min(6,len(choices)):
                    self.run_action(lambda key=key,choice=choices[index]:self.change(**{key:choice})); return 'break'
            if 315 <= y <= 340 and 80 <= x <= 258:
                self.run_action(lambda:self.go('intention')); return 'break'
        if getattr(self, 'intention_trace', False) and self.screen == 'intention':
            width, height = self.desktop_viewport
            fit=min(width/355, height/345)
            ox,oy=(width-round(355*fit))//2,(height-round(345*fit))//2
            x,y=(event.x-ox)/fit,(event.y-oy)/fit
            if 69 <= y <= 212 and 16 <= x <= 337:
                col=max(0,min(3,int((x-16)//81)))
                row=0 if y < 144 else 1
                self.run_action(lambda: self.select_intention(['Love','Career','Money','Family','Growth','Friendship','A Big Decision','General'][row*4+col])); return 'break'
            if 224 <= y <= 258 and 16 <= x <= 337:
                from intention_trace import _edit_question
                self.run_action(lambda:_edit_question(self)); return 'break'
            if 286 <= y <= 315 and 75 <= x <= 280:
                self.run_action(self.begin); return 'break'
        if getattr(self, 'draw_trace', False) and self.screen == 'draw':
            width, height = self.desktop_viewport
            fit=min(width/355, height/345)
            ox,oy=(width-round(355*fit))//2,(height-round(345*fit))//2
            x,y=(event.x-ox)/fit,(event.y-oy)/fit
            boxes=[(24,83,111,198),(116,83,203,198),(210,83,297,198)]
            for i,(left,top,right,bottom) in enumerate(boxes):
                if left <= x <= right and top <= y <= bottom:
                    self.run_action(lambda i=i:self.pick(i)); return 'break'
        if getattr(self, 'revealed_trace', False) and self.screen == 'revealed':
            width,height=self.desktop_viewport; fit=min(width/371,height/312); ox,oy=(width-round(371*fit))//2,(height-round(312*fit))//2
            x,y=(event.x-ox)/fit,(event.y-oy)/fit
            boxes=[(38,50,130,165),(145,50,233,165),(247,50,336,165)]
            for i,(left,top,right,bottom) in enumerate(boxes):
                if left<=x<=right and top<=y<=bottom:
                    self.run_action(lambda i=i:self.open_card(i)); return 'break'
            if 166<=x<=352 and 276<=y<=306:
                self.run_action(lambda:self.go('reading')); return 'break'
        if getattr(self, 'meaning_trace', False) and self.screen == 'meaning':
            width,height=self.desktop_viewport; fit=min(width/338,height/312); ox,oy=(width-round(338*fit))//2,(height-round(312*fit))//2
            x,y=(event.x-ox)/fit,(event.y-oy)/fit
            if 140<=x<=326 and 78<=y<=131:
                col=0 if x<234 else 1; row=0 if y<108 else 1
                self.run_action(lambda:self._set_meaning_tab(['Meaning','Position','My Question','Keywords'][row*2+col])); return 'break'
            if 80<=x<=258 and 275<=y<=304:
                self.run_action(lambda:self.go('revealed')); return 'break'
        if getattr(self, 'reading_trace', False) and self.screen == 'reading':
            width,height=self.desktop_viewport; fit=min(width/355,height/312); ox,oy=(width-round(355*fit))//2,(height-round(312*fit))//2
            x,y=(event.x-ox)/fit,(event.y-oy)/fit
            if 34<=x<=185 and 270<=y<=300:
                self.run_action(lambda:self.go('reflect')); return 'break'
            if 191<=x<=322 and 270<=y<=300:
                self.run_action(self.save); return 'break'
        if getattr(self, 'reflect_trace', False) and self.screen == 'reflect':
            width,height=self.desktop_viewport; fit=min(width/355,height/312); ox,oy=(width-round(355*fit))//2,(height-round(312*fit))//2
            x,y=(event.x-ox)/fit,(event.y-oy)/fit
            from reflect_trace import STEPS,_custom
            if 18<=x<=337 and 70<=y<=206:
                index=min(2,max(0,int((y-70)//48))); self.run_action(lambda:self._choose_reflect_step(STEPS[index])); return 'break'
            if 18<=x<=337 and 218<=y<=244:
                self.run_action(lambda:_custom(self)); return 'break'
            if 37<=x<=318 and 253<=y<=284:
                self.run_action(self.save_and_show_confirmation); return 'break'
            if 95<=x<=260 and 287<=y<=308:
                self.run_action(self.save_and_show_confirmation); return 'break'
        if getattr(self, 'save_trace', False) and self.screen == 'save':
            width,height=self.desktop_viewport; fit=min(width/362,height/260); ox,oy=(width-round(362*fit))//2,(height-round(260*fit))//2
            x,y=(event.x-ox)/fit,(event.y-oy)/fit
            if 37<=x<=180 and 224<=y<=248:
                self.run_action(lambda:self.go('intro')); return 'break'
            if 181<=x<=344 and 224<=y<=248:
                self.run_action(lambda:self.go('diary')); return 'break'
        if getattr(self, 'diary_trace', False) and self.screen == 'diary':
            width,height=self.desktop_viewport; fit=min(width/353,height/260); ox,oy=(width-round(353*fit))//2,(height-round(260*fit))//2
            x,y=(event.x-ox)/fit,(event.y-oy)/fit
            entries=list(reversed(self.store.data.get('readings',[])))
            if 18<=x<=336 and 54<=y<=218:
                index=min(3,max(0,int((y-54)//41)))
                if index<len(entries):
                    from diary_trace import _open_entry
                    self.run_action(lambda reading=entries[index]:_open_entry(self,reading)); return 'break'
            if 18<=x<=177 and 226<=y<=249:
                self.run_action(lambda:self.go('intention')); return 'break'
            if 181<=x<=336 and 226<=y<=249:
                self.run_action(self.clear_diary); return 'break'
        if getattr(self, 'followup_trace', False) and self.screen == 'followup':
            width,height=self.desktop_viewport; fit=min(width/355,height/260); ox,oy=(width-round(355*fit))//2,(height-round(260*fit))//2
            x,y=(event.x-ox)/fit,(event.y-oy)/fit
            from followup_trace import STATUSES,_choose,_save
            if 36<=x<=319 and 102<=y<=195:
                index=min(2,max(0,int((y-102)//31))); self.run_action(lambda:_choose(self,STATUSES[index])); return 'break'
            if 35<=x<=319 and 226<=y<=248:
                self.run_action(lambda:_save(self)); return 'break'
            if 95<=x<=260 and 248<=y<=260:
                self.run_action(lambda:self.go('diary')); return 'break'
        if getattr(self, 'settings_trace', False) and self.screen == 'settings':
            width,height=self.desktop_viewport; fit=min(width/356,height/260); ox,oy=(width-round(356*fit))//2,(height-round(260*fit))//2
            x,y=(event.x-ox)/fit,(event.y-oy)/fit
            if 44<=x<=280 and 59<=y<=104:
                self.run_action(lambda:self.open_background(['Day','Sunset','Night'][min(2,max(0,int((x-44)//83)))])); return 'break'
            if 265<=x<=337 and 131<=y<=153:
                self.run_action(lambda:self.toggle('music')); return 'break'
            if 265<=x<=337 and 158<=y<=180:
                self.run_action(lambda:self.toggle('sound')); return 'break'
            if 95<=x<=282 and 181<=y<=205:
                self.run_action(lambda:self.set_text_speed(50 if self.settings.get('text_speed',50)>=90 else self.settings.get('text_speed',50)+10)); return 'break'
            if 39<=x<=170 and 211<=y<=232:
                self.run_action(self.about); return 'break'
            if 173<=x<=273 and 211<=y<=232:
                self.run_action(self.clear_diary); return 'break'
            if 276<=x<=348 and 211<=y<=232:
                self.run_action(self.reset); return 'break'
            if 103<=x<=250 and 237<=y<=258:
                self.run_action(lambda:self.go('intro')); return 'break'
        x,y=self.to_source(event)
        if SCREENS[self.screen][1]+4 <= y <= SCREENS[self.screen][1]+33:
            self.drag_origin=(event.x_root,event.y_root,self.root.winfo_x(),self.root.winfo_y())
        hit = self.find_hit(x,y)
        if hit:
            if self.sound and self.settings['sound']:
                self.sound.click()
            hit[2]()
            return 'break'

    def next_focus(self, event=None):
        if getattr(self.canvas,'region_callbacks',None):
            self.canvas.focus_next_region()
            return 'break'
        if not self.hits and getattr(self,'controls',None):
            next(iter(self.controls.values())).focus_set()
            return 'break'
        if self.hits:
            self.focus_index = (self.focus_index+1) % len(self.hits)
            if self.focus_rect:
                self.canvas.delete(self.focus_rect)
            box, label, _ = self.hits[self.focus_index]
            self.focus_rect = self.rect(box, '', '#7334c9')
            self.status.set(label + ' — press Enter')
        return 'break'

    def activate_focus(self, event=None):
        if getattr(self.canvas,'activate_region',lambda:False)():
            return 'break'
        if 0 <= self.focus_index < len(self.hits):
            self.hits[self.focus_index][2]()
        else:
            self.advance_from_keyboard()
        return 'break'

    def advance_from_keyboard(self,event=None):
        if event is not None and isinstance(event.widget,(tk.Text,tk.Button)):
            return
        action={'intro':self.new_reading,
                'oracle':lambda:self.go('intention'),
                'intention':self.begin}.get(self.screen)
        if action:
            self.run_action(action)
            return 'break'

    def capture_note(self):
        if self.screen == 'save' and getattr(self, 'note_widget', None):
            try:
                self.note = self.note_widget.get('1.0', 'end-1c')[:4000]
            except tk.TclError:
                pass

    def go(self, screen):
        if screen == 'followup' and not (self.reading or {}).get('step'):
            screen = 'reflect'
        self.capture_note()
        if self.resize_timer:
            self.root.after_cancel(self.resize_timer)
            self.resize_timer=None
        if self.timer:
            self.root.after_cancel(self.timer)
            self.timer = None
        self.board_mode = False
        self.intro_trace = screen == 'intro'
        self.oracle_trace = screen == 'oracle'
        self.intention_trace = screen == 'intention'
        self.draw_trace = screen == 'draw'
        self.revealed_trace = screen == 'revealed'
        self.meaning_trace = screen == 'meaning'
        self.reading_trace = screen == 'reading'
        self.reflect_trace = screen == 'reflect'
        self.save_trace = screen == 'save'
        self.diary_trace = screen == 'diary'
        self.followup_trace = screen == 'followup'
        self.settings_trace = screen == 'settings'
        self.screen = screen
        # All pages use the current viewport; navigation must not resize it.
        self.render()

    def back(self):
        previous = {'intro':'intro', 'oracle':'intro', 'intention':'oracle', 'draw':'intention',
                    'revealed':'intention', 'meaning':'revealed', 'reading':'revealed',
                    'save':'reading', 'diary':'intro', 'settings':'intro',
                    'reflect':'reading','followup':'diary'}
        self.go(previous[self.screen])

    def render(self):
        if getattr(self,'magic',None):self.magic.dispose()
        for effect in getattr(self,'card_effects',[]):
            effect.dispose()
        self.card_effects=[]
        self.card_animating=False
        self.selection_styles=[]
        for timer in self.typing_timers:
            self.root.after_cancel(timer)
        self.typing_timers = []
        for widget in self.widgets:
            widget.destroy()
        self.widgets, self.images, self.hits = [], [], []
        self.focus_index = -1
        self.focus_rect = None
        self.note_widget = None
        self.canvas.delete('all')
        from compact_ui import draw as draw_design
        if draw_design(self):
            if getattr(self,self.screen+'_trace',False):
                from trace_runtime import finish
                finish(self)
                from selection_style import connect
                connect(self)
                from magic_effects import mount
                mount(self)
            self.canvas.focus_set()
            return
        box = SCREENS[self.screen]
        width, height = (box[2]-box[0])*self.scale, (box[3]-box[1])*self.scale
        self.canvas.configure(width=round(width), height=round(height))
        self.art(box)
        # These painted window controls now operate the real application.
        self.hit((box[2]-30, box[1]+7, box[2]-7, box[1]+31), 'Close app', self.close)
        self.hit((box[2]-53, box[1]+7, box[2]-31, box[1]+31), 'Change zoom', lambda: self.zoom(-.5 if self.scale >= 2 else .5))
        self.hit((box[2]-77, box[1]+7, box[2]-54, box[1]+31), 'Minimize', self.minimize)
        self.hit((box[0]+5,box[1]+7,box[0]+31,box[1]+31),'Navigation menu',self.popup_menu)
        getattr(self, 'show_'+self.screen)()
        self.install_controls()
        self.status.set(self.message or 'A little guidance for a brighter you ♡')
        self.canvas.focus_set()

    def legacy_install_controls(self):
        """Use native Tk buttons: artwork is presentation, never the only control."""
        self.controls={}
        for index,(bounds,label,action) in enumerate(self.hits):
            box=bounds
            caption=None
            selected=False
            tile_icon=None
            custom_tile=False
            control_art=None
            toggle_state=None
            scene_arrow=None
            primary_label={'Start your journey':'☆  Start', 'Choose intention':'Next →', 'Draw three cards':'Next →'}.get(label)
            if self.screen=='revealed' and label.startswith('Read ') and label!='Read your overall message':
                card_index=next(i for i,c in enumerate(self.reading['cards']) if label=='Read '+c['name'])
                x=1251+card_index*89
                box=(x,295,x+80,328)
                card=self.reading['cards'][card_index]
                control_art=(1251,295,1331,328) if card['orientation']=='Upright' else (1340,295,1423,328)
            elif self.screen=='revealed' and label=='Read your overall message':
                # Both the full illustrated character and its speech bubble
                # are real buttons, with the original artwork kept intact.
                box=bounds
            elif self.screen=='reading' and label.startswith('Save this reading'):
                box=bounds
            elif self.screen=='diary' and label.startswith('Open saved '):
                box=(1210,bounds[1]+17,1235,bounds[1]+48)
                caption='›'
            elif self.screen=='diary' and 'diary page' in label:
                caption='‹ Previous' if 'Previous' in label else 'Next ›'
            elif self.screen=='settings' and ('music' in label or 'sound' in label):
                key='music' if 'music' in label else 'sound'
                y=702 if key=='music' else 735
                box=(1451,y,1498,y+24)
                toggle_state=bool(self.settings.get(key))
            elif self.screen=='oracle':
                if label in ('Previous style','Next style'):
                    scene_arrow=label
                if label=='Rename your oracle':
                    # The original name panel itself is a real image button.
                    # No added pencil or small white button obscures the art.
                    if self.settings.get('name','Lumi')!='Lumi':
                        caption='This is '+self.settings['name']+'!\nYour companion on this journey. ♡'
                elif label in ('Hats','Buddies','Accessories','Backgrounds'):
                    selected=label==self.category and self.category!='Hats'
                elif bounds[1]>=293 and bounds[3]<=392:
                    key={'Hats':'hat','Buddies':'buddy','Accessories':'accessory','Backgrounds':'selected_background'}[self.category]
                    selected=self.settings.get(key)==label and not (self.category=='Hats' and label=='Star')
                    if self.category!='Hats':
                        custom_tile=True
                        tile_icon={
                            'Cat':(345,349,385,383), 'Bunny':(1454,174,1498,232),
                            'Frog':(476,304,515,334), 'Bow':(540,303,582,335),
                            'Flowers':(404,300,456,336),
                            'Day':(1297,615,1347,660),
                            'Sunset':(1368,615,1418,660),
                            'Night':(1442,615,1491,660),
                        }.get(label)
                        caption='×' if label=='None' else None
            elif self.screen=='diary' and label=='Clear diary':
                control_art=(1294,850,1497,875)
            elif self.screen=='intention' and label in INTENTIONS:
                selected=label==self.intention
            elif self.screen=='draw' and label.startswith('Choose '):
                n=['Choose Past','Choose Present','Choose Future'].index(label)
                if n in self.chosen:
                    caption='✓'
                    selected=True
            elif self.screen=='settings' and label.endswith(' theme'):
                selected=label==(self.settings.get('selected_background') or '')+' theme'
            elif self.screen=='meaning' and label=='Explain card orientation':
                control_art=(164,706,247,732)
                caption=self.reading['cards'][self.card_index]['orientation']+(' ↓' if self.reading['cards'][self.card_index]['orientation']=='Reversed' else ' ↑')
            elif self.screen=='meaning' and label in ('Meaning','In This Position','For Your Question','Keywords'):
                selected=label==self.meaning_tab
            # Native controls receive mouse, keyboard and accessibility events
            # directly, independently of Canvas coordinate dispatch.
            photo=None
            if caption is None or custom_tile or toggle_state is not None or (self.screen=='draw' and label.startswith('Choose ')):
                key=('control',self.screen,tuple(box),self.scale,self.category if self.screen=='oracle' else '',label,tuple(self.settings.get(k) for k in ('selected_background','hat','accessory','buddy')) if scene_arrow else ())
                if key not in self.cache:
                    if scene_arrow:
                        arrow=self.scene_arrow(box,scene_arrow=='Previous style')
                        self.cache[key]=arrow.zoom(int(self.scale*2)).subsample(2)
                    elif toggle_state is not None:
                        toggle=self.switch_image(toggle_state)
                        self.cache[key]=toggle.zoom(int(self.scale*2)).subsample(2)
                    elif control_art:
                        sprite=self.crop(control_art)
                        sprite=self.resized(sprite,box[2]-box[0],box[3]-box[1],('control-art',control_art,box))
                        self.cache[key]=sprite.zoom(int(self.scale*2)).subsample(2)
                    elif custom_tile:
                        # Retain the original rounded tile border and use an
                        # illustrated option instead of a blank text rectangle.
                        tile=self.crop(box).copy()
                        if self.category=='Backgrounds':
                            tile=self.resized(self.crop((334,294,399,343)),box[2]-box[0],box[3]-box[1],'background-option-frame').copy()
                        tw,th=tile.width(),tile.height()
                        tile.put('#fff5fc',to=(3,3,tw-3,th-3))
                        if label=='Crystal':
                            sprite=self.crystal_sprite().zoom(2)
                            self.paste_layer(tile,sprite,(tw-sprite.width())//2,(th-sprite.height())//2)
                        if tile_icon:
                            sprite=self.crop(tile_icon)
                            ratio=min((tw-12)/sprite.width(),(th-8)/sprite.height())
                            iw,ih=max(1,int(sprite.width()*ratio)),max(1,int(sprite.height()*ratio))
                            sprite=self.resized(sprite,iw,ih,('option',tile_icon,iw,ih))
                            tile.tk.call(str(tile),'copy',str(sprite),'-to',(tw-iw)//2,(th-ih)//2)
                        self.cache[key]=tile.zoom(int(self.scale*2)).subsample(2)
                    elif self.screen=='oracle':
                        # Crop the already scaled panel: image-button pixels
                        # align with the background even at 150% display size.
                        panel=self.cache[('zoom',str(self.crop(SCREENS[self.screen])),self.scale)]
                        x,y=self.xy(box[0],box[1])
                        left,top=round(x),round(y)
                        width=round((box[2]-box[0])*self.scale)
                        height=round((box[3]-box[1])*self.scale)
                        image=tk.PhotoImage(width=width,height=height)
                        image.tk.call(str(image),'copy',str(panel),'-from',left,top,left+width,top+height,'-to',0,0)
                        self.cache[key]=image
                    else:
                        source=self.crop(box)
                        self.cache[key]=source.zoom(int(self.scale*2)).subsample(2)
                photo=self.cache[key]
                self.images.append(photo)
            # Start and Next remain native buttons, but their image is the
            # complete original painted button, including its lettering.
            button=tk.Button(self.canvas,command=lambda fn=action:self.run_action(fn),
                image=photo if photo else '',text=caption or '',compound='center',
                relief='flat',overrelief='flat',bd=0,padx=0,pady=0,
                bg='#bfe3ff' if selected else '#fff3fc',activebackground='#fff3fc',
                fg=INK,activeforeground=INK,cursor='hand2',takefocus=True,
                highlightthickness=0 if primary_label or self.screen=='oracle' else (1 if selected else 0),highlightbackground='#8656c8',
                highlightcolor='#8656c8',font=(self.font_family,-round((16 if primary_label else 9 if self.screen=='revealed' else 11)*self.scale),'bold' if primary_label else 'normal'),
                wraplength=max(10,round((box[2]-box[0]-4)*self.scale)))
            button.bind('<Return>',lambda event,b=button:(b.invoke(),'break')[1])
            x,y=self.xy(box[0],box[1])
            self.canvas.create_window(x,y,anchor='nw',window=button,
                width=round((box[2]-box[0])*self.scale),height=round((box[3]-box[1])*self.scale))
            self.widgets.append(button)
            self.controls[label]=button

    def switch_image(self, enabled):
        """A working switch that retains the pictured track-and-knob design."""
        image=tk.PhotoImage(width=47,height=24)
        image.put(PAPER,to=(0,0,47,24))
        for y in range(2,23):
            for x in range(2,46):
                cx=min(35,max(12,x))
                distance=(x-cx)**2+(y-12)**2
                if distance<=100:
                    color='#537eff' if enabled else '#c7c5db'
                    if distance>81:
                        color='#6667ca'
                    image.put(color,(x,y))
        center=35 if enabled else 12
        for y in range(3,22):
            for x in range(center-9,center+10):
                if (x-center)**2+(y-12)**2<=81:
                    image.put('#fff9ff',(x,y))
        return image

    def run_action(self, action):
        if getattr(self, '_action_pending', False):
            return
        self._action_pending = True
        self.root.after_idle(lambda: setattr(self, '_action_pending', False))
        from sound_events import snapshot,after_action
        before=snapshot(self);self._quiet_action=False
        action()
        after_action(self,before)
        from magic_effects import after_action as animate_action
        animate_action(self,before)

    def change(self, **values):
        if 'selected_background' in values:
            value=values.pop('selected_background')
            if values:self.store.settings(**values)
            self.select_background(value)
            return
        from selection_state import choose
        for key,value in values.items():
            if key in ("hat","buddy","accessory","selected_background"):choose(self,key,value)
        self.store.settings(**values)
        self.render()

    def show_intro(self):
        self.hit((56,359,265,402), 'Start your journey', lambda: self.go('oracle'))
        self.hit((56,405,265,447), 'Settings', lambda: self.go('settings'))

    def legacy_show_oracle(self):
        categories = [('Hats',330,386),('Buddies',386,452),('Accessories',452,528),('Backgrounds',528,603)]
        for category, left, right in categories:
            self.hit((left,256,right,287), category, lambda c=category:self.set_category(c))
            # Keep the painted tabs' original shapes and spacing.
        key,choices=ORACLE_OPTIONS[self.category]
        if self.category=='Backgrounds':
            self.rect((331,292,602,392),'#fff0f8')
        elif self.category!='Hats':
            # Keep all eight rounded slots and the floral panel. Unavailable
            # slots are visibly empty instead of looking like inert options.
            for row in range(2):
                for left,right in [(334,399),(399,465),(465,531),(531,599)]:
                    top=294 if row==0 else 344
                    self.rect((left+3,top+3,right-3,top+41),'#fff5fc')
        for i, choice in enumerate(choices):
            col, row = i%4, i//4
            columns=[(334,399),(399,465),(465,531),(531,599)]
            left,right=columns[col]
            top,bottom=(294,343) if row==0 else (344,392)
            if self.category=='Backgrounds':
                left,right=[(337,418),(425,506),(513,594)][i]
                top,bottom=303,365
                self.text((left+right)/2,379,choice,11,81,'center')
            box=(left,top,right,bottom)
            key = {'Hats':'hat','Buddies':'buddy','Accessories':'accessory','Backgrounds':'selected_background'}[self.category]
            self.hit(box, choice, lambda k=key,v=choice:self.change(**{k:v}))
            # The native image button supplies the selected option's artwork.
            # Selection is stored without painting over the original border.
        self.hit((353,174,382,217), 'Previous style', lambda:self.cycle_style(-1))
        self.hit((551,174,581,217), 'Next style', lambda:self.cycle_style(1))
        self.hit((379,438,552,474), 'Choose intention', lambda:self.go('intention'))
        # Always compose background, full cat, worn clothing and companion.
        self.costume_preview()
        # Preserve the exact painted lettering and rounded name panel.
        if self.settings.get('name','Lumi') != 'Lumi':
            self.rect((350,400,580,414), '#fff0f8')
            self.text(465,409,'This is '+self.settings['name']+'!',11,230,'center')
        self.hit((341,394,590,436),'Rename your oracle',self.rename)

    def sticker(self, box, polygon, key, tint=None):
        """Mask a sprite at display time; the embedded source stays untouched."""
        cache_key = ('sticker', key, tint)
        if cache_key in self.cache:
            return self.cache[cache_key]
        original = self.crop(box)
        image = original.copy()
        points = [(x-box[0],y-box[1]) for x,y in polygon]
        for y in range(image.height()):
            for x in range(image.width()):
                inside = False
                previous = len(points)-1
                for current in range(len(points)):
                    ax,ay = points[current]
                    bx,by = points[previous]
                    if (ay > y) != (by > y) and x < (bx-ax)*(y-ay)/(by-ay)+ax:
                        inside = not inside
                    previous = current
                if not inside:
                    image.transparency_set(x,y,True)
                elif tint:
                    r,g,b = original.get(x,y)
                    # Preserve the dark outline and warm gold stars.
                    if b > r and b > g and max(r,g,b)>90:
                        if tint == 'Ice':
                            rgb=(min(255,r+65),min(255,g+70),min(255,b+45))
                        elif tint == 'Rose':
                            rgb = (min(255,r+48),g,min(255,b+5))
                        else:
                            rgb = (r,min(255,g+22),min(255,b+20))
                        image.put('#%02x%02x%02x' % rgb,(x,y))
        self.cache[cache_key] = image
        return image

    def put_sticker(self,photo,x,y):
        if getattr(self, '_compose_only', False):
            return
        key=('zoom',str(photo),self.scale)
        if key not in self.cache:
            self.cache[key]=photo.zoom(int(self.scale*2)).subsample(2)
        image=self.cache[key]
        self.images.append(image)
        px,py=self.xy(x,y)
        self.canvas.create_image(px,py,image=image,anchor='nw')

    def icon_sprite(self, box, size=None):
        """Draw costume artwork without the pale rectangular tile behind it."""
        key=('transparent-icon',tuple(box))
        if key not in self.cache:
            original=self.crop(box)
            photo=original.copy()
            w,h=photo.width(),photo.height()
            # Flood only pale background connected to the edge. Enclosed light
            # pixels (eyes, petals, highlights) remain inside the dark outline.
            pending=[(x,0) for x in range(w)]+[(x,h-1) for x in range(w)]
            pending += [(0,y) for y in range(h)]+[(w-1,y) for y in range(h)]
            visited=set()
            while pending:
                px,py=pending.pop()
                if (px,py) in visited or not (0<=px<w and 0<=py<h):
                    continue
                visited.add((px,py))
                r,g,b=original.get(px,py)
                if r>=175 and g>=150 and b>=170:
                    photo.transparency_set(px,py,True)
                    pending.extend([(px-1,py),(px+1,py),(px,py-1),(px,py+1)])
            self.cache[key]=photo
        photo=self.cache[key]
        if size:
            photo=self.resized(photo,size[0],size[1],key)
        return photo

    def icon(self,box,x,y,size=None):
        self.put_sticker(self.icon_sprite(box,size),x,y)

    def reference_lumi(self, hat='Star'):
        """Use the same face, body, proportions and pixels as the oracle panel."""
        outline=[
            (398,193),(406,180),(421,168),(429,151),(441,134),(453,124),
            (467,124),(481,140),(488,150),(507,150),(515,157),(513,178),
            (504,186),(496,189),(501,203),(499,214),(491,224),
            (496,232),(497,244),(491,251),(477,251),(469,246),
            (460,251),(445,250),(436,246),(420,250),(412,243),
            (412,231),(418,222),(416,212),(422,205),(408,206),(399,201),
        ]
        photo=self.sticker((397,122,518,252),outline,'reference-lumi-complete')
        if hat in ('Star','Moon','Rose'):
            # The complete original image means no mismatched head/body seam.
            self.put_sticker(photo,397,122)
            if hat!='Star':
                hat_art=self.sticker((397,122,517,209),
                    [(397,194),(407,179),(422,167),(429,151),(441,134),
                     (453,124),(467,124),(482,143),(488,150),(508,150),
                     (515,157),(512,179),(503,187),(487,185),(475,191),
                     (449,199),(416,208),(403,203)],'reference-lumi-hat',hat)
                self.put_sticker(hat_art,397,122)
        else:
            # Alternate headwear uses the SAME oracle face/body, never the
            # differently posed cat from the Intro screen.
            body=self.sticker((411,176,503,252),
                [(423,193),(438,181),(458,177),(479,181),(494,191),
                 (501,203),(499,214),(491,224),(496,232),(497,244),
                 (491,251),(477,251),(469,246),(460,251),(445,250),
                 (436,246),(420,250),(412,243),(412,231),(418,222),
                 (416,212)],'reference-lumi-body')
            self.put_sticker(body,411,176)
            if hat!='None':
                icons={'Flowers':(404,300,456,336),'Frog':(476,304,515,334),
                       'Bow':(540,302,583,335),'Cat':(345,349,385,383)}
                self.icon(icons.get(hat,icons['Flowers']),435,163)

    def cat_layer(self):
        key='wearable-cat-layer'
        if key not in self.cache:
            # Keep the original Lumi artwork as the app's default character.
            # A replacement asset can remain in the folder without changing
            # the established visual identity or wardrobe composition.
            source=tk.PhotoImage(data=LUMI_DATA) if LUMI_DATA else tk.PhotoImage(file=str(Path(__file__).parent/'lumi_base.png'))
            image=self.resized(source,120,110,'wearable-cat-source').copy()
            # The generated sprite has a neutral checker backdrop. Remove
            # only edge-connected neutral pixels; the purple outline protects
            # Lumi's white face, body, ears, paws and tail inside the silhouette.
            pending=[(x,0) for x in range(120)]+[(x,109) for x in range(120)]
            pending += [(0,y) for y in range(110)]+[(119,y) for y in range(110)]
            visited=set()
            while pending:
                x,y=pending.pop()
                if (x,y) in visited or not (0<=x<120 and 0<=y<110):
                    continue
                visited.add((x,y))
                r,g,b=image.get(x,y)
                if image.transparency_get(x,y) or max(r,g,b)-min(r,g,b)<28:
                    image.transparency_set(x,y,True)
                    pending.extend([(x-1,y),(x+1,y),(x,y-1),(x,y+1)])
            self.cache[key]=image
        return self.cache[key]

    def paste_layer(self,target,image,x,y):
        # x/y are logical coordinates inside the preview, not window pixels.
        sx,sy=max(0,-x),max(0,-y)
        dx,dy=max(0,x),max(0,y)
        width=min(image.width()-sx,target.width()-dx)
        height=min(image.height()-sy,target.height()-dy)
        if width>0 and height>0:
            target.tk.call(str(target),'copy',str(image),'-from',sx,sy,sx+width,sy+height,'-to',dx,dy)

    def crystal_sprite(self):
        """A tiny rose-quartz heart charm shared by the outfit and option tile."""
        if 'heart-crystal' in self.cache:
            return self.cache['heart-crystal']
        gem=tk.PhotoImage(width=21,height=23)
        for i in range(9):
            gem.put('#b89bdc',(i+2,i//2))
            gem.put('#b89bdc',(18-i,i//2))
        # Stepped heart silhouette, faceted pink interior and pearl highlights.
        rows=[(5,8,12,15),(4,9,11,16),(3,17),(3,17),(3,17),
              (4,16),(5,15),(6,14),(7,13),(8,12),(9,11),(10,10)]
        pixels=set()
        for y,spans in enumerate(rows,6):
            for j in range(0,len(spans),2):
                for x in range(spans[j],spans[j+1]+1):pixels.add((x,y))
        for x,y in pixels:
            edge=any((x+dx,y+dy) not in pixels for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)])
            color='#9160ad' if edge else '#ffe0f5' if x<9 and y<12 else '#f5a8d9' if x<11 else '#d98dce'
            gem.put(color,(x,y))
        for x,y in [(6,8),(7,8),(6,9),(10,14)]:gem.put('#fff8ff',(x,y))
        for x,y in [(18,5),(17,6),(18,6),(19,6),(18,7),(2,16)]:gem.put('#fff0b8',(x,y))
        self.cache['heart-crystal']=gem
        return gem

    def legacy_costume_preview(self):
        background=self.settings.get('selected_background','Day')
        if background not in ('Day','Sunset','Night'):
            background='Day'
        swatches={'Day':(1297,615,1347,660),'Sunset':(1368,615,1418,660),'Night':(1442,615,1491,660)}
        scene=self.resized(self.crop(swatches[background]),222,129,('scene',background)).copy()
        # The same cat is always the base layer; no choice swaps its identity.
        self.paste_layer(scene,self.cat_layer(),40,23)
        hat=self.settings.get('hat','Star')
        if hat in ('Star','Moon','Rose','Ice'):
            image=self.sticker((397,122,517,209),
                [(397,194),(407,179),(422,167),(429,151),(441,134),(453,124),
                 (467,124),(482,143),(488,150),(508,150),(515,157),(512,179),
                 (503,187),(487,185),(475,191),(449,199),(416,208),(403,203)],
                'wearable-hat',None if hat=='Star' else hat)
            # Remove residual blue/green scenery caught at the old hat edge,
            # then fit the brim above the new cat's eyes, not across its face.
            hat_key=('fitted-hat',hat)
            if hat_key not in self.cache:
                clean=image.copy()
                for hy in range(clean.height()):
                    for hx in range(clean.width()):
                        r,g,b=clean.get(hx,hy)
                        if g>r*1.08 and g>b*.65:
                            clean.transparency_set(hx,hy,True)
                self.cache[hat_key]=self.resized(clean,92,67,hat_key)
            self.paste_layer(scene,self.cache[hat_key],60,8)
        elif hat!='None':
            specs={'Flowers':((404,300,456,336),(56,32),(72,40)),
                   'Frog':((476,304,515,334),(51,35),(77,32)),
                   'Bow':((540,303,582,335),(43,30),(80,39)),
                   'Cat':((345,349,385,383),(52,39),(74,31))}
            box,size,position=specs.get(hat,specs['Flowers'])
            self.paste_layer(scene,self.icon_sprite(box,size),*position)
        accessory=self.settings.get('accessory','Bow')
        if accessory=='Bow':
            self.paste_layer(scene,self.icon_sprite((540,303,582,335),(32,23)),96,96)
        elif accessory=='Flowers':
            self.paste_layer(scene,self.icon_sprite((404,300,456,336),(43,24)),88,96)
        elif accessory=='Crystal':
            self.paste_layer(scene,self.crystal_sprite(),101,97)
        buddy=self.settings.get('buddy','Cat')
        if buddy=='Bunny':
            bunny=self.sticker((1454,174,1498,232),
                [(1456,198),(1457,177),(1464,176),(1468,193),(1477,178),
                 (1485,176),(1485,186),(1478,199),(1494,206),(1496,223),
                 (1488,232),(1461,231),(1455,222)],'bunny')
            self.paste_layer(scene,self.resized(bunny,25,33,'wearable-bunny'),8,94)
        elif buddy=='Frog':
            self.paste_layer(scene,self.icon_sprite((476,304,515,334),(30,23)),7,104)
        elif buddy=='Cat':
            self.paste_layer(scene,self.icon_sprite((345,349,385,383),(31,26)),6,101)
        self.oracle_scene=scene
        self.put_sticker(scene,356,120)

    def scene_arrow(self,box,left):
        image=self.crop(box).copy()
        # Match each arrow's backing to the actual chosen background.
        self.paste_layer(image,self.oracle_scene,356-box[0],120-box[1])
        polygon=([(378,175),(375,174),(354,191),(353,196),(376,213),(381,212),(381,177)]
                 if left else [(554,175),(559,176),(578,191),(579,196),(558,214),(552,212),(552,177)])
        arrow=self.sticker(box,polygon,'left-arrow' if left else 'right-arrow')
        self.paste_layer(image,arrow,0,0)
        return image

    def rename(self):
        from tkinter.simpledialog import askstring
        name = askstring('Your little oracle','What is your oracle’s name?', initialvalue=self.settings.get('name','Lumi'), parent=self.root)
        if name and name.strip():
            self.change(name=name.strip()[:24])

    def set_category(self, category):
        from selection_state import choose
        choose(self,'oracle-tabs',category)
        self.category = category
        self.render()

    def legacy_cycle_style(self, step):
        key,choices=ORACLE_OPTIONS[self.category]
        current=self.settings.get(key,choices[0])
        index=choices.index(current) if current in choices else 0
        self.change(**{key:choices[(index+step)%len(choices)]})

    def entry(self, box, variable):
        entry = tk.Entry(self.canvas, textvariable=variable, relief='flat', bg='#faf8ff', fg=INK,
                         insertbackground=INK, font=(self.font_family, -round(11*self.scale)))
        x,y = self.xy(box[0],box[1])
        self.canvas.create_window(x,y,anchor='nw',width=(box[2]-box[0])*self.scale,height=(box[3]-box[1])*self.scale,window=entry)
        self.widgets.append(entry)
        return entry

    def show_intention(self):
        boxes = [(646,114,722,183),(728,114,805,183),(811,114,891,183),
                 (646,189,722,258),(728,189,805,258),(811,189,891,258),
                 (646,264,765,331),(771,264,891,331)]
        for intention, box in zip(INTENTIONS, boxes):
            self.hit(box, intention, lambda v=intention:self.select_intention(v))
            if intention == self.intention:
                self.rect(box,'','#cf68bb')
        self.entry((654,374,883,398),self.question)
        self.hit((680,421,856,460),'Draw three cards',self.begin)

    def select_intention(self, value):
        from selection_state import choose
        choose(self,'intentions',value)
        self.intention=value
        self.render()

    def begin(self):
        if self.screen=='draw':return
        selected=self.settings.get('selection_choices',{}).get('intentions')
        if selected not in INTENTIONS:
            from lumi_reminder import show
            show(self)
            return
        self.intention=selected
        # Back/Next with unchanged inputs resumes this reading rather than
        # silently drawing another set during the demonstration.
        if self.reading and self.reading.get('intention')==self.intention and self.reading.get('question','')==self.question.get().strip()[:500]:
            self.go('revealed' if len(self.chosen)==3 else 'draw')
            return

        self.shuffle_pending=True
        self.reading=draw_reading(self.intention,self.question.get())
        self.reading['interpretation']=overall(self.reading)
        self.reading['selected_intention']=self.settings.get('selection_choices',{}).get('intentions')
        self.note=''
        self.chosen=set()
        self.message='Pick three cards, slowly ♡'
        self.go('draw')

    def new_reading(self):
        from selection_state import fresh
        fresh(self)
        self.reading=None
        self.chosen=set()
        self.note=''
        self.intention='General'
        self.question.set('')
        self.go('oracle')

    def show_draw(self):
        for i,box in enumerate([(938,152,1019,292),(1029,152,1110,292),(1118,152,1201,292)]):
            self.hit(box,['Choose Past','Choose Present','Choose Future'][i],lambda n=i:self.pick(n))
            if i in self.chosen:
                self.rect(box,'','#ffe994')
                self.text((box[0]+box[2])/2,220,'✓',30,70,'center','#fff4a5',True)
        self.text(1075,330,f'{len(self.chosen)} of 3 chosen',10,200,'center','#fff9ff')

    def pick(self, index):
        if self.screen!='draw' or index not in range(3) or index in self.chosen:return
        self.chosen.add(index)
        if len(self.chosen)==3:
            from sound_events import play
            play(self,'save_chime')
        self.render()
        if getattr(self,'magic',None) and index<len(self.card_effects):
            self.magic.burst(self.card_effects[index].box)
        if len(self.chosen)==3 and getattr(self,'magic',None):
            boxes=[effect.box for effect in self.card_effects]
            self.magic.burst((boxes[0][0],boxes[0][1],boxes[-1][2],boxes[-1][3]))
            self.canvas.itemconfigure(self.magic.glow,state='hidden')

    def draw_card(self, card, box):
        name=card['name']
        template = 0 if name in ['The Lovers','The Empress','Strength','Temperance'] else 2 if name in ['The Star','The Sun','The World','The Fool','Judgement'] else 1
        w,h=box[2]-box[0],box[3]-box[1]
        self.art(CARD_ART[template],box[0],box[1],(w,h))
        if name == ['The Lovers','The Moon','The Star'][template]:
            return  # Keep the reference's exact lettering for its three cards.
        self.rect((box[0]+4,box[3]-h*.17,box[2]-4,box[3]-4),'#fff2cd')
        self.text((box[0]+box[2])/2,box[3]-h*.085,name.upper(),max(6,min(9,w/9)),w-9,'center',INK,True)

    def show_revealed(self):
        self.message='Click a card for its meaning, or Lumi’s speech bubble for your full reading.'
        for i,card in enumerate(self.reading['cards']):
            box=[(1248,101,1331,260),(1341,101,1425,260),(1432,101,1515,260)][i]
            self.draw_card(card,box)
            self.hit(box,'Read '+card['name'],lambda n=i:self.open_card(n))
            left=1251+i*89
            self.rect((left,296,left+80,325), '#ead1ff' if card['orientation']=='Upright' else '#bfeaff')
            self.text(left+40,311,card['orientation']+(' ↑' if card['orientation']=='Upright' else ' ↓'),11,79,'center')
        self.hit((1376,350,1511,446),'Read your overall message',lambda:self.go('reading'))
        self.hit((1245,341,1378,470),'Read your overall message',lambda:self.go('reading'))

    def open_card(self, index):
        from selection_state import choose
        choose(self,'meaning-tabs',None)
        self.card_index=index
        self.meaning_tab='Meaning'
        self.go('meaning')

    def _set_meaning_tab(self, tab):
        from selection_state import choose
        choose(self,'meaning-tabs',tab)
        self.meaning_tab = tab
        self.render()

    def _choose_reflect_step(self, step):
        if self.reading is not None:
            self.reading['step'] = step
        self.render()

    def text_panel(self, box, content, size=12, bg=PAPER, padding=3):
        frame=tk.Frame(self.canvas,bg=bg)
        text=tk.Text(frame,wrap='word',relief='flat',bd=0,bg=bg,fg=INK,font=(self.font_family,-round(size*self.scale)),
                     padx=padding,pady=padding,highlightthickness=0,cursor='arrow')
        # Reveal text at the selected speed; the scrollbar retains the full text.
        speed = int(self.settings.get('text_speed', 50))
        def reveal(position=0):
            end = min(len(content), position + 4 + speed // 4)
            text.configure(state='normal')
            text.insert('end', content[position:end])
            text.configure(state='disabled')
            if end < len(content):
                self.typing_timers.append(self.root.after(24, lambda: reveal(end)))
        reveal()
        scroll=tk.Scrollbar(frame,command=text.yview,width=9)
        text.configure(yscrollcommand=scroll.set)
        text.pack(side='left',fill='both',expand=True)
        # Match the picture's clean panels. Mouse-wheel / trackpad scrolling
        # remains available without a permanent native scrollbar.
        x,y=self.xy(box[0],box[1])
        self.canvas.create_window(x,y,anchor='nw',width=(box[2]-box[0])*self.scale,height=(box[3]-box[1])*self.scale,window=frame)
        self.widgets.append(frame)

    def show_meaning(self):
        card=self.reading['cards'][self.card_index]
        self.draw_card(card,(44,566,147,716))
        labels=['Meaning','In This Position','For Your Question','Keywords']
        for i,label in enumerate(labels):
            box=(161,579+i*33,291,608+i*33)
            self.hit(box,label,lambda v=label:self.set_tab(v))
            if label==self.meaning_tab:
                self.rect(box,'','#9884e5')
        self.rect((164,706,247,732),'#b8e8ff')
        self.text(205,719,card['orientation']+(' ↓' if card['orientation']=='Reversed' else ' ↑'),11,82,'center')
        self.hit((161,704,250,734),'Explain card orientation',lambda:self.set_tab('Meaning'))
        value={
            'Meaning':card['orientation']+'\n'+card['meaning']+'\n\nTrust your intuition and take one gentle step.',
            'In This Position':card['position']+'\n\n'+card['context'],
            'For Your Question':(self.reading.get('question') or self.reading['intention'])+'\n\n'+card['meaning']+'\n\n'+card['guidance'],
            'Keywords':'\n'.join('✦ '+word.capitalize() for word in card['keywords']),
        }[self.meaning_tab]
        self.text_panel((46,744,294,831),value,12)
        self.rect((43,833,294,887),PAPER)
        for i,keyword in enumerate(card['keywords'][:6]):
            col,row=i%3,i//3
            left,top=46+col*82,835+row*27
            self.pill((left,top,left+77,top+23),keyword.capitalize())
        self.hit((76,900,211,929),'Back to cards',lambda:self.go('revealed'))

    def pill(self,box,label):
        x1,y1=self.xy(box[0],box[1]); x2,y2=self.xy(box[2],box[3])
        r=6*self.scale
        self.canvas.create_polygon(x1+r,y1,x2-r,y1,x2,y1,x2,y1+r,x2,y2-r,
            x2,y2,x2-r,y2,x1+r,y2,x1,y2,x1,y2-r,x1,y1+r,x1,y1,
            smooth=True,fill='#e6d6ff',outline='')
        self.text((box[0]+box[2])/2,(box[1]+box[3])/2,label,9,box[2]-box[0]-6,'center')

    def set_tab(self,value):
        self.meaning_tab=value
        self.render()

    def show_reading(self):
        # Coordinates follow the original three rows. Only sample text is
        # covered: the original icons, separators and panel borders stay intact.
        self.reading_layout = []
        for card,heading_y,body_y in zip(self.reading['cards'],(610,670,729),(627,687,746)):
            self.rect((398,heading_y-2,636,body_y+29),PAPER)
            label=card['position']+' – '+card['name']+' ('+card['orientation']+')'
            pixels=round(12*self.scale)
            heading_font=tkfont.Font(root=self.root,family=self.font_family,size=-pixels,weight='bold')
            while heading_font.measure(label)>232*self.scale and pixels>round(9*self.scale):
                pixels-=1
                heading_font.configure(size=-pixels)
            heading=self.text(402,heading_y,label,pixels/self.scale,232,bold=True)
            body=self.text(402,body_y,card['meaning'],12,232)
            # Keep longer meanings inside their row without shifting the next
            # heading. Both blocks retain exactly the same left alignment.
            body_pixels=round(12*self.scale)
            while self.canvas.bbox(body)[3]-self.canvas.bbox(body)[1]>29*self.scale and body_pixels>round(9*self.scale):
                body_pixels-=1
                self.canvas.itemconfigure(body,font=(self.font_family,-body_pixels))
            self.reading_layout.append((heading,body,heading_y,body_y))
        # No extra native padding: body text begins at the reference's x=347,
        # directly below its original Overall Message heading.
        self.text_panel((347,813,635,873),overall(self.reading),12,padding=0)
        self.hit((421,885,648,928),'Save this reading to Moon Diary',lambda:self.go('save'))
        self.message='Click Lumi’s message to save this reading ♡'

    def show_save(self):
        for i,card in enumerate(self.reading['cards']):
            self.draw_card(card,(704+i*75,622,772+i*75,723))
        self.rect((712,726,912,748),PAPER)
        self.text(812,737,self.reading['date'][:16].replace('T',' · '),11,202,'center')
        self.note_widget=tk.Text(self.canvas,wrap='word',relief='flat',bd=0,bg='#faf8ff',fg=INK,
                                 insertbackground=INK,font=(self.font_family,-round(11*self.scale)),padx=4,pady=4)
        self.note_widget.insert('1.0',self.note)
        x,y=self.xy(699,762)
        self.canvas.create_window(x,y,anchor='nw',window=self.note_widget,width=200*self.scale,height=44*self.scale)
        self.widgets.append(self.note_widget)
        self.hit((900,766,921,802),'Edit your note',self.focus_note)
        self.hit((701,821,916,860),'Save to Diary',self.save)
        self.hit((701,862,916,899),'Draw again',lambda:self.go('intention'))

    def focus_note(self):
        if self.note_widget is not None:
            self.note_widget.focus_set()
            self.note_widget.mark_set('insert','end-1c')

    def save(self):
        self.capture_note()
        self.store.save(self.reading,self.note)
        self.page=0
        self.message='Saved to your Moon Diary ♡'
        self.go('save')

    def save_reading_only(self):
        if self.reading is not None:
            self.reading['step']=''
            self.save()

    def save_and_show_confirmation(self):
        """Persist once, then show the saved confirmation screen."""
        if not self.reading:
            return
        self.store.save(self.reading, self.note)
        self.go('save')

    def show_diary(self):
        readings=self.store.data['readings']
        self.rect((976,609,1241,902),PAPER)
        if not readings:
            self.text(1105,730,'Your story starts here.\n\nSave your first reading\nto begin your Moon Diary. ♡',13,239,'center')
        for i,reading in enumerate(readings[self.page*4:self.page*4+4]):
            y=613+i*69
            self.rect((977,y,1239,y+65),'#fff7fa','#e1cbea')
            self.draw_card(reading['cards'][0],(988,y+7,1029,y+59))
            self.text(1045,y+8,reading['date'][:10],11,175)
            self.text(1045,y+24,(reading.get('note') or reading['cards'][0]['meaning'])[:42],11,169)
            self.text(1045,y+49,'♡ '+reading['intention'],10,155)
            self.text(1220,y+34,'›',22,17,'center','#9782d6')
            self.hit((978,y,1238,y+65),'Open saved '+reading['intention']+' reading',lambda r=reading:self.load(r))
        pages=max(1,(len(readings)+3)//4)
        self.hit((1054,905,1163,930),'Clear diary',self.clear_diary)
        if pages>1:
            self.text(1009,916,'‹ Back',10,62,'center')
            self.text(1202,916,'Next ›',10,62,'center')
        if self.page>0:
            self.hit((978,905,1044,930),'Previous diary page',lambda:self.diary_page(-1))
        if self.page+1<pages:
            self.hit((1174,905,1238,930),'Next diary page',lambda:self.diary_page(1))

    def diary_page(self,delta):
        self.page+=delta
        self.render()

    def load(self,reading):
        from selection_state import choose
        choose(self,"intentions",reading.get("selected_intention"))
        self.intention=reading.get("intention","General")
        self.question.set(reading.get("question",""))
        self.reading=reading
        self.note=reading.get('note','')
        self.message='Saved reading · '+reading['date'][:10]
        self.go('revealed')

    def toggle(self,key):
        enabled=not self.settings.get(key,False)
        if enabled and self.sound and not self.sound.available:
            messagebox.showinfo('Audio unavailable','No system audio player is available on this computer.',parent=self.root)
            return
        self.store.settings(**{key:enabled})
        if key=='sound' and not enabled and self.sound:
            stop=getattr(self.sound,'stop_effects',None)
            if stop:stop()
        if key=='music' and self.sound:
            self.sound.set_music(enabled)
        self.render()

    def show_settings(self):
        # Clear the example selection; show the actual saved preference.
        self.rect((1436,609,1499,684),PAPER)
        self.art((1440,613,1494,665))
        self.text(1467,674,'Night',11,54,'center')
        for theme,box in [('Day',(1291,609,1356,685)),('Sunset',(1362,609,1427,685)),('Night',(1435,609,1500,685))]:
            self.hit(box,theme+' theme',lambda t=theme:self.open_background(t))
            if self.settings.get('selected_background')==theme:
                self.rect(box,'','#7152c6')
        for key,y in [('music',702),('sound',735)]:
            box=(1451,y,1498,y+24)
            self.rect(box,PAPER)
            on=self.settings.get(key,False)
            x1,y1=self.xy(1453,y+2);x2,y2=self.xy(1496,y+22)
            self.canvas.create_oval(x1,y1,x2,y2,fill='#5082ff' if on else '#c9c3d9',outline='#6963b5',width=self.scale)
            cx=1485 if on else 1464
            x1,y1=self.xy(cx-9,y+3);x2,y2=self.xy(cx+9,y+21)
            self.canvas.create_oval(x1,y1,x2,y2,fill='#fff9ff',outline='')
            self.hit((1293,y-2,1500,y+27),('Disable ' if on else 'Enable ')+key,lambda k=key:self.toggle(k))
        slider=tk.Scale(self.canvas,from_=0,to=100,orient='horizontal',showvalue=False,
                        bg=PAPER,fg=INK,troughcolor='#d5c6ff',highlightthickness=0,bd=0,sliderlength=12,
                        command=self.set_text_speed)
        slider.set(self.settings.get('text_speed',50))
        self.speed_slider=slider
        x,y=self.xy(1333,786)
        self.canvas.create_window(x,y,anchor='nw',window=slider,width=128*self.scale,height=23*self.scale)
        self.widgets.append(slider)
        self.hit((1294,819,1497,848),'About Veil & Vision',self.about)
        self.hit((1294,850,1497,875),'Clear diary',self.clear_diary)
        self.hit((1294,877,1497,905),'Reset progress',self.reset)

    def set_text_speed(self,value):
        value=max(0,min(100,int(float(value))))
        if self.settings.get('text_speed')!=value:
            self.store.settings(text_speed=value)

    def select_background(self, value, open_oracle=False):
        """The wardrobe owns this one choice; Settings is only a shortcut."""
        if value not in ('Day','Sunset','Night'):
            raise ValueError('Choose Day, Sunset or Night.')
        self.store.settings(selected_background=value)
        if open_oracle:
            from selection_state import choose
            self.category='Backgrounds'
            choose(self,'oracle-tabs','Backgrounds')
            self.go('oracle')
        else:
            self.render()

    def open_background(self, value):
        self.select_background(value, open_oracle=True)

    def about(self):
        messagebox.showinfo('Veil & Vision',
            'A little guidance for a brighter you ♡\n\n'
            'Original supplied artwork, with a working Python interface.\n'
            '22 Major Arcana · three unique cards · upright/reversed.\n'
            'Readings are reflection prompts, not fixed predictions.\n\n'
            'The reference provides three illustrated card templates;\n'
            'other cards use these illustrations with their own names and meanings.\n'
            'Music is a locally generated gentle chime loop.\n\n'
            'Tab / Enter: select a painted control. Escape: back.\n'
            'All screens share one fixed presentation window.',parent=self.root)

    def clear_diary(self):
        self._quiet_action=True
        if messagebox.askyesno('Clear Moon Diary','Permanently delete all saved readings?',parent=self.root):
            self.store.data['readings']=[]
            self.store.write()
            self.page=0
            self.message='Moon Diary cleared.'
            from sound_events import play
            play(self,'ui_click')
            self.render()

    def reset(self):
        if messagebox.askyesno('Reset progress','Reset oracle, background, sound and the current unsaved reading? Saved diary entries will stay.',parent=self.root):
            self.store.settings(selected_background=None,hat='Star',buddy='Cat',accessory='Bow',name='Lumi',music=False,sound=False,text_speed=50,selection_choices={})
            if self.sound:
                self.sound.set_music(False)
            self.reading=None
            self.question.set('')
            self.note=''
            self.intention='General'
            self.message='A fresh beginning ♡'
            self.go('intro')


def main():
    root=tk.Tk()
    try:
        app=ReferenceApp(root,Store())
    except (OSError,ValueError,RuntimeError,tk.TclError) as error:
        messagebox.showerror('Cannot open Veil & Vision',str(error),parent=root)
        root.destroy()
        return
    root.mainloop()



if __name__ == '__main__':
    main()
