#!/user/bin/env python3
__version__ = "1.0.0"

import tkinter as tk     # Tkinter for GUI element injection
from tkinter import ttk  # For other Tkinter widgets
import time
import turtle

DEFAULT_AMOUNT = 5                  # Default amount slider position
DEFAULT_SPEED = 1                   # Default speed slider position
MAX_DISKS = 20                      # The amount slider cap
STICK_WIDTH = 15
STICK_HEIGHT = 200
START_DISK_WIDTH = 150              # Width of the bottom disk
START_DISK_WIDTH_DECREASE = 5       # Width decrease per higher disk
DISK_HEIGHT = 20
DISK_FONT = ("Arial", 10, "normal")
DISK_COLOR = "#DAA06D"
BASE_COLOR = "#FFFFFF"              # The color of the base (platform and sticks)
MIN_INTERVAL = 0.0005               # The minimum interval between moves

Y = -100                            # The y offset of the base from (0 | 0)
COMPACT_VIEW = False                # Compacts the turtle view
CONTROLS_AT_BOTTOM = True           # Put controls at the bottom rather than on the right side


# Draws a rectangle at the specified position
def draw_rectangle(x, y, size_x, size_y, fill_color=""):
    if fill_color:
        turtle.fillcolor(fill_color)
        turtle.begin_fill()
    turtle.goto(x, y)
    turtle.pd()
    for _ in range(2):
        turtle.forward(size_x)  # Length of the rectangle's side
        turtle.right(90)  # Turning right to form corners
        turtle.forward(size_y)  # Width of the rectangle
        turtle.right(90)
    turtle.pu()
    if fill_color:
        turtle.end_fill()


# Draws a disk at the specified stick and height
def draw_disk(stick: int, height: int, name: int, color=DISK_COLOR):
    stick_pos = [-200 + STICK_WIDTH / 2, 0, 200 - STICK_WIDTH / 2][stick]
    draw_rectangle(stick_pos - ((START_DISK_WIDTH - START_DISK_WIDTH_DECREASE * height) / 2),
                   DISK_HEIGHT * (height + 1) + Y, START_DISK_WIDTH - START_DISK_WIDTH_DECREASE * height, DISK_HEIGHT,
                   color)
    turtle.pu()
    turtle.goto(stick_pos, DISK_HEIGHT / 2 - (DISK_FONT[1] - 2) + DISK_HEIGHT * height + Y)
    turtle.write(str(name), font=DISK_FONT, align="center")


# Draws the rest
def draw_sticks_and_base():
    draw_rectangle(-300, 0 + Y, 600, 20, BASE_COLOR)
    draw_rectangle(-200, STICK_HEIGHT + Y, STICK_WIDTH, STICK_HEIGHT, BASE_COLOR)
    draw_rectangle(-STICK_WIDTH / 2, STICK_HEIGHT + Y, STICK_WIDTH, STICK_HEIGHT, BASE_COLOR)
    draw_rectangle(200 - STICK_WIDTH, STICK_HEIGHT + Y, STICK_WIDTH, STICK_HEIGHT, BASE_COLOR)


# Draws the current state of the sticks / towers
def draw_state(start_stick: list, help_stick: list, target_stick: list):
    global iteration
    turtle.clear()
    if algorithm_running:
        print(f"Iteration {iteration + 1} | {get_percent()}% | ", end="")
        run_data_label_text.set(f"{get_percent()}%")
        iteration += 1
    print(f"{start_stick} | {help_stick} | {target_stick}")
    draw_sticks_and_base()

    # Disks
    for i, disk in enumerate(start_stick):
        draw_disk(0, i, current_amount - disk)
    for i, disk in enumerate(help_stick):
        draw_disk(1, i, current_amount - disk)
    for i, disk in enumerate(target_stick):
        draw_disk(2, i, current_amount - disk)

    turtle.update()
    time.sleep(MIN_INTERVAL / current_speed / 0.1)


# Function to determine if the hanoi algorithm has ended
# If it has it will stop and reset everything
def maybe_hanoi_ended():
    global full_start_stick_global, target_stick_global, iteration, algorithm_running
    if full_start_stick_global == target_stick_global:  # Check
        draw_state(start_stick_global, help_stick_global, target_stick_global)
        algorithm_running = False
        iteration = 0
        run_data_label_text.set("")
        run_button.config(state=tk.NORMAL)


