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

    def __eq__(self, other):
        if not isinstance(other, Point):
            return NotImplemented

        return self.x == other.x and self.y == other.y

    def __str__(self):
        return f"({self.x}, {self.y})"


class Cell:
    value = 1
    text = None
    rectangle = None
    cords = None

    def __init__(self, value=1, text=None, rectangle=None, x=0, y=0):
        self.value = value
        self.text = text
        self.rectangle = rectangle
        self.cords = Point(x, y)

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
            self.text = canvas.create_text(x * cell_width + cell_width / 2, y * cell_height + cell_height / 2,
                                           text=f"{self.value}")

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


class AStarQueueItem:
    def __init__(self, cords: Point, total_cost: float, prev_cords: Point or None, end_cords: Point):
        self.cords = cords
        self.total_cost = total_cost
        self.heuristic = sqrt(abs(cords.x - end_cords.x)**2 + abs(cords.y - end_cords.y)**2) + total_cost
        self.prev_cords = prev_cords


class AStarQueue:
    queue = []
    path = []

    def __init__(self, start: Point, end: Point):
        self.start = start
        self.end = end
        self.queue.append(AStarQueueItem(start, 0, None, end))

    def find_cords_in_path(self, cords: Point):
        return list(filter(lambda item: item.cords == cords, self.path))

    def insert_item(self, new_item: AStarQueueItem):
        print()
        for i, item in enumerate(self.queue):
            if new_item.heuristic < item.heuristic:
                self.queue.insert(i, new_item)
                return
        self.queue.append(new_item)


def astar_loop(astar):
    width = len(field.cells[0])
    height = len(field.cells)

    while len(astar.queue):
        head: AStarQueueItem = astar.queue[0]

        print(f"({astar.end.x}, {astar.end.y})")
        if head.cords == astar.end:
            astar.path.append(head)
            return astar

        print(f"({head.cords.x}, {head.cords.y})")
        print()

        for y in range(-1, 2):
            for x in range(-1, 2):
                curr_cords: Point = head.cords
                new_cords = Point(curr_cords.x + x, curr_cords.y + y)

                # out of bounds check
                if new_cords.x > width - 1 or new_cords.x < 0 or new_cords.y > height - 1 or new_cords.y < 0:
                    continue

                # previous coordinates are skipped
                if curr_cords == head.prev_cords:
                    continue

                curr_cell: Cell = field.cells[curr_cords.y + y][curr_cords.x + x]

                # wall
                if curr_cell.value == -1:
                    continue

                # diagonal movement will take the pythagorean formula of the value of the tile itself + the lowest
                # neighbor so: maybe average might be better?
                # ______
                # | 42 |
                # | x3 |
                # ------
                # movement to 2 from x costs root(min(3, 4)**2 + 2**2) = root(13) = 3.6~
                if abs(y) + abs(x) == 2:
                    vert_value = field.cells[curr_cords.y + y][curr_cords.x].value
                    hori_value = field.cells[curr_cords.y][curr_cords.x + x].value

                    # diagonal is wall -> skip
                    if vert_value == -1 or hori_value == -1:
                        continue

                    vert_value = vert_value if vert_value > 0 else 1
                    hori_value = hori_value if hori_value > 0 else 1
                    adj_value = curr_cell.value if curr_cell.value > 0 else 1
                    new_cost = sqrt(min(vert_value, hori_value)**2 + adj_value**2)
                else:
                    new_cost = curr_cell.value if curr_cell.value > 0 else 1

                new_item = AStarQueueItem(new_cords, head.total_cost + new_cost, head.cords, astar.end)
                old_items = astar.find_cords_in_path(new_cords)

                # check if old item in path total cost is higher than the new total cost
                if old_items:
                    for old_item in old_items:
                        if new_item.heuristic > old_item.heuristic:
                            break
                        astar.insert_item(new_item)
                else:
                    astar.insert_item(new_item)

        astar.path.append(head)
        astar.queue.remove(head)

    # no solution
    return False


def find_first(needle, array):
    if not needle:
        return None
    for item in array:
        if needle == item.cords:
            return item


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
    astar = AStarQueue(Point(start.cords.x, start.cords.y), Point(end.cords.x, end.cords.y))

    solution = astar_loop(astar)
    # for item in solution.path:
    #     item.cords
    if not type(solution) == AStarQueue:
        return False
    solution = list(reversed(solution.path))
    pathing = solution[0]
    path = [solution[0]]

    print("Soltuon:")
    print(f"({pathing.cords.x}, {pathing.cords.y})")

    while pathing:
        pathing = find_first(pathing.prev_cords, solution)
        if pathing:
            print(f"({pathing.cords.x}, {pathing.cords.y})")
            path.append(pathing)


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

    subtract_weight_button = tk.Button(root, text='Subtract weight', width=10,
                                       command=lambda: set_function(subtract_weight))
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
