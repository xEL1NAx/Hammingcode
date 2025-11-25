import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import pyperclip
import time

# ------------------- Hamming Logic -------------------

def compute_parities_7(code7):
    p1 = code7[0] ^ code7[2] ^ code7[4] ^ code7[6]
    p2 = code7[1] ^ code7[2] ^ code7[5] ^ code7[6]
    p4 = code7[3] ^ code7[4] ^ code7[5] ^ code7[6]
    return p1, p2, p4

def check_hamming7(bits):
    if len(bits) != 7:
        raise ValueError("Requires exactly 7 bits.")

    p1, p2, p4 = compute_parities_7(bits)
    syndrome = (p4 << 2) | (p2 << 1) | p1
    res = {"syndrome": syndrome}

    if syndrome == 0:
        res.update({"status": "correct", "msg": "Code is correct.", "corrected": bits.copy(), "error_index": None})
    else:
        idx = syndrome - 1
        corrected = bits.copy()
        corrected[idx] ^= 1
        res.update({"status": "corrected", "msg": f"Corrected error in bit position {idx+1}.",
                    "corrected": corrected, "error_index": idx})
    return res

def check_hamming8(bits8):
    if len(bits8) != 8:
        raise ValueError("Requires exactly 8 bits.")

    b7 = bits8[:7]
    p_overall = bits8[7]
    p1, p2, p4 = compute_parities_7(b7)

    syndrome = (p4 << 2) | (p2 << 1) | p1
    overall = 0
    for b in bits8:
        overall ^= b

    res = {"syndrome": syndrome, "overall": overall}

    if syndrome == 0 and overall == 0:
        res.update({"status": "correct", "msg": "Code is correct.", "corrected": bits8.copy(), "error_index": None})

    elif syndrome != 0 and overall == 1:
        idx = syndrome - 1
        corrected = bits8.copy()
        corrected[idx] ^= 1
        res.update({"status": "corrected", "msg": f"Corrected error in bit position {idx+1}.",
                    "corrected": corrected, "error_index": idx})

    elif syndrome == 0 and overall == 1:
        corrected = bits8.copy()
        corrected[7] ^= 1
        res.update({"status": "corrected", "msg": "Corrected error in overall parity (bit 8).",
                    "corrected": corrected, "error_index": 7})

    else:
        res.update({"status": "double_error", "msg": "Double error detected — not correctable.",
                    "corrected": bits8.copy(), "error_index": None})

    return res

def generate_from_data(data4, extended=False):
    if len(data4) != 4:
        raise ValueError("Requires exactly 4 data bits.")

    code7 = [0] * 7
    code7[2] = data4[0]
    code7[4] = data4[1]
    code7[5] = data4[2]
    code7[6] = data4[3]

    p1, p2, p4 = compute_parities_7(code7)
    code7[0] = p1
    code7[1] = p2
    code7[3] = p4

    if not extended:
        return code7

    overall = 0
    for b in code7:
        overall ^= b
    return code7 + [overall]

