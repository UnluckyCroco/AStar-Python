import tkinter as tk
from colorama import Fore
from math import *

root = tk.Tk()
canvas = tk.Canvas(height=100, width=100, highlightthickness=1, highlightbackground="black")
canvas.grid(row=0, column=2, rowspan=3, padx=10, pady=10)
cell_height = 15
cell_width = 15

def print_3d_array(three_d_array):
    width = len(three_d_array[0])
    print(Fore.RED + "_" * (width * 3 + 3))
    for array in three_d_array:
        print(Fore.RED + "| ", end="")
        for value in array:
            if type(value) == Cell:
                text = str(value.value)
                print(Fore.WHITE + (text if len(text) == 2 else f" {text}"), end=" ")
        print(Fore.RED + "|")
    print(Fore.RED + "-" * (width * 3 + 3))


def subtract_weight(x):
    return x - 1 if x > 1 else x

def add_weight(x):
    return x + 1 if 9 > x > 0 else x

def set_wall(x):
    return -1

def reset_tile(x):
    return 1

def set_start(x):
    return 0

def set_end(x):
    return -2

def get_color(value):
    if value == -1:
        return "black"
    if value == 0:
        return "green"
    if value == -2:
        return "red"
    return "white"

class Point:
    x = 0
    y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y

class Cell:
    value = 1
    text = None
    rectangle = None
    coordinates = None

    def __init__(self, value = 1, text = None, rectangle = None, x = 0, y = 0):
        self.value = value
        self.text = text
        self.rectangle = rectangle
        self.coordinates = Point(x, y)

    def set_value(self, selected_option, x, y):
        match selected_option:
            case "add_weight":
                self.value = self.value + 1 if 9 > self.value > 0 else self.value
            case "subtract_weight":
                self.value = self.value - 1 if self.value > 1 else self.value
            case "set_wall":
                self.value = -1
            case "reset_tile":
                self.value = 1
            case "set_start":
                if not field.find_first(0):
                    self.value = 0
            case "set_end":
                if not field.find_first(-2):
                    self.value = -2
        self.set_text(x, y)
        self.set_color()

    def set_text(self, x, y):
        if self.text:
            if self.value < 2:
                canvas.delete(self.text)
            else:
                canvas.itemconfig(self.text, text=self.value)
        elif self.value > 1:
            self.text = canvas.create_text(x * cell_width + cell_width / 2, y * cell_height + cell_height / 2, text=f"{self.value}")

    def set_color(self):
        canvas.itemconfig(self.rectangle, fill=get_color(self.value))


class Field:
    selected_option = add_weight
    cells = []
    width = 0
    height = 0

    def clicked(self, x, y):
        self.cells[y][x].set_value(self.selected_option.__name__, x, y)

    def find_values(self, value):
        temp_array = []
        for row in self.cells:
            for cell in row:
                if cell.value == value:
                    temp_array.append(cell)

        return temp_array


    def find_first(self, value):
        for row in self.cells:
            for cell in row:
                if cell.value == value:
                    return cell

        return None


field = Field()

def set_function(function):
    field.selected_option = function

def clicked(event):
    x = floor(event.x / cell_width)
    y = floor(event.y / cell_height)
    # print(f"{x} {y}")
    field.clicked(x, y)

def generate_field():
    new_height = height_entry_text.get()
    new_width = width_entry_text.get()
    if not (new_height.isdigit() and new_width.isdigit()):
        return
    height = int(new_height)
    width = int(new_width)
    if not (height > 0 and width > 0):
        return

    field.width = width
    field.height = height

    canvas.config(width=width * cell_width - 1, height=height * cell_height - 1)
    for y in range(0, height):
        y_coord = y * cell_height
        field.cells.append([])
        for x in range(0, width):
            x_coord = x * cell_width
            cell = canvas.create_rectangle(x_coord, y_coord, x_coord + cell_width, y_coord + cell_height,
                                           outline="black")
            field.cells[y].append(Cell(rectangle=cell, x=x, y=y))

class AStar:
    start = None
    end = None


# 1.41421356237 multiplier for diagonal movement (square root of (x squared + x squared))
def start_astar():
    print_3d_array(field.cells)
    # test = list(map(lambda cell_row: list(filter(lambda cell: cell.value == 0, cell_row)), field.cells))
    # test = list(filter(lambda mapped: len(mapped) > 0, map(lambda cell_row: list(filter(lambda cell: cell.value == 0, cell_row)), field.cells)))
    # test = list(filter(lambda mapped: len(mapped) > 0, filter(lambda cell: cell.value == 0, field.cells)))
    # print_3d_array(test)

    start = field.find_first(0)
    end = field.find_first(-2)
    if not (start and end):
        return


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    root.title('A*')

    width_label = tk.Label(root, text="Width:")
    width_entry_text = tk.StringVar()
    width_entry = tk.Entry(root, width=10, textvariable=width_entry_text)

    height_label = tk.Label(root, text="Height:")
    height_entry_text = tk.StringVar()
    height_entry = tk.Entry(root, width=10, textvariable=height_entry_text)

    width_label.grid(row=0, column=0, padx=(10, 0), pady=10)
    height_label.grid(row=1, column=0, padx=(10, 0), pady=10)
    width_entry.grid(row=0, column=1, padx=10, pady=10)
    height_entry.grid(row=1, column=1, padx=10, pady=10)

    generate_button = tk.Button(root, text='Generate', command=generate_field, width=10)

    generate_button.grid(row=2, padx=10, pady=10, columnspan=2)

    add_weight_button = tk.Button(root, text='Add weight', width=10, command=lambda: set_function(add_weight))
    add_weight_button.grid(row=0, column=3, pady=10, padx=10)

    subtract_weight_button = tk.Button(root, text='Subtract weight', width=10, command=lambda: set_function(subtract_weight))
    subtract_weight_button.grid(row=0, column=4, pady=10, padx=10)

    set_wall_button = tk.Button(root, text='Set wall', width=10, command=lambda: set_function(set_wall))
    set_wall_button.grid(row=1, column=3, pady=10, padx=10)

    reset_tile_button = tk.Button(root, text='Reset tile', width=10, command=lambda: set_function(reset_tile))
    reset_tile_button.grid(row=1, column=4, pady=10, padx=10)

    set_start_button = tk.Button(root, text='Set start', width=10, command=lambda: set_function(set_start))
    set_start_button.grid(row=2, column=3, pady=10, padx=10)

    set_end_button = tk.Button(root, text='Set end', width=10, command=lambda: set_function(set_end))
    set_end_button.grid(row=2, column=4, pady=10, padx=10)

    start_button = tk.Button(root, text='Start', width=10, command=start_astar)
    start_button.grid(row=4, column=2, pady=(0, 10), padx=10)

    canvas.bind('<Button>', clicked)

    root.mainloop()