# The hanoi algorithm
def hanoi(discs: int, start_stick: list, help_stick: list, target_stick: list):
    if discs > 0:
        hanoi(discs - 1, start_stick, target_stick, help_stick)
        if start_stick:
            target_stick.append(start_stick.pop())

        draw_state(start_stick_global, help_stick_global, target_stick_global)
        hanoi(discs - 1, help_stick, start_stick, target_stick)
    else:
        # This part should be called at the deepest recursion level
        maybe_hanoi_ended()


# Tkinter init
root = turtle.getcanvas()
inner_frame = tk.Frame(root)
if CONTROLS_AT_BOTTOM:
    inner_frame.grid(column=0, row=1, sticky="w")
else:
    inner_frame.grid(column=1, row=0, sticky="n")

# Turtle init
turtle.tracer(0, 0)
turtle.ht()
turtle.speed(0)
screen = turtle.Screen()
if COMPACT_VIEW:
    screen.setup(700, 350)

# Amount option display init
current_amount: int = DEFAULT_AMOUNT
amount_label_text = tk.StringVar(value=f"Disks: {current_amount}")
amount_label = tk.Label(inner_frame, textvariable=amount_label_text)
amount_label.grid(column=0, row=0)


# Amount slider callback
def on_amount_changed(val):
    global amount_label_text, current_amount, start_stick_global, full_start_stick_global, help_stick_global
    global target_stick_global
    if not algorithm_running:
        current_amount = round(float(val))
    amount_label_text.set(f"Disks: {current_amount}")


# Amount slider init
amount_slider = ttk.Scale(inner_frame, from_=0, to=MAX_DISKS, value=DEFAULT_AMOUNT, orient='horizontal',
                          command=on_amount_changed)
amount_slider.grid(column=1 if CONTROLS_AT_BOTTOM else 0, row=0 if CONTROLS_AT_BOTTOM else 1)

# Speed option display init
current_speed: float = DEFAULT_SPEED
speed_label_text = tk.StringVar(value=f"Speed: {current_speed}")
speed_label = tk.Label(inner_frame, textvariable=speed_label_text)
speed_label.grid(column=2 if CONTROLS_AT_BOTTOM else 0, row=0 if CONTROLS_AT_BOTTOM else 2)


# Speed slider callback
def on_speed_changed(val):
    global speed_label_text, current_speed
    current_speed = round(float(val) * 100) / 100
    speed_label_text.set(f"Speed: {current_speed}")


# Speed slider init
speed_slider = ttk.Scale(inner_frame, from_=0.01, to=1, value=DEFAULT_SPEED, orient='horizontal',
                         command=on_speed_changed)
speed_slider.grid(column=3 if CONTROLS_AT_BOTTOM else 0, row=0 if CONTROLS_AT_BOTTOM else 3)


# Run button callback
def run_algorithm():
    global current_amount, start_stick_global, full_start_stick_global, help_stick_global, target_stick_global
    global algorithm_running

    if not algorithm_running:
        start_stick_global = [i for i in range(current_amount)]
        full_start_stick_global = [i for i in start_stick_global]
        help_stick_global = []
        target_stick_global = []
        run_button.config(state="disabled")
        draw_state(start_stick_global, help_stick_global, target_stick_global)
        algorithm_running = True
        hanoi(len(start_stick_global), start_stick_global, help_stick_global, target_stick_global)


# Run button init
run_button = tk.Button(inner_frame, text="run", command=run_algorithm)
run_button.grid(column=5 if CONTROLS_AT_BOTTOM else 0, row=0 if CONTROLS_AT_BOTTOM else 5)

# Interation Data
run_data_label_text = tk.StringVar()
run_data_label = tk.Label(inner_frame, textvariable=run_data_label_text)
run_data_label.grid(column=7 if CONTROLS_AT_BOTTOM else 0, row=0 if CONTROLS_AT_BOTTOM else 7)

# Other variable inits
algorithm_running = False
iteration = 0
total_console_log_size = 0


# Function to determine the percent of solving the puzzle
def get_percent() -> int:
    global full_start_stick_global
    total = 2 ** len(full_start_stick_global) - 1
    if total != 0:
        return round(iteration / total * 1000) / 10
    else:
        return 0


# Stick setup
start_stick_global = []
full_start_stick_global = []
help_stick_global = []
target_stick_global = []

if __name__ == "__main__":
    # Final turtle init
    turtle.clear()
    turtle.mainloop()
