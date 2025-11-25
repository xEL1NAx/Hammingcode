# Hamming Code Checker & Generator

A modern GUI application built with **CustomTkinter** for generating, checking, and correcting **Hamming codes** (both standard Hamming(7,4) and extended Hamming(8,4)).  
It is fully interactive, with a dynamic bit panel and real-time bit toggling.

---

## Features

- **Check Hamming codes**
  - Supports Hamming(7,4) and Hamming(8,4)
  - Detects single-bit errors and corrects them
  - Detects double-bit errors (not correctable)
  - Real-time highlighting of error bits

- **Generate Hamming codes**
  - Generate 7-bit or 8-bit Hamming code from 4 data bits
  - Extended parity for Hamming(8,4)
  - Displayed dynamically on the bit panel

- **Interactive GUI**
  - Clickable bit buttons for manual bit editing
  - Big and small bit panels with responsive scaling
  - Flexible layout for different window sizes
  - Light/Dark mode toggle
  - Log window for detailed explanation and operations

- **Utility Functions**
  - Copy result to clipboard
  - Export result to `.txt` file

---

## Requirements

- Python 3.9+
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- [pyperclip](https://pypi.org/project/pyperclip/)

Install dependencies via pip:

```bash
pip install customtkinter pyperclip
````

---

## Usage

1. Clone the repository:

```bash
git clone https://github.com/xEL1NAx/Hammingcode/
cd hamming-gui
```

2. Run the application:

```bash
python hamming_gui.py
```

3. Select mode (`Auto-detect`, `Hamming(7,4)`, `Hamming(8,4)`),
   select operation (`Check` or `Generate`),
   enter bits manually or click the bit buttons.

4. Use buttons to:

   * Check/Generate code
   * Copy result to clipboard
   * Export result to a text file

5. Toggle **Dark Mode** using the switch.

---

## How it Works

* **Hamming(7,4):** Standard 7-bit Hamming code with 3 parity bits
* **Hamming(8,4):** Extended code with an extra parity bit to detect double-bit errors
* **Bit Panel:** Interactive buttons allow you to toggle bits directly
* **Automatic correction:** Single-bit errors are corrected automatically and highlighted in red
