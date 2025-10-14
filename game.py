import tkinter as tk
import time

# ---------- Configuration ----------
CELL = 48
ROWS, COLS = 8, 8
SEED_MOVE_STEPS = 20
DROP_SPEED = 0.18
BETWEEN_DROPS = 0.35
GROW_STAGE_SECONDS = 2
GROW_HOLD_SECONDS = 5
FLASH_CYCLES = 12
FLASH_DELAY = 0.08
SCROLL_DELAY = 0.22

# ---------- Colors ----------
COLORS = {
    "B": "#000000",   # background
    "G": "#00C000",   # leaves (green)
    "BR": "#8B4513",  # trunk/soil (brown)
    "BL": "#0077FF",  # water
    "Y": "#FFD700",   # seed (gold)
    "W": "#FFFFFF",   # pot (white)
    "S": "#FF33AA",   # celebration color 1
    "T": "#33FFFF",   # celebration color 2
}

# ---------- Small 3x5 font ----------
FONT_3x5 = {
    "A": ["010", "101", "111", "101", "101"],
    "B": ["110", "101", "110", "101", "110"],
    "C": ["011", "100", "100", "100", "011"],
    "E": ["111", "100", "111", "100", "111"],
    "H": ["101", "101", "111", "101", "101"],
    "K": ["101", "110", "100", "110", "101"],
    "N": ["101", "111", "111", "101", "101"],
    "O": ["010", "101", "101", "101", "010"],
    "R": ["110", "101", "110", "101", "101"],
    "S": ["011", "100", "010", "001", "110"],
    "T": ["111", "010", "010", "010", "010"],
    "U": ["101", "101", "101", "101", "111"],
    "W": ["101", "101", "101", "111", "101"],
    "Y": ["101", "101", "010", "010", "010"],
    " ": ["000", "000", "000", "000", "000"],
}

# ---------- Simulator ----------
class SenseSim:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Automatic Planting Simulation 🌱")
        w = COLS * CELL
        h = ROWS * CELL
        self.canvas = tk.Canvas(self.root, width=w, height=h, bg=COLORS["B"], highlightthickness=0)
        self.canvas.pack()
        self.rects = [[None for _ in range(COLS)] for _ in range(ROWS)]
        for r in range(ROWS):
            for c in range(COLS):
                x1, y1 = c * CELL, r * CELL
                self.rects[r][c] = self.canvas.create_rectangle(x1, y1, x1 + CELL, y1 + CELL,
                                                                outline="#111111", fill=COLORS["B"])
        self.root.update()

    def set_pixel(self, r, c, color_code):
        if 0 <= r < ROWS and 0 <= c < COLS:
            self.canvas.itemconfig(self.rects[r][c], fill=COLORS[color_code])

    def clear(self):
        for r in range(ROWS):
            for c in range(COLS):
                self.set_pixel(r, c, "B")
        self.root.update()

    def update(self):
        self.root.update()

    def delay(self, sec):
        end = time.time() + sec
        while time.time() < end:
            self.root.update()
            time.sleep(0.01)

# ---------- Drawing helpers ----------
def draw_soil(sim, seed_col=None):
    for r in range(ROWS):
        for c in range(COLS):
            if r == 7:
                sim.set_pixel(r, c, "BR")
            else:
                sim.set_pixel(r, c, "B")
    if seed_col is not None:
        sim.set_pixel(6, seed_col, "Y")
    sim.update()

def draw_pot(sim, pot_col):
    sim.set_pixel(0, pot_col, "W")
    sim.set_pixel(0, pot_col + 1, "W")

def draw_drop(sim, drop_col, y):
    sim.set_pixel(y, drop_col, "BL")

# ---------- Tree growth ----------
def grow_tree(sim, seed_col):
    for stage in range(1, 4):
        draw_soil(sim, seed_col=None)
        # trunk
        if stage >= 1:
            sim.set_pixel(6, seed_col, "BR")
        if stage >= 2:
            sim.set_pixel(5, seed_col, "BR")
        if stage >= 3:
            sim.set_pixel(4, seed_col, "BR")
            # T-shape leaves
            for dx in (-1,0,1):
                c = seed_col + dx
                if 0 <= c < COLS:
                    sim.set_pixel(3, c, "G")
            # extra leaf on top to look like tree
            sim.set_pixel(2, seed_col, "G")
        sim.update()
        sim.delay(GROW_STAGE_SECONDS)
    sim.delay(GROW_HOLD_SECONDS)

# ---------- Jig-jag flash ----------
def jig_jag_flash(sim):
    for i in range(12):
        color = "S" if i % 2 == 0 else "T"
        for r in range(ROWS):
            for c in range(COLS):
                sim.set_pixel(r,c,color)
        sim.update()
        sim.delay(0.08)
    sim.clear()

# ---------- Scrolling message ----------
def draw_char_3x5(sim, ch, color, x_offset):
    pattern = FONT_3x5.get(ch, FONT_3x5[" "])
    for r,row in enumerate(pattern):
        for c,bit in enumerate(row):
            if bit=="1":
                col = x_offset+c
                row_pos = 1+r
                if 0<=col<COLS and 0<=row_pos<ROWS:
                    sim.set_pixel(row_pos,col,color)

def scroll_message(sim,message,color):
    msg = "   " + message.upper() + "   "
    total_width = len(msg)*3
    for offset in range(total_width-COLS+1):
        sim.clear()
        for c in range(COLS):
            sim.set_pixel(7,c,"BR")
        for i,ch in enumerate(msg):
            draw_char_3x5(sim,ch,color,i*3 - offset)
        sim.update()
        sim.delay(0.22)

# ---------- Simulation ----------
def simulate(sim):
    seed_col = 2
    seed_dir = 1
    pot_col = 1
    seed_moving = True
    hit_position = None

    draw_soil(sim, seed_col)
    draw_pot(sim, pot_col)
    sim.delay(0.6)

    # Move seed
    for _ in range(SEED_MOVE_STEPS):
        if seed_moving:
            seed_col += seed_dir
            if seed_col <= 1 or seed_col >= 6:
                seed_dir *= -1
        draw_soil(sim, seed_col)
        draw_pot(sim, pot_col)
        sim.update()
        sim.delay(0.16)

    # Auto-align pot above seed
    pot_col = max(0,min(seed_col-1,6))
    drop_col = pot_col+1

    # Drop 3 droplets; seed stays yellow, hit recorded but seed doesn't change
    hits = 0
    for drop_idx in range(3):
        for y in range(1,7):
            draw_soil(sim, seed_col)
            draw_pot(sim, pot_col)
            draw_drop(sim, drop_col, y)
            sim.update()
            sim.delay(DROP_SPEED)
            if y==6 and drop_col==seed_col:
                if hit_position is None:
                    hit_position = seed_col
                hits += 1
        sim.delay(BETWEEN_DROPS)

    # Grow tree if hit
    if hit_position is not None:
        grow_tree(sim, hit_position)
        jig_jag_flash(sim)
        scroll_message(sim,"THANK YOU","G")
    else:
        scroll_message(sim,"WASTED","BL")

    # Retry button
    button = tk.Button(sim.root,text="RETRY",font=("Helvetica",14,"bold"),
                       command=lambda: restart(sim))
    button.pack(pady=10)
    sim.root.mainloop()

def restart(sim):
    for widget in sim.root.winfo_children():
        if isinstance(widget, tk.Button):
            widget.destroy()
    simulate(sim)

if __name__=="__main__":
    sim = SenseSim()
    simulate(sim)
