# Veil & Vision — submission/demo

## Run

Keep this entire project folder together. Run **main.py** with Python 3.10 or newer and Tkinter:

```sh
python3 main.py
```

On macOS, you can also double-click `run_veil_vision.command`. The tested interpreter is native Python 3.13 with Tkinter. Assets are separate files bundled in this folder; do not submit only the Python entry point. No API key or internet service is used.

Close older Veil & Vision windows before opening an updated copy.

## Demo flow

Intro → Customize → Intention → Reveal three cards → Continue → Your Cards → Card Meaning → Overall Reading → Little Step → Save → Moon Diary → Follow-up → Settings → New Reading.

The client window, shared container and Canvas are 761 × 740 on all twelve pages. Artwork is fitted proportionally, so shorter compositions retain surrounding background space. Page 4 keeps its fixed night artwork.

Readings and preferences are stored locally in `data/moon_diary.json`. New Reading keeps diary entries. Clear Diary and Reset Progress ask for confirmation. Reset Progress preserves diary entries.

## Page 2 reconstructed Lumi layers

Page 2 uses a newly reconstructed transparent Lumi sprite, with separate existing hat, accessory, buddy and background assets. Choices update the preview and persist. None removes that category's layer. This is an approximation of the original flattened character, not a pixel-identical recovery of the hidden head/neck. Original artwork files remain intact; other pages retain their original Lumi.