# ------------------- GUI -------------------

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class HammingApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Hamming Code Checker & Generator")
        self.geometry("900x600")
        self.minsize(900, 600)

        # configure scaling/flexibility
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        self.mode_var = ctk.StringVar(value="Auto-detect")
        self.operation_var = ctk.StringVar(value="Check")
        self.input_var = tk.StringVar(value="")
        self.current_bits = []
        self.bit_buttons = []
        self.parity_positions = set()
        self.last_error_index = None

        self._build_left()
        self._build_right()
        self.update_bits_display()

    # ---------------- LEFT SIDE UI ----------------

    def _build_left(self):
        frame = ctk.CTkFrame(self)
        frame.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame, text="Mode", font=("Arial", 15, "bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkOptionMenu(frame, variable=self.mode_var,
                          values=["Auto-detect", "Hamming(7,4)", "Hamming(8,4)"],
                          command=lambda *_: self.update_bits_display())\
            .grid(row=1, column=0, sticky="ew", pady=5)

        ctk.CTkLabel(frame, text="Operation", font=("Arial", 15, "bold")).grid(row=2, column=0, sticky="w", pady=(15, 0))
        ctk.CTkSegmentedButton(frame, values=["Check", "Generate"],
                               variable=self.operation_var,
                               command=lambda *_: self.update_bits_display())\
            .grid(row=3, column=0, sticky="ew", pady=5)

        ctk.CTkLabel(frame, text="Input (click or type bits):").grid(row=4, column=0, sticky="w", pady=(15, 0))
        inp = ctk.CTkEntry(frame, textvariable=self.input_var)
        inp.grid(row=5, column=0, sticky="ew", pady=5)
        inp.bind("<KeyRelease>", lambda *_: self.on_text_change())

        self.bits_frame = ctk.CTkFrame(frame)
        self.bits_frame.grid(row=6, column=0, sticky="ew", pady=15)

        # buttons area
        btn_area = ctk.CTkFrame(frame)
        btn_area.grid(row=7, column=0, sticky="ew", pady=10)

        ctk.CTkButton(btn_area, text="Check / Generate",
                      command=self.on_check_generate).pack(fill="x", pady=3)
        ctk.CTkButton(btn_area, text="Copy Result",
                      command=self.copy_result).pack(fill="x", pady=3)
        ctk.CTkButton(btn_area, text="Export Result",
                      command=self.export_result).pack(fill="x", pady=3)

        self.theme_switch = ctk.CTkSwitch(frame, text="Dark Mode",
                                          command=self.toggle_theme)
        self.theme_switch.grid(row=8, column=0, sticky="w", pady=10)

    # ---------------- RIGHT SIDE UI ----------------

    def _build_right(self):
        frame = ctk.CTkFrame(self)
        frame.grid(row=0, column=1, sticky="nsew", padx=12, pady=12)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(frame, text="Bit Panel",
                     font=("Arial", 15, "bold")).grid(row=0, column=0, sticky="w")

        self.big_bits_frame = ctk.CTkFrame(frame)
        self.big_bits_frame.grid(row=1, column=0, sticky="ew", pady=10)
        self.big_bits_frame.grid_columnconfigure((0,1,2,3,4,5,6,7), weight=1)

        ctk.CTkLabel(frame, text="Explanation / Log",
                     font=("Arial", 15, "bold")).grid(row=2, column=0, sticky="w")

        self.log_box = ctk.CTkTextbox(frame)
        self.log_box.grid(row=3, column=0, sticky="nsew", pady=5)
        self.log_box.configure(state="disabled")

    # ---------------- BIT PANEL & LOGIC ----------------

    def on_text_change(self):
        text = ''.join(c for c in self.input_var.get() if c in "01")
        self.input_var.set(text)
        self.update_bits_display()

    def update_bits_display(self):
        for w in self.bits_frame.winfo_children():
            w.destroy()
        for w in self.big_bits_frame.winfo_children():
            w.destroy()

        op = self.operation_var.get()
        mode = self.mode_var.get()
        text = self.input_var.get()

        # determine display length
        if op == "Generate":
            display_len = 8 if mode == "Hamming(8,4)" else 7
        else:
            if mode == "Hamming(7,4)":
                display_len = 7
            elif mode == "Hamming(8,4)":
                display_len = 8
            else:
                if len(text) >= 8:
                    display_len = 8
                else:
                    display_len = 7

        # parse bit array
        bits = [0] * display_len
        for i in range(min(len(text), display_len)):
            bits[i] = int(text[i])

        self.current_bits = bits
        self.parity_positions = {0,1,3}
        if display_len == 8:
            self.parity_positions.add(7)

        self.bit_buttons = []

        # ---------------- SMALL BIT BUTTONS ----------------
        small_frame = ctk.CTkFrame(self.bits_frame)
        small_frame.pack(fill="x")

        for i in range(display_len):
            btn = ctk.CTkButton(
                small_frame,
                text=str(bits[i]),
                width=40,
                height=30,
                command=lambda i=i: self.toggle_bit(i)
            )
            btn.grid(row=0, column=i, padx=3)
            self.bit_buttons.append(btn)

        # ---------------- BIG BIT BUTTONS (scaling fix: wrap rows) ----------------
        cols = min(display_len, 4)
        for i in range(cols):
            self.big_bits_frame.grid_columnconfigure(i, weight=1)

        for i in range(display_len):
            row = i // 4
            col = i % 4
            btn = ctk.CTkButton(
                self.big_bits_frame,
                text=f"Bit {i+1}\n{bits[i]}",
                height=70,
                command=lambda i=i: self.toggle_bit(i)
            )
            btn.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
            self.bit_buttons.append(btn)

    def toggle_bit(self, idx):
        self.current_bits[idx] ^= 1
        new = self.current_bits[idx]

        self.input_var.set(''.join(str(x) for x in self.current_bits))
        self.update_bits_display()

    def on_check_generate(self):
        op = self.operation_var.get()
        mode = self.mode_var.get()
        text = self.input_var.get()

        if op == "Generate":
            if len(text) != 4:
                messagebox.showerror("Input Error", "Enter exactly 4 data bits.")
                return
            data = [int(c) for c in text]
            full = generate_from_data(data, extended=(mode == "Hamming(8,4)"))
            self.input_var.set(''.join(str(x) for x in full))
            self.log("Generated code: " + ''.join(str(x) for x in full))
            self.update_bits_display()
            return

        if mode == "Auto-detect":
            m = "Hamming(8,4)" if len(text) >= 8 else "Hamming(7,4)"
        else:
            m = mode

        bits = [int(x) for x in text]
        if m == "Hamming(7,4)":
            res = check_hamming7(bits[:7])
        else:
            res = check_hamming8(bits[:8])

        self.log(res["msg"])
        corrected = ''.join(str(x) for x in res["corrected"])
        self.input_var.set(corrected)
        self.update_bits_display()

        if res["error_index"] is not None:
            self.highlight_error(res["error_index"])

    def highlight_error(self, idx):
        b1 = self.bit_buttons[idx]
        b2 = self.bit_buttons[idx + len(self.current_bits)]

        b1.configure(fg_color="red")
        b2.configure(fg_color="red")

    # ---------------- COPY / EXPORT / THEME ----------------

    def copy_result(self):
        pyperclip.copy(self.input_var.get())
        self.log("Copied to clipboard.")

    def export_result(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if not path:
            return
        with open(path, "w") as f:
            f.write(self.input_var.get())
        self.log(f"Saved to {path}")

    def toggle_theme(self):
        if self.theme_switch.get() == 1:
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")

    # ---------------- LOG ----------------

    def log(self, text):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", text + "\n")
        self.log_box.configure(state="disabled")
        self.log_box.see("end")

if __name__ == "__main__":
    HammingApp().mainloop()
