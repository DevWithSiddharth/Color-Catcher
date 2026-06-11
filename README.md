# 🎮 Color Catcher



<pre>
<span>  ██████╗ ██████╗ ██╗      ██████╗ ██████╗ ██╗   ██╗██████╗ </span>
<span> ██╔════╝██╔═══██╗██║     ██╔════╝██╔═══██╗██║   ██║██╔══██╗</span>
<span> ██║     ██║   ██║██║     ██║     ██║   ██║██║   ██║█████╔╝</span>
<span> ██║     ██║   ██║██║     ██║     ██║   ██║██║   ██║██╔══██╗</span>
<span> ╚██████╗╚██████╔╝███████╗╚██████╗╚██████╔╝╚██████╔╝██║  ██║</span>
<span>  ╚═════╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝</span>
</pre>

<p align="center">
  A fast-paced neon arcade game built with <b>Pygame</b><br>
  Catch, dodge, survive, and push for high scores ⚡
</p>

---



## ✨ Features

- 🎯 Fast-paced arcade gameplay with increasing difficulty  
- 🧠 Smart input switching (mouse ↔ keyboard auto-detection)  
- 💥 Juice effects: screen shake, flashes, scaling impacts  
- ✨ Particle explosion system for satisfying feedback  
- 🌌 Animated starfield background  
- ❤️ Lives system with clear game over state  
- 📈 Dynamic difficulty scaling  
- 🪟 Resizable window support  

---

## 🎮 How to Play

### 🧺 Objective
Catch:
- 🟢 Good balls  
- 🟡 Gold balls  

Avoid:
- 🔴 Bad balls  

---

### 🎯 Scoring
| Object | Effect |
|--------|--------|
| 🟢 Good ball | +1 point |
| 🟡 Gold ball | +10 points |
| 🔴 Bad ball | -1 life |

---

## 🕹 Controls

The game auto-switches between input modes:

### 🖱 Mouse Mode
Move basket horizontally using your mouse

### ⌨ Keyboard Mode
- ⬅ Move Left → Left Arrow  
- ➡ Move Right → Right Arrow  

> ⚡ Input mode changes automatically based on your last action.

---

## 💀 Game Over

You start with **5 lives**.

When lives reach 0:

- The game stops immediately  
- “GAME OVER” appears on screen  
- Final score is displayed  

### 🔁 Restart Game
Press: R

---

## 🚀 Installation

### 1. Clone this repository:
```bash
git clone https://github.com/DevWithSiddharth/Color-Catcher.git
```





### 2. Install dependencies
```bash
pip install pygame
```
### 3. Run the game
```bash
 python main.py
 ```
---

## 🔥 Gameplay Feel

Color Catcher is built around **fast feedback and escalating intensity**.

Every interaction is designed to feel responsive and satisfying:

- 🟢 Catch good → satisfying bounce + particle burst  
- 🔴 Hit bad → red flash + screen shake + life loss  
- 🟡 Catch gold → high-value burst with stronger visual effects  
- 📈 Survive longer → faster spawn rates and increased pressure  

The game gradually shifts from calm control → chaotic survival, pushing your reflexes and focus.


---


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <b>Made with ❤️ using Pygame</b><br>
  <i>Stay sharp. Catch fast. Survive longer.</i>
</p>
