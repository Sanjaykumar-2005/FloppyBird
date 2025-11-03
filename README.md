# 🕹️ Flappy Bird Championship (Arduino + Python)

This project brings **hardware-controlled Flappy Bird** to life using **Arduino buttons** and **Pygame graphics**.  
Two players compete head-to-head by pressing real physical buttons connected to an Arduino board — or use keyboard keys for testing.

---

## 🚀 Features

- 🎮 **Two-player Flappy Bird** gameplay  
- 🟡 Player 1 (Yellow Bird) → Button 1 / Keyboard `W`  
- 🟠 Player 2 (Orange Bird) → Button 2 / Keyboard `↑`  
- 🔌 **Arduino serial connection** (USB) for real button input  
- ⚙️ Software **debouncing** to avoid false presses  
- 🧱 Dynamic pipes and real-time collision detection  
- 🧠 Auto winner detection & live scoring  
- 💻 Cross-platform (Windows / Linux / Mac)

---

## 🧩 Hardware Setup

| Component | Pin | Description |
|------------|-----|-------------|
| Button 1 (Player 1) | D2 | Yellow bird control |
| Button 2 (Player 2) | D3 | Orange bird control |
| Common Ground | GND | Connect both buttons |

🪛 Use **pull-up configuration**: one side of each button → digital pin, other side → GND.  
No external resistors needed (uses Arduino’s internal pull-ups).

---

## 🖥️ Software Requirements

- **Arduino IDE** (to upload `.ino` sketch)  
- **Python 3.9+**
- Required Python libraries:
  ```bash
  pip install pygame pyserial
