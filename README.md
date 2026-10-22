# 🌙 Veil & Vision

### A cosy, pastel pixel-art journey of reflection and self-discovery

**Veil & Vision** is an interactive Python desktop application that combines tarot-inspired storytelling, character customisation, and personal reflection in a dreamy pixel-art environment.

Guided by **Lumi**, a friendly companion, users can explore card readings, choose meaningful Little Steps, and record their experiences in a personal Moon Diary.

The project brings together creative interface design, interactive storytelling, and Python programming.

---

## ✨ Features

### 🌙 Meet Lumi — Your Personal Companion
Customise Lumi with different hats, accessories, buddies, and backgrounds. Your selections are saved so Lumi can accompany you throughout your experience.

### 🔮 Interactive Three-Card Reading
Choose and reveal three cards, explore their individual meanings, and receive an overall reading.

### 🌱 Little Steps
Turn a reading into a small, meaningful action through the Little Step feature.

### 📖 Moon Diary
Save readings and reflections locally and revisit previous experiences.

### 🎨 Cosy Pixel-Art Interface
Explore a cohesive pastel-inspired desktop experience with custom artwork and interactive elements.

### ⚙️ Settings & Personalisation
Manage preferences, diary entries, and progress through the settings interface.

---
### 🖼️ Application design

<img width="1055" height="1491" alt="Lumi_poster" src="https://github.com/user-attachments/assets/830a064b-cc57-4e57-9378-730c1995ee6e" />



## 🛠️ Technologies

| Technology | Purpose |
|---|---|
| Python 3.10+ | Application logic |
| Tkinter | Desktop graphical user interface |
| Tkinter Canvas | Artwork display and interface composition |
| JSON | Local data persistence |
| GitHub | Source code hosting and project documentation |

**No API keys or internet services are required.**

---

## 🚀 Installation & Running

### Requirements

- Python 3.10 or newer
- Tkinter
- A compatible desktop environment

The application has been tested on macOS using native Python 3.13 with Tkinter.

### Run with Python

Keep the complete project folder together, including all artwork and asset files.

Open a terminal in the project folder and run:

```bash
python3 main.py
```

### Run on macOS

You can also launch the application using:

`run_veil_vision.command`

Close older Veil & Vision windows before opening an updated version.

**Important:** Do not download or move only `main.py`. The application depends on additional Python modules and artwork assets.

---

## 🗺️ Application Journey

The interactive experience follows this sequence:

Intro → Customize → Intention → Reveal Three Cards → Continue → Your Cards → Card Meaning → Overall Reading → Little Step → Save → Moon Diary → Follow-up → Settings → New Reading

---

## 💾 Local Data & Privacy

Veil & Vision stores readings and preferences locally in:

`data/moon_diary.json`

- Saved diary entries remain available when starting a New Reading.
- Clear Diary requests confirmation before deleting diary entries.
- Reset Progress requests confirmation and preserves diary entries.
- The application does not require an online account or external API.

---

## 🎨 Interface & Character Design

The application uses a consistent **761 × 740** window, shared container, and Canvas across its twelve pages.

Artwork is proportionally fitted to preserve the original compositions. Page 4 retains its fixed night artwork.

### Lumi Customisation

Page 2 features a reconstructed transparent Lumi sprite with separate layers for hats, accessories, buddies, and backgrounds.

- Customisation choices update the preview.
- Selected options persist.
- Choosing None removes the corresponding optional layer.
- The reconstructed sprite approximates the original flattened artwork.
- Original artwork files remain intact, and other pages retain their original Lumi.

---

## 💡 Development Goals

This project was created to explore the connection between programming, creativity, and user experience.

Key development areas include:

- Python application development
- Graphical user interface design
- Event-driven programming
- Interactive navigation and state management
- Local data persistence
- Modular code organisation
- Visual consistency and usability

---

## 🌷 Future Improvements

Potential enhancements include:

- Expanded Lumi animations and customisation
- More interactive reading options
- Improved personalisation
- Additional Moon Diary features
- Accessibility and usability enhancements
- Cross-platform compatibility improvements

---

## 💜 Project Vision

Veil & Vision explores how software can provide a gentle, imaginative space for reflection.

Through interactive storytelling, thoughtful visual design, and a friendly companion, the application aims to make everyday self-reflection more engaging.

*Sometimes, a little reflection is the beginning of something meaningful.*

---

**Made with Python, creativity, and a little moonlight. 🌙**

